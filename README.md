# 제주 경로 탐색 알고리즘 웹 버전

기존 PyQt5/Matplotlib 프로그램의 핵심 그래프 데이터와 4개 최단경로 알고리즘을 최대한 유지하고,
GUI 부분만 Flask + HTML/CSS/JavaScript + Leaflet 웹 UI로 교체한 버전입니다.

## 실행

```bash
pip install -r requirements.txt
python app.py
```

브라우저:
http://127.0.0.1:5000

## 포함 기능

- 다익스트라
- A*
- 벨먼-포드
- 플로이드-워셜
- 출발지/목적지 선택
- 53개 제주 거점과 88개 간선
- OSRM 도로 geometry
- 정체 구간 및 정체 지수
- 도로 완전 통제
- 탐색 시간
- 메모리 사용량
- 예상 소요 시간
- 최단 경로 표시
- 알고리즘 탐색 단계 슬라이더
- Leaflet 기반 지도 확대/축소

## 참고

기존 Python 프로그램은 Carto 타일과 Matplotlib을 사용했지만,
웹 버전에서는 지도 표시를 Leaflet + OpenStreetMap으로 변경했습니다.
최단경로 계산은 Python 백엔드에서 수행합니다.
