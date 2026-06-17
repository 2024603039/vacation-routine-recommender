from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import math

app = FastAPI()


class PlanRequest(BaseModel):
    start_date: date
    end_date: date
    tasks: str
    certificate_name: str
    certificate_total_hours: int
    weekly_study_days: int
    day_start: str
    day_end: str
    mood: str


def time_to_minutes(time_text: str):
    hour, minute = map(int, time_text.split(":"))
    return hour * 60 + minute


def minutes_to_time(minutes: int):
    minutes = minutes % (24 * 60)
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def add_schedule(schedule, current, minutes, title, description, category):
    schedule.append({
        "time": f"{minutes_to_time(current)} - {minutes_to_time(current + minutes)}",
        "title": title,
        "description": description,
        "minutes": minutes,
        "category": category
    })
    return current + minutes


@app.get("/")
def root():
    return {"message": "Vacation planner FastAPI is running!"}


@app.post("/plan")
def make_plan(data: PlanRequest):
    total_vacation_days = (data.end_date - data.start_date).days + 1

    if total_vacation_days <= 0:
        return {
            "error": True,
            "message": "방학 끝나는 날은 시작일보다 뒤여야 합니다."
        }

    # 방학 중 실제 공부할 날짜 수 계산
    study_days = max(1, math.floor(total_vacation_days / 7 * data.weekly_study_days))

    # 자격증 하루 공부량 계산
    total_cert_minutes = data.certificate_total_hours * 60
    daily_cert_minutes = math.ceil(total_cert_minutes / study_days)

    # 자격증 공부는 2번으로 쪼개기
    cert_first_minutes = math.ceil(daily_cert_minutes * 0.55)
    cert_second_minutes = daily_cert_minutes - cert_first_minutes

    # 사용자가 입력한 추가 할 일
    task_list = [task.strip() for task in data.tasks.split(",") if task.strip()]

    if len(task_list) == 0:
        task_list = ["운동", "방 정리", "자유시간"]

    start_min = time_to_minutes(data.day_start)
    end_min = time_to_minutes(data.day_end)

    if end_min <= start_min:
        end_min += 24 * 60

    available_minutes = end_min - start_min

    # 기본 생활 루틴 시간
    wake_minutes = 40
    breakfast_minutes = 40
    lunch_minutes = 60
    dinner_minutes = 60
    rest_minutes = 30
    evening_wrap_minutes = 30

    fixed_minutes = (
        wake_minutes
        + breakfast_minutes
        + lunch_minutes
        + dinner_minutes
        + rest_minutes
        + evening_wrap_minutes
        + daily_cert_minutes
    )

    remaining_minutes = max(0, available_minutes - fixed_minutes)

    # 추가 할 일 시간 배분
    task_minutes = max(20, remaining_minutes // len(task_list))

    schedule = []
    current = start_min

    current = add_schedule(
        schedule,
        current,
        wake_minutes,
        "기상 / 준비",
        "세수, 물 마시기, 오늘 계획 확인",
        "생활"
    )

    current = add_schedule(
        schedule,
        current,
        breakfast_minutes,
        "아침 식사",
        "아침 먹고 하루 시작 준비하기",
        "식사"
    )

    current = add_schedule(
        schedule,
        current,
        cert_first_minutes,
        f"{data.certificate_name} 공부 1차",
        f"집중력이 좋은 시간에 {data.certificate_name} 핵심 개념 공부",
        "자격증"
    )

    current = add_schedule(
        schedule,
        current,
        rest_minutes,
        "짧은 휴식",
        "눈 쉬기, 스트레칭, 물 마시기",
        "휴식"
    )

    current = add_schedule(
        schedule,
        current,
        lunch_minutes,
        "점심 식사",
        "점심 먹고 잠깐 쉬기",
        "식사"
    )

    # 사용자가 적은 할 일 중 절반은 오후에 배치
    half = math.ceil(len(task_list) / 2)
    afternoon_tasks = task_list[:half]
    evening_tasks = task_list[half:]

    for task in afternoon_tasks:
        current = add_schedule(
            schedule,
            current,
            task_minutes,
            task,
            f"{task}을/를 {task_minutes}분 동안 진행",
            "개인 할 일"
        )

    if cert_second_minutes > 0:
        current = add_schedule(
            schedule,
            current,
            cert_second_minutes,
            f"{data.certificate_name} 공부 2차",
            f"오전에 공부한 내용 복습 또는 문제 풀이",
            "자격증"
        )

    current = add_schedule(
        schedule,
        current,
        dinner_minutes,
        "저녁 식사",
        "저녁 먹고 에너지 회복하기",
        "식사"
    )

    for task in evening_tasks:
        current = add_schedule(
            schedule,
            current,
            task_minutes,
            task,
            f"{task}을/를 {task_minutes}분 동안 진행",
            "개인 할 일"
        )

    current = add_schedule(
        schedule,
        current,
        evening_wrap_minutes,
        "하루 마무리",
        "오늘 한 일 체크하고 내일 할 일 적기",
        "정리"
    )

    # 난이도 판단
    if daily_cert_minutes >= 240:
        difficulty = "빡셈"
        advice = "하루 자격증 공부 시간이 꽤 많아요. 주간 공부일을 늘리거나 목표 시간을 줄이면 더 현실적이에요."
    elif daily_cert_minutes >= 120:
        difficulty = "보통"
        advice = "충분히 가능한 계획이에요. 오전과 오후로 나눠서 공부하면 부담이 줄어들어요."
    else:
        difficulty = "여유"
        advice = "부담이 크지 않은 계획이에요. 남는 시간에 복습이나 기출 풀이를 넣으면 좋아요."

    # 기분별 조언
    if data.mood == "지침":
        mood_advice = "오늘은 모든 일을 완벽하게 하려 하지 말고, 자격증 공부 1차만 끝내도 성공이에요."
    elif data.mood == "불안함":
        mood_advice = "불안할수록 계획표를 눈에 보이게 만들고 하나씩 체크하는 게 좋아요."
    elif data.mood == "의욕 있음":
        mood_advice = "의욕 있을 때 너무 몰아서 하지 말고, 내일도 할 수 있을 만큼만 유지해요."
    elif data.mood == "심심함":
        mood_advice = "심심한 날에는 개인 할 일에 재미있는 활동을 하나 섞어보세요."
    else:
        mood_advice = "오늘은 계획표대로 차근차근 움직이면 충분해요."

    return {
        "error": False,
        "vacation_days": total_vacation_days,
        "study_days": study_days,
        "certificate_name": data.certificate_name,
        "certificate_total_hours": data.certificate_total_hours,
        "daily_cert_minutes": daily_cert_minutes,
        "daily_cert_hours_text": f"{daily_cert_minutes // 60}시간 {daily_cert_minutes % 60}분",
        "difficulty": difficulty,
        "advice": advice,
        "mood_advice": mood_advice,
        "schedule": schedule
    }