from flask import Flask, render_template, request, jsonify
import heapq
import math
import time
import tracemalloc
import requests

app = Flask(__name__)

# 1. 초고밀도 확장 노드 좌표 데이터 (총 53개 거점)
LOCATION_COORDS = {
    # Northern Urban & Coastal
    '제주공항': (33.5066, 126.4928),
    '제주시청': (33.4996, 126.5299),
    '오현중학교': (33.5042, 126.5567),
    '삼양해수욕장': (33.5262, 126.5862),
    '조천읍사무소': (33.5350, 126.6340),
    '함덕해수욕장': (33.5434, 126.6692),
    '김녕해수욕장': (33.5571, 126.7423),
    '세화해수욕장': (33.5250, 126.8520),
    '구좌읍사무소': (33.5255, 126.8530),

    # Eastern Mid-Mountain (동부 중산간)
    '봉개교차로': (33.4862, 126.5921),
    '아라동(아라초)': (33.4750, 126.5450),
    '제주돌문화공원': (33.4336, 126.6705),
    '교래사거리': (33.4248, 126.6894),
    '선흘리': (33.5011, 126.7111),
    '덕천리': (33.4922, 126.7651),
    '송당리사거리': (33.4678, 126.8091),
    '수산2리교차로': (33.4152, 126.8651),
    '가시리': (33.3850, 126.7820),
    '성읍민속마을': (33.3871, 126.7981),
    '신풍리': (33.3481, 126.8480),

    # Eastern & Southern Coastal
    '성산일출봉': (33.4581, 126.9422),
    '표선해수욕장': (33.3251, 126.8423),
    '남원포구': (33.2792, 126.7197),
    '위미리': (33.2730, 126.6580),
    '효돈동': (33.2610, 126.6080),

    # Seogwipo Urban
    '동문로터리': (33.2514, 126.5678),
    '중앙로터리': (33.2539, 126.5596),
    '서귀포버스터미널': (33.2491, 126.5093),
    '강정마을': (33.2380, 126.4780),
    '중문관광단지': (33.2483, 126.4124),

    # Hallasan Mountain & Sanrok Roads
    '관음사입구': (33.4235, 126.5458),
    '성판악': (33.3845, 126.6169),
    '한라산국립공원': (33.3617, 126.5348),
    '1100고지': (33.3617, 126.4622),
    '서귀포치유의숲': (33.3050, 126.5180),

    # Western Mid-Mountain (서부 중산간)
    '외도동': (33.4930, 126.4320),
    '하귀리': (33.4810, 126.4020),
    '애월읍사무소': (33.4623, 126.3267),
    '유수암리': (33.4250, 126.3880),
    '소길리': (33.4110, 126.3750),
    '새별오름': (33.3622, 126.3584),
    '광령리': (33.4520, 126.4480),
    '금악리교차로': (33.3551, 126.2915),
    '저지오름삼거리': (33.3320, 126.2575),
    '오설록': (33.3061, 126.2895),
    '덕수리': (33.2720, 126.2980),
    '산방산교차로': (33.2415, 126.3120),
    '안덕계곡': (33.2548, 126.3475),

    # Western Coastal
    '한림공원': (33.3900, 126.2394),
    '협재해수욕장': (33.3938, 126.2397),
    '신창풍차해안': (33.3420, 126.1780),
    '고산리': (33.3080, 126.1680),
    '모슬포항': (33.2173, 126.2514)
}

