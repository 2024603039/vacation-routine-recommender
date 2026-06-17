# 방학 루틴 추천 플래너

## 프로젝트 소개

방학 루틴 추천 플래너는 사용자가 방학 시작일과 종료일, 자격증 총 공부 목표 시간, 일주일 공부 횟수, 하루 시작 시간과 마무리 시간, 추가 할 일을 입력하면 맞춤형 하루 루틴을 추천해주는 웹 애플리케이션입니다.

Streamlit은 사용자 입력과 결과 출력을 담당하고, FastAPI는 입력값을 받아 방학 기간, 실제 공부일 수, 하루 자격증 공부량, 시간대별 추천 루틴을 계산한 뒤 JSON 형태로 반환합니다.

## 주요 기능

- 방학 기간 계산
- 자격증 하루 공부량 추천
- 일주일 공부 횟수 반영
- 사용자가 입력한 추가 할 일을 하루 루틴에 자동 배치
- 아침, 점심, 저녁 식사를 포함한 현실적인 시간표 생성
- 오늘 상태에 따른 맞춤형 조언 제공
- 원형 루틴 추천표 시각화
- 시간대별 추천 루틴 출력
- FastAPI JSON 추천 결과 확인

## 사용 기술

- Streamlit
- FastAPI
- Docker
- AWS EC2

## 프로젝트 구조

```text
vacation-routine-recommender/
│
├─ front/
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ Dockerfile
│  └─ .streamlit/
│     └─ config.toml
│
├─ back/
│  ├─ main.py
│  ├─ requirements.txt
│  └─ Dockerfile
│
├─ docker-compose.yml
├─ .gitignore
└─ README.md
