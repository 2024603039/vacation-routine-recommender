import streamlit as st
import streamlit.components.v1 as components
import requests
from datetime import date, time
import math
from html import escape

st.set_page_config(
    page_title="방학 루틴 추천 플래너",
    page_icon="🧸",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff7fb 0%, #f5f0ff 45%, #eef8ff 100%);
    color: #333333;
}

html, body, [class*="css"], .stMarkdown, .stText, p, div, span, label {
    color: #333333 !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1 {
    color: #ff5c9a !important;
    text-align: center;
    font-weight: 900;
}

h2, h3 {
    color: #5b4fcf !important;
    font-weight: 800;
}

.small-desc {
    text-align: center;
    font-size: 18px;
    line-height: 1.7;
}

.metric-card {
    background-color: #fff4fa;
    padding: 20px;
    border-radius: 22px;
    border: 2px solid #ffd6e8;
    text-align: center;
    min-height: 125px;
}

.metric-card h3 {
    color: #ff5c9a !important;
    margin-bottom: 6px;
}

.metric-card p {
    font-size: 22px;
    font-weight: 900;
    margin: 0;
}

.schedule-card {
    background-color: white;
    padding: 16px 18px;
    border-radius: 18px;
    margin-bottom: 10px;
    border-left: 8px solid #ff8fab;
    box-shadow: 0 4px 12px rgba(120, 100, 180, 0.12);
}

.schedule-card b {
    color: #333333 !important;
    font-size: 17px;
}

.schedule-time {
    color: #ff5c9a !important;
    font-weight: 800;
}

.legend-item {
    background: white;
    padding: 10px 14px;
    border-radius: 14px;
    margin-bottom: 8px;
    border: 1px solid #f1d7e5;
    box-shadow: 0 3px 8px rgba(120, 100, 180, 0.08);
}

.color-dot {
    display: inline-block;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    margin-right: 8px;
}