# 2. 간선 데이터 (총 88개 간선)
RAW_EDGES = [
    # [1] 북부 해안 & 도심 일주망
    ('제주공항', '제주시청'), ('제주시청', '오현중학교'), ('오현중학교', '삼양해수욕장'),
    ('삼양해수욕장', '조천읍사무소'), ('조천읍사무소', '함덕해수욕장'), ('함덕해수욕장', '김녕해수욕장'),
    ('김녕해수욕장', '세화해수욕장'), ('세화해수욕장', '구좌읍사무소'), ('구좌읍사무소', '성산일출봉'),

    # [2] 서부 해안 일주망
    ('제주공항', '외도동'), ('외도동', '하귀리'), ('하귀리', '애월읍사무소'),
    ('애월읍사무소', '한림공원'), ('한림공원', '협재해수욕장'), ('협재해수욕장', '신창풍차해안'),
    ('신창풍차해안', '고산리'), ('고산리', '모슬포항'),

    # [3] 남부 & 동부 해안 일주망
    ('성산일출봉', '표선해수욕장'), ('표선해수욕장', '신풍리'), ('신풍리', '남원포구'),
    ('남원포구', '위미리'), ('위미리', '효돈동'), ('효돈동', '동문로터리'),
    ('동문로터리', '중앙로터리'), ('중앙로터리', '서귀포버스터미널'), ('서귀포버스터미널', '강정마을'),
    ('강정마을', '중문관광단지'), ('중문관광단지', '안덕계곡'), ('안덕계곡', '산방산교차로'),
    ('산방산교차로', '모슬포항'),

    # [4] 동부 중산간 촘촘한 세부 네트워크
    ('제주시청', '아라동(아라초)'), ('제주시청', '봉개교차로'), ('오현중학교', '봉개교차로'),
    ('봉개교차로', '선흘리'), ('선흘리', '함덕해수욕장'), ('선흘리', '덕천리'),
    ('덕천리', '김녕해수욕장'), ('덕천리', '송당리사거리'), ('봉개교차로', '제주돌문화공원'),
    ('제주돌문화공원', '교래사거리'), ('교래사거리', '송당리사거리'), ('송당리사거리', '구좌읍사무소'),
    ('송당리사거리', '수산2리교차로'), ('수산2리교차로', '성산일출봉'), ('교래사거리', '가시리'),
    ('가시리', '성읍민속마을'), ('성읍민속마을', '표선해수욕장'), ('성읍민속마을', '수산2리교차로'),
    ('가시리', '신풍리'), ('교래사거리', '남원포구'), ('제주돌문화공원', '표선해수욕장'),

    # [5] 서부 중산간 촘촘한 세부 네트워크
    ('제주공항', '광령리'), ('광령리', '유수암리'), ('유수암리', '소길리'), ('소길리', '새별오름'),
    ('외도동', '광령리'), ('하귀리', '유수암리'), ('애월읍사무소', '소길리'), ('애월읍사무소', '새별오름'),
    ('새별오름', '금악리교차로'), ('금악리교차로', '한림공원'), ('금악리교차로', '저지오름삼거리'),
    ('저지오름삼거리', '신창풍차해안'), ('저지오름삼거리', '협재해수욕장'), ('저지오름삼거리', '오설록'),
    ('오설록', '고산리'), ('오설록', '덕수리'), ('덕수리', '산방산교차로'), ('덕수리', '안덕계곡'),
    ('오설록', '새별오름'), ('새별오름', '안덕계곡'), ('새별오름', '중문관광단지'),

    # [6] 한라산 횡단 및 동서 연결 산록도로
    ('아라동(아라초)', '관음사입구'), ('관음사입구', '광령리'), ('관음사입구', '봉개교차로'),
    ('관음사입구', '성판악'), ('관음사입구', '1100고지'), ('성판악', '한라산국립공원'),
    ('성판악', '교래사거리'), ('성판악', '효돈동'), ('성판악', '동문로터리'),
    ('1100고지', '한라산국립공원'), ('1100고지', '서귀포치유의숲'), ('서귀포치유의숲', '중앙로터리'),
    ('서귀포치유의숲', '서귀포버스터미널'), ('1100고지', '중문관광단지'), ('1100고지', '오설록'),
    ('1100고지', '금악리교차로')
]

GRAPH_NODES = {node: [] for node in LOCATION_COORDS}
for u, v in RAW_EDGES:
    GRAPH_NODES[u].append(v)
    GRAPH_NODES[v].append(u)

ROUTE_CACHE = {}

def latlon_to_tile(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile

def tile_to_latlon(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1.0 - 2.0 * ytile / n)))
    lat = math.degrees(lat_rad)
    return lat, lon

def fetch_osrm_geometry(u, v):
    key = tuple(sorted([u, v]))
    if key in ROUTE_CACHE:
        return ROUTE_CACHE[key]
    
    start_lat, start_lon = LOCATION_COORDS[u]
    end_lat, end_lon = LOCATION_COORDS[v]
    url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    
    try:
        res = requests.get(url, timeout=3).json()
        if res.get('code') == 'Ok':
            route = res['routes'][0]
            coords = route['geometry']['coordinates']
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            dist = route['distance']
            ROUTE_CACHE[key] = (lons, lats, dist)
            return ROUTE_CACHE[key]
    except Exception:
        pass
    
    lons = [start_lon, end_lon]
    lats = [start_lat, end_lat]
    ROUTE_CACHE[key] = (lons, lats, 10000.0)
    return ROUTE_CACHE[key]

def haversine(u, v):
    lat1, lon1 = LOCATION_COORDS[u]
    lat2, lon2 = LOCATION_COORDS[v]
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_edge_weight(u, v, traffic_edge, traffic_factor, is_blocked):
    edge_key = tuple(sorted([u, v]))
    _, _, base_dist = fetch_osrm_geometry(u, v)

    if is_blocked and edge_key == traffic_edge:
        return float('inf')

    if edge_key == traffic_edge:
        return base_dist * traffic_factor
    
    return base_dist

# --- 최단경로 탐색 알고리즘 모듈 ---

def run_dijkstra(start_node, end_node, traffic_edge, traffic_factor, is_blocked):
    distances = {node: float('inf') for node in LOCATION_COORDS}
    distances[start_node] = 0
    previous = {node: None for node in LOCATION_COORDS}
    pq = [(0, start_node)]
    visited = set()
    steps = []

    while pq:
        curr_dist, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        steps.append({'type': 'visit', 'node': u, 'curr_dist': curr_dist, 'active_edge': None})
        if u == end_node:
            break

        for v in GRAPH_NODES[u]:
            if v in visited:
                continue
            w = get_edge_weight(u, v, traffic_edge, traffic_factor, is_blocked)
            if distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                previous[v] = u
                heapq.heappush(pq, (distances[v], v))
                steps.append({'type': 'relax', 'node': u, 'target': v, 'curr_dist': distances[v], 'active_edge': (u, v)})

    path = []
    curr = end_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    steps.append({'type': 'done', 'path': path, 'distance': distances[end_node]})
    return steps

def run_astar(start_node, end_node, traffic_edge, traffic_factor, is_blocked):
    g_score = {node: float('inf') for node in LOCATION_COORDS}
    g_score[start_node] = 0
    f_score = {node: float('inf') for node in LOCATION_COORDS}
    f_score[start_node] = haversine(start_node, end_node)
    
    previous = {node: None for node in LOCATION_COORDS}
    pq = [(f_score[start_node], start_node)]
    visited = set()
    steps = []

    while pq:
        _, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        steps.append({'type': 'visit', 'node': u, 'curr_dist': g_score[u], 'active_edge': None})
        if u == end_node:
            break

        for v in GRAPH_NODES[u]:
            if v in visited:
                continue
            w = get_edge_weight(u, v, traffic_edge, traffic_factor, is_blocked)
            tentative_g = g_score[u] + w
            if tentative_g < g_score[v]:
                previous[v] = u
                g_score[v] = tentative_g
                f_score[v] = g_score[v] + haversine(v, end_node)
                heapq.heappush(pq, (f_score[v], v))
                steps.append({'type': 'relax', 'node': u, 'target': v, 'curr_dist': g_score[v], 'active_edge': (u, v)})

    path = []
    curr = end_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    steps.append({'type': 'done', 'path': path, 'distance': g_score[end_node]})
    return steps

def run_bellman_ford(start_node, end_node, traffic_edge, traffic_factor, is_blocked):
    distances = {node: float('inf') for node in LOCATION_COORDS}
    distances[start_node] = 0
    previous = {node: None for node in LOCATION_COORDS}
    steps = []

    # 양방향 간선 목록 생성
    all_edges = []
    for u, v in RAW_EDGES:
        w = get_edge_weight(u, v, traffic_edge, traffic_factor, is_blocked)
        all_edges.append((u, v, w))
        all_edges.append((v, u, w))

    num_nodes = len(LOCATION_COORDS)
    
    for i in range(num_nodes - 1):
        updated = False
        for u, v, w in all_edges:
            if distances[u] != float('inf') and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                previous[v] = u
                updated = True
                steps.append({'type': 'relax', 'node': u, 'target': v, 'curr_dist': distances[v], 'active_edge': (u, v)})
        if not updated:
            break

    path = []
    curr = end_node
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()

    steps.append({'type': 'done', 'path': path, 'distance': distances[end_node]})
    return steps

