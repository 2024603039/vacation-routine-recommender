# 방학 루틴 추천 플래너

## 프로젝트 소개

방학 루틴 추천 플래너는 사용자가 방학 시작일과 종료일, 자격증 공부 목표 시간, 일주일 공부 횟수, 하루 시작 시간과 마무리 시간, 추가 할 일, 오늘 상태를 입력하면 맞춤형 하루 루틴을 추천해주는 웹 애플리케이션입니다.

Streamlit은 사용자 입력과 결과 출력을 담당하고, FastAPI는 입력값을 받아 방학 기간, 실제 공부일 수, 하루 자격증 공부량, 추천 난이도, 시간대별 추천 루틴을 계산한 뒤 JSON 형태로 반환합니다.

이 프로젝트는 Streamlit 프론트엔드와 FastAPI 백엔드를 분리하여 구현했으며, Docker 컨테이너를 이용해 AWS EC2 환경에서 실행되도록 구성했습니다.

## 주요 기능

* 방학 기간 계산
* 자격증 하루 공부량 추천
* 일주일 공부 횟수 반영
* 사용자가 입력한 추가 할 일을 하루 루틴에 자동 배치
* 아침, 점심, 저녁 식사를 포함한 시간대별 루틴 생성
* 오늘 상태에 따른 맞춤형 조언 제공
* 원형 루틴 추천표 시각화
* 시간대별 추천 루틴 출력
* FastAPI에서 반환한 JSON 추천 결과 확인

## 사용 기술

* Streamlit
* FastAPI
* Docker
* AWS EC2

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
```

## 실행 흐름

```text
사용자 입력
→ Streamlit 프론트엔드
→ FastAPI 백엔드 요청
→ 추천 결과 JSON 반환
→ Streamlit 화면 출력
```

## Streamlit 프론트엔드 역할

Streamlit은 사용자가 값을 입력하는 화면을 제공합니다.

사용자는 다음 정보를 입력할 수 있습니다.

* 방학 시작일
* 방학 종료일
* 준비할 자격증 이름
* 방학 동안 자격증 공부 총 목표 시간
* 일주일 공부 횟수
* 자격증 외 추가 할 일
* 하루 시작 시간
* 하루 마무리 시간
* 오늘 상태

입력 후 추천 버튼을 누르면 Streamlit은 FastAPI의 `/plan` 엔드포인트로 입력값을 전송합니다.

## FastAPI 백엔드 역할

FastAPI는 Streamlit에서 전달받은 입력값을 바탕으로 추천 결과를 생성합니다.

FastAPI는 다음 정보를 계산하여 JSON 형태로 반환합니다.

* 전체 방학 기간
* 실제 공부일 수
* 하루 자격증 공부량
* 추천 난이도
* 맞춤형 조언
* 오늘 상태에 따른 조언
* 시간대별 추천 루틴

## 추천 방식

추천 방식은 규칙 기반 추천 방식입니다.

입력된 방학 기간, 주간 공부 횟수, 총 공부 목표 시간을 바탕으로 하루 공부량을 계산합니다.
또한 사용자가 입력한 추가 할 일을 시간대별 루틴에 자동으로 배치하여 하루 계획을 추천합니다.

추천 난이도는 하루 공부량에 따라 다음과 같이 나뉩니다.

```text
하루 공부량이 많음 → 빡셈
하루 공부량이 적당함 → 보통
하루 공부량이 적음 → 여유
```

## API 엔드포인트

### GET /

FastAPI 서버가 정상적으로 실행 중인지 확인하는 기본 엔드포인트입니다.

### POST /plan

Streamlit에서 전달한 입력값을 받아 추천 루틴을 생성합니다.

요청 데이터 예시는 다음과 같습니다.

```json
{
  "start_date": "2026-06-17",
  "end_date": "2026-08-31",
  "tasks": "운동, 영어 공부, 방 정리",
  "certificate_name": "SQLD",
  "certificate_total_hours": 80,
  "weekly_study_days": 5,
  "day_start": "09:00",
  "day_end": "23:00",
  "mood": "평범함"
}
```

응답 데이터 예시는 다음과 같습니다.

```json
{
  "error": false,
  "vacation_days": 76,
  "study_days": 54,
  "certificate_name": "SQLD",
  "certificate_total_hours": 80,
  "daily_cert_minutes": 89,
  "daily_cert_hours_text": "1시간 29분",
  "difficulty": "여유",
  "advice": "부담이 크지 않은 계획이에요. 남는 시간에 복습이나 기출 풀이를 넣으면 좋아요.",
  "mood_advice": "오늘은 계획표대로 차근차근 움직이면 충분해요.",
  "schedule": []
}
```

## Docker 실행 방법

프로젝트 루트 폴더에서 다음 명령어를 실행합니다.

```bash
docker compose up -d --build
```

실행 상태는 다음 명령어로 확인할 수 있습니다.

```bash
docker ps
```

## 로컬 접속 주소

Streamlit 앱 주소는 다음과 같습니다.

```text
http://localhost:8501
```

FastAPI 문서 주소는 다음과 같습니다.

```text
http://localhost:8000/docs
```

## AWS EC2 배포

이 프로젝트는 AWS Learner Lab의 EC2 환경에서 Docker를 이용해 실행했습니다.

EC2에서 Streamlit과 FastAPI는 각각 다른 컨테이너로 실행됩니다.

```text
Streamlit 컨테이너 → 8501 포트
FastAPI 컨테이너 → 8000 포트
```

EC2 접속 주소 예시는 다음과 같습니다.

```text
http://EC2_PUBLIC_IP:8501
```

FastAPI 문서 주소 예시는 다음과 같습니다.

```text
http://EC2_PUBLIC_IP:8000/docs
```

## 데모 영상 확인 내용

데모 영상에서는 다음 내용을 확인할 수 있습니다.

* GitHub 저장소 구조
* EC2 주소를 통한 Streamlit 앱 접속
* Streamlit 화면에서 사용자 입력
* 추천 요청 버튼 클릭
* 추천 결과 출력
* FastAPI에서 반환된 JSON 결과 확인
* EC2 터미널에서 `docker ps` 명령어 실행
* Streamlit 컨테이너와 FastAPI 컨테이너 실행 상태 확인
* FastAPI docs에서 `/plan` 엔드포인트 확인

## 프로젝트 특징

이 앱은 단순한 문구 추천이 아니라 사용자의 방학 기간과 자격증 공부 목표를 바탕으로 실제 하루 루틴을 계산합니다.

또한 원형 루틴 추천표와 시간대별 루틴을 함께 제공하여 사용자가 자신의 방학 계획을 직관적으로 확인할 수 있도록 구성했습니다.