.stButton > button {
    width: 100%;
    border-radius: 24px;
    background: linear-gradient(90deg, #ff7fab, #a78bfa);
    color: white !important;
    border: none;
    padding: 0.9rem;
    font-size: 18px;
    font-weight: 800;
    box-shadow: 0 8px 18px rgba(167, 139, 250, 0.35);
}

.stButton > button:hover {
    background: linear-gradient(90deg, #ff5c9a, #8b5cf6);
    color: white !important;
    border: none;
}

textarea {
    border-radius: 16px !important;
    color: #333333 !important;
    background-color: white !important;
}

input {
    color: #333333 !important;
}

.stSelectbox label,
.stTextInput label,
.stTextArea label,
.stDateInput label,
.stTimeInput label,
.stNumberInput label,
.stSlider label {
    color: #333333 !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)


def split_korean_text(text, size=6):
    text = str(text)
    return [text[i:i + size] for i in range(0, len(text), size)]


def polar_to_xy(cx, cy, r, angle_deg):
    angle_rad = math.radians(angle_deg - 90)
    x = cx + r * math.cos(angle_rad)
    y = cy + r * math.sin(angle_rad)
    return x, y


def make_life_plan_svg(schedule):
    colors = [
        "#77b7df",
        "#ffb3a7",
        "#fff176",
        "#94e3e8",
        "#f3a6b5",
        "#9fa8da",
        "#c8e6c9",
        "#ffd6a5",
        "#cdb4db",
        "#bde0fe",
    ]

    cx, cy = 260, 260
    r = 220
    total = sum(item["minutes"] for item in schedule)

    current_angle = 0
    svg_parts = []

    svg_parts.append(f"""
    <svg viewBox="0 0 520 520" width="100%" height="560" xmlns="http://www.w3.org/2000/svg">
        <circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="white" stroke="#222" stroke-width="3"/>
    """)

    for i, item in enumerate(schedule):
        minutes = item["minutes"]
        angle = minutes / total * 360
        start_angle = current_angle
        end_angle = current_angle + angle

        x1, y1 = polar_to_xy(cx, cy, r, start_angle)
        x2, y2 = polar_to_xy(cx, cy, r, end_angle)

        large_arc = 1 if angle > 180 else 0
        color = colors[i % len(colors)]

        svg_parts.append(f"""
        <path d="M {cx} {cy} L {x1:.2f} {y1:.2f} A {r} {r} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z"
              fill="{color}" stroke="#222" stroke-width="2"/>
        """)

        mid_angle = start_angle + angle / 2
        label_x, label_y = polar_to_xy(cx, cy, r * 0.58, mid_angle)

        title = escape(item["title"])
        lines = split_korean_text(title, 6)

        svg_parts.append(f"""
        <text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="middle"
              dominant-baseline="middle"
              font-size="18" font-weight="900" fill="#111"
              font-family="Arial, sans-serif">
        """)

        start_dy = -12 * (len(lines) - 1)

        for j, line in enumerate(lines):
            svg_parts.append(f"""
            <tspan x="{label_x:.2f}" dy="{start_dy if j == 0 else 24}">{line}</tspan>
            """)

        svg_parts.append("</text>")

        time_text = escape(item["time"].split(" - ")[0])
        time_x, time_y = polar_to_xy(cx, cy, r + 24, start_angle)

        svg_parts.append(f"""
        <text x="{time_x:.2f}" y="{time_y:.2f}" text-anchor="middle"
              dominant-baseline="middle"
              font-size="13" font-weight="900" fill="#111"
              font-family="Arial, sans-serif">
              {time_text}
        </text>
        """)

        current_angle = end_angle

    last_time = escape(schedule[-1]["time"].split(" - ")[1])
    last_x, last_y = polar_to_xy(cx, cy, r + 24, 360)

    svg_parts.append(f"""
    <text x="{last_x:.2f}" y="{last_y:.2f}" text-anchor="middle"
          dominant-baseline="middle"
          font-size="13" font-weight="900" fill="#111"
          font-family="Arial, sans-serif">
          {last_time}
    </text>
    """)

    svg_parts.append(f"""
        <circle cx="{cx}" cy="{cy}" r="8" fill="#111"/>
    </svg>
    """)

    return "\n".join(svg_parts), colors


st.markdown("""
<h1>🧸 방학 루틴 추천 플래너</h1>
<p class="small-desc">
방학 기간과 목표를 입력하면<br>
나에게 맞는 하루 루틴을 추천해드릴게요 ✨
</p>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.15])

with left:
    st.subheader("🗓️ 방학 기간")

    start_date = st.date_input("방학 시작일", value=date.today())
    end_date = st.date_input("방학 끝나는 날", value=date.today())

    st.subheader("📚 자격증 공부 목표")

    certificate_name = st.text_input(
        "준비할 자격증 이름",
        placeholder="예: SQLD, ADsP, 정보처리기사",
        value="SQLD"
    )

    certificate_total_hours = st.number_input(
        "방학 동안 자격증 공부 총 목표 시간",
        min_value=1,
        max_value=500,
        value=80,
        step=1
    )

    weekly_study_days = st.slider(
        "일주일에 며칠 공부할 건가요?",
        min_value=1,
        max_value=7,
        value=5
    )

    st.subheader("🌷 나머지 방학 할 일")

    tasks = st.text_area(
        "자격증 말고 해야 할 일을 쉼표로 적어주세요.",
        placeholder="예: 운동, 영어 공부, 유튜브 기획, 방 정리",
        height=100
    )

    st.subheader("⏰ 하루 루틴 시간")

    day_start = st.time_input("하루 시작 시간", value=time(9, 0))
    day_end = st.time_input("하루 마무리 시간", value=time(23, 0))

    mood = st.selectbox(
        "오늘 상태",
        ["평범함", "지침", "불안함", "의욕 있음", "심심함"]
    )

    make_button = st.button("✨ 내 방학 루틴 추천받기")

with right:
    st.subheader("📌 앱 사용 방법")
    st.write("1. 방학 시작일과 끝나는 날을 입력하세요.")
    st.write("2. 자격증 총 공부 목표 시간을 입력하세요.")
    st.write("3. 일주일에 며칠 공부할지 정하세요.")
    st.write("4. 해야 할 일을 적으면 하루 루틴에 자동으로 들어갑니다.")
    st.write("5. 버튼을 누르면 맞춤형 방학 루틴이 추천됩니다.")
    st.info("예: 방학 40일, SQLD 80시간, 주 5일 공부라면 하루 공부량과 시간대별 루틴이 자동 추천됩니다.")

if make_button:
    if end_date < start_date:
        st.error("방학 끝나는 날은 시작일보다 뒤여야 해요.")
    else:
        try:
            response = requests.post(
                "http://back:8000/plan",
                json={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "tasks": tasks,
                    "certificate_name": certificate_name,
                    "certificate_total_hours": certificate_total_hours,
                    "weekly_study_days": weekly_study_days,
                    "day_start": day_start.strftime("%H:%M"),
                    "day_end": day_end.strftime("%H:%M"),
                    "mood": mood
                }
            )

            result = response.json()

            if result.get("error"):
                st.error(result["message"])
            else:
                st.divider()
                st.markdown("## ✅ 방학 루틴 추천 결과")

                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>방학 기간</h3>
                        <p>{result['vacation_days']}일</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>공부일 수</h3>
                        <p>{result['study_days']}일</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>하루 공부량</h3>
                        <p>{result['daily_cert_hours_text']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>추천 난이도</h3>
                        <p>{result['difficulty']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                st.write("")
                st.success(result["advice"])
                st.info(result["mood_advice"])

                st.divider()

                plan_col, list_col = st.columns([1, 1.2])

                with plan_col:
                    st.markdown("## 🕘 원형 루틴 추천표")

                    life_plan_svg, colors = make_life_plan_svg(result["schedule"])

                    components.html(
                        f"""
                        <div style="
                            background: white;
                            border-radius: 28px;
                            padding: 18px;
                            border: 3px solid #ffd6e8;
                            box-shadow: 0 8px 24px rgba(120, 100, 180, 0.14);
                        ">
                            {life_plan_svg}
                        </div>
                        """,
                        height=630
                    )

                    st.markdown("### 색상표")

                    for i, item in enumerate(result["schedule"]):
                        color = colors[i % len(colors)]
                        st.markdown(f"""
                        <div class="legend-item">
                            <span class="color-dot" style="background:{color};"></span>
                            <b>{item['title']}</b> · {item['minutes']}분
                        </div>
                        """, unsafe_allow_html=True)

                with list_col:
                    st.markdown("## ⏰ 시간대별 추천 루틴")

                    for item in result["schedule"]:
                        st.markdown(f"""
                        <div class="schedule-card">
                            <div class="schedule-time">{item['time']}</div>
                            <b>{item['title']}</b>
                            <p>{item['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)

                with st.expander("FastAPI에서 받은 JSON 추천 결과 확인하기"):
                    st.json(result)

        except Exception as e:
            st.error("FastAPI 서버와 연결할 수 없습니다.")
            st.write(e)
