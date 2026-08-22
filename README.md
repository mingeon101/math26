# 제주도 경로 탐색 알고리즘 웹 시뮬레이션 - Render 배포

## 파일 구조

jeju_route_render/
├── app.py
├── requirements.txt
├── render.yaml
└── templates/
    └── index.html

## Render 배포

1. GitHub 저장소에 위 파일을 그대로 업로드합니다.
2. Render에서 New > Blueprint를 선택합니다.
3. GitHub 저장소를 연결합니다.
4. render.yaml을 읽으면 웹 서비스가 생성됩니다.
5. 배포 완료 후 Render가 제공하는 https://....onrender.com 주소로 접속합니다.

## 수동 생성 시

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

## 주의

OSRM 공개 서버를 사용하므로 초기 지도/도로 geometry 로딩 및 첫 경로 계산에는 시간이 걸릴 수 있습니다.
Render 무료 인스턴스는 일정 시간 사용하지 않으면 sleep될 수 있어 첫 접속이 느릴 수 있습니다.