def run_floyd_warshall(start_node, end_node, traffic_edge, traffic_factor, is_blocked):
    nodes = list(LOCATION_COORDS.keys())
    dist = {u: {v: float('inf') for v in nodes} for u in nodes}
    next_node = {u: {v: None for v in nodes} for u in nodes}
    steps = []

    for u in nodes:
        dist[u][u] = 0

    for u, v in RAW_EDGES:
        w = get_edge_weight(u, v, traffic_edge, traffic_factor, is_blocked)
        dist[u][v] = w
        dist[v][u] = w
        next_node[u][v] = v
        next_node[v][u] = u

    # Floyd-Warshall 3중 루프
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] != float('inf') and dist[k][j] != float('inf'):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        next_node[i][j] = next_node[i][k]
                        if i == start_node:
                            steps.append({'type': 'relax', 'node': k, 'target': j, 'curr_dist': dist[i][j], 'active_edge': (i, k)})

    # 경로 복원
    path = []
    if next_node[start_node][end_node] is not None:
        curr = start_node
        path.append(curr)
        while curr != end_node:
            curr = next_node[curr][end_node]
            if curr is None:
                break
            path.append(curr)

    steps.append({'type': 'done', 'path': path, 'distance': dist[start_node][end_node]})
    return steps


ALGORITHMS = {
    "다익스트라": run_dijkstra,
    "A*": run_astar,
    "벨먼-포드": run_bellman_ford,
    "플로이드-워셜": run_floyd_warshall,
}

@app.route("/")
def index():
    return render_template("index.html", nodes=sorted(LOCATION_COORDS.keys()), edges=RAW_EDGES)

@app.route("/api/route", methods=["POST"])
def route_api():
    data = request.get_json(force=True)

    algo = data.get("algorithm", "다익스트라")
    start = data.get("start")
    end = data.get("end")
    edge_index = int(data.get("traffic_edge_index", 0))
    traffic_factor = float(data.get("traffic_factor", 2.5))
    is_blocked = bool(data.get("blocked", False))

    if start not in LOCATION_COORDS or end not in LOCATION_COORDS:
        return jsonify({"error": "출발지 또는 목적지가 올바르지 않습니다."}), 400

    if start == end:
        return jsonify({"error": "출발지와 목적지가 같습니다."}), 400

    if edge_index < 0 or edge_index >= len(RAW_EDGES):
        edge_index = 0

    traffic_edge = tuple(sorted(RAW_EDGES[edge_index]))

    fn = ALGORITHMS.get(algo)
    if fn is None:
        return jsonify({"error": "지원하지 않는 알고리즘입니다."}), 400

    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        steps = fn(start, end, traffic_edge, traffic_factor, is_blocked)
    except Exception as e:
        tracemalloc.stop()
        return jsonify({"error": str(e)}), 500

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    done = steps[-1] if steps else {
        "type": "done", "path": [], "distance": float("inf")
    }

    distance = done.get("distance", float("inf"))
    if math.isinf(distance):
        distance_value = None
        eta_minutes = None
    else:
        distance_value = distance
        dist_km = distance / 1000.0
        eta_minutes = int((dist_km / 55.0) * 60)

    return jsonify({
        "algorithm": algo,
        "start": start,
        "end": end,
        "traffic_edge": list(traffic_edge),
        "traffic_factor": traffic_factor,
        "blocked": is_blocked,
        "steps": steps,
        "path": done.get("path", []),
        "distance_m": distance_value,
        "distance_km": None if distance_value is None else distance_value / 1000.0,
        "eta_minutes": eta_minutes,
        "elapsed_ms": elapsed_ms,
        "peak_kb": peak_mem / 1024.0,
    })

@app.route("/api/edge-geometry")
def edge_geometry():
    """Return OSRM road geometry for drawing the graph in Leaflet."""
    result = []
    for u, v in RAW_EDGES:
        lons, lats, dist = fetch_osrm_geometry(u, v)
        result.append({
            "u": u, "v": v,
            "coordinates": [[lat, lon] for lon, lat in zip(lons, lats)],
            "distance_m": dist
        })
    return jsonify(result)

@app.route("/api/nodes")
def nodes_api():
    return jsonify([
        {"name": name, "lat": lat, "lon": lon}
        for name, (lat, lon) in LOCATION_COORDS.items()
    ])

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
