import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정
st.set_page_config(
    page_title="봉이 & 꼬밍 맞춤 피부관리 🌸",
    page_icon="✨",
    layout="centered",
)

# 2. 구글 시트 연결
conn = st.connection("gsheets", type=GSheetsConnection)

# 기존 저장된 데이터 불러오기
try:
    data = conn.read(worksheet="Sheet1", ttl="0s")
except Exception:
    data = pd.DataFrame(columns=["이름", "생리시작일", "등록일시"])

st.title("🌸 생리주기 맞춤 스킨케어 💖")


# 3. 생리주기별 관리법 및 손메모 루틴 반영 함수
def get_skincare_info(day, cycle_length=28):
    day = ((day - 1) % cycle_length) + 1

    if 1 <= day <= 5:
        phase_name = "🩸 생리 중 (Day 1~5)"
        tag = "관리는 쉬고 진정/보습 집중 ☕"
        status = "호르몬 수치가 낮아 피부가 매우 예민하고 건조합니다. 무리한 관리는 피하고 휴식을 취해주세요."
        morning_routine = (
            "💧 자극 없는 가벼운 물세안 & 순한 수분 보습"
        )
        night_routine = """🌿 진정 케어: 시카/세라마이드 위주의 진정·보습 크림 가볍게 바르기
                            ⬇️ (5분 후)
                            🧴 멜라토닝크림(10월까지): 기미·잡티 부위에 콕콕 찍어바르기"""

    elif 6 <= day <= 14:  # 약 9일간의 황금기
        golden_day = day - 5
        phase_name = (
            f"✨ 황금기 (Day 6~14 / 황금기 {golden_day}일차)"
        )
        tag = (
            "피부 컨디션 최상! 리들샷 & 영양 집중 케어 🌟"
        )
        status = "에스트로겐 활성으로 흡수력이 가장 좋은 시기입니다. 리들샷과 고기능성 세럼을 활용해보세요!"
        morning_routine = "아침: 효소 파우더 클렌징 (리들샷 사용 후 주 1~2회 가볍게)"
        night_routine = """🌙 **저녁 집중 케어 (택 1)**

                        ✨ **Option A. 리들샷 & 영양 흡수 케어**
                        1. 리들샷(주3회) + 매트릭실 + 보습 듬뿍
                        2. 디바이스 흡수모드 / 초음파(주 1회) + 마스크팩(주2-3회)


                        ---

                        🧴 **Option B. 멜라토닝 케어**
                        1. 보습크림 바르기
                        ⬇️ (5분 후)
                        2. 멜라토닝크림(10월까지): 기미·잡티 부위에 콕콕 찍어바르기"""

    elif 15 <= day <= 18:
        phase_name = (
            "🥚 배란기 / 호르몬 전환기 (Day 15~18)"
        )
        tag = "유수분 밸런스 & 진정 대비 🌿"
        status = "에스트로겐이 줄어들고 체온과 피지 분비가 조금씩 올라가는 전환기입니다."
        morning_routine = "💧 아침: 나이아신아마이드 세럼 (유수분 밸런스 & 피지 조절)"
        night_routine = "🌙 저녁: 매트릭실 + 디바이스 흡수모드 ➔ 보습 ➔ 멜라토닝 크림"

    else:  # Day 19~28
        phase_name = "🌧️ 생리 전 / 황체기 (Day 19~28)"
        tag = "트러블 주의 & 모공관리 🧼"
        status = "프로게스테론 영향으로 피지가 폭발하고 트러블이 올라오기 쉬운 시기입니다."
        morning_routine = (
            "💧 아침: 나이아신+ 알부틴 세럼으로 트러블/피지 케어"
        )
        night_routine = """🌙 **[기본 저녁 케어]**
                            1. 매트릭실 + 디바이스 흡수모드
                            ⬇️ (5분 후)
                            2. 🧴 멜라토닝크림(10월까지): 기미·잡티에 콕콕 찍어바르기

                            ---
                            🍑 **[특별 딥클렌징 케어]**
                            1. 클레이팩(전체 or T존/나비존) 
                            ⬇️ 8분 (촉촉할 때 닦아내기)
                            2. 물기 닦고 애크린겔 바르기
                            3. 세럼 & 보습제 듬뿍 바르기"""
    return (
        day,
        phase_name,
        tag,
        status,
        morning_routine,
        night_routine,
    )


# 4. 사용자 탭 화면 출력 함수
def render_user_tab(user_name, user_key):
    st.subheader(f"👤 {user_name}님의 생리일 설정")

    # 구글 시트에서 해당 사용자의 가장 최근 생리일 가져오기
    user_data = (
        data[data["이름"] == user_name]
        if not data.empty
        else pd.DataFrame()
    )

    default_date = datetime.date.today() - datetime.timedelta(
        days=7
    )
    if not user_data.empty and "생리시작일" in user_data.columns:
        try:
            last_saved = user_data.iloc[-1]["생리시작일"]
            default_date = datetime.datetime.strptime(
                str(last_saved), "%Y-%m-%d"
            ).date()
        except Exception:
            pass

    # 입력 폼
    with st.form(key=f"form_{user_key}"):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "최근 생리 시작일",
                value=default_date,
                key=f"date_input_{user_key}",
            )
        with col2:
            cycle_len = st.number_input(
                "생리 주기(일)",
                min_value=20,
                max_value=40,
                value=28,
                key=f"cycle_input_{user_key}",
            )

        save_btn = st.form_submit_button(
            "💾 날짜 구글 시트에 저장하기"
        )

        if save_btn:
            new_row = pd.DataFrame(
                [
                    {
                        "이름": user_name,
                        "생리시작일": str(start_date),
                        "등록일시": (
                            datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        ),
                    }
                ]
            )
            updated_df = pd.concat(
                [data, new_row], ignore_index=True
            )
            conn.update(worksheet="Sheet1", data=updated_df)
            st.success(
                f"🎉 {user_name}님의 생리 시작일({start_date})이 구글 시트에 저장되었습니다!"
            )
            st.rerun()

    # 계산 로직
    today = datetime.date.today()
    days_passed = (today - start_date).days

    if days_passed < 0:
        st.error("⚠️ 시작일이 오늘보다 미래일 수 없습니다.")
        return

    (
        day_in_cycle,
        phase_name,
        tag,
        status,
        morning,
        night,
    ) = get_skincare_info(days_passed + 1, cycle_len)

    st.divider()
    st.markdown(
        f"### 📅 오늘은 주기 **D+{day_in_cycle}일차**입니다!"
    )
    st.progress(min(day_in_cycle / cycle_len, 1.0))

    # 주기별 스킨케어 카드
    with st.container(border=True):
        st.markdown(f"## {phase_name}")
        st.markdown(f"**상태:** `{tag}`")
        st.info(status)

        st.markdown("---")
        st.markdown(f"**☀️ {morning}**")
        st.markdown(f"**🌙 {night}**")

    # 5. 🔥 황금기 전용 요일별 케어 체크박스 표
    if 6 <= day_in_cycle <= 14:
        st.divider()
        st.subheader(
            "🗓️ 황금기 9일간 스킨케어 중복 방지 기록표"
        )
        st.caption(
            "리들샷과 디바이스 케어가 중복되지 않도록 날짜별로 체크해두세요!"
        )

        cols = st.columns(3)
        days_label = [
            "1일차",
            "2일차",
            "3일차",
            "4일차",
            "5일차",
            "6일차",
            "7일차",
            "8일차",
            "9일차",
        ]

        for idx, d_name in enumerate(days_label):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**📍 황금기 {d_name}**")
                    st.checkbox(
                        "🫧 효소파우더",
                        key=f"ep_g_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "💉 리들샷",
                        key=f"rs_g_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "💆‍♀️ 디바이스",
                        key=f"dv_g_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "🎭 마스크팩",
                        key=f"mp_g_{user_key}_{idx}",
                    )

    # 6. 🌧️ 황체기 전용 모공케어 체크박스 표
    if 19 <= day_in_cycle <= 28:
        st.divider()
        st.subheader(
            "🗓️ 황체기 9일간 모공케어 중복 방지 기록표"
        )
        st.caption("주 1~2회 권장")

        cols = st.columns(3)
        days_label = [
            "1일차",
            "2일차",
            "3일차",
            "4일차",
            "5일차",
            "6일차",
            "7일차",
            "8일차",
            "9일차",
        ]

        for idx, d_name in enumerate(days_label):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**📍 황체기 {d_name}**")
                    st.checkbox(
                        "🫛 클레이팩",
                        key=f"clay_l_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "🧴 애크린겔",
                        key=f"acne_l_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "💆‍♀️ 디바이스",
                        key=f"dv_l_{user_key}_{idx}",
                    )
                    st.checkbox(
                        "🎭 마스크팩",
                        key=f"mp_l_{user_key}_{idx}",
                    )

    # 다음 생리 D-day
    next_date = start_date + datetime.timedelta(days=cycle_len)
    d_day = (next_date - today).days
    st.caption(
        f"🔮 다음 생리 예정일: {next_date.strftime('%Y-%m-%d')} (D-{d_day})"
    )


# 7. 메인 탭 구조
tab_bong, tab_kkoming = st.tabs(["🌸 봉이", "🎀 꼬밍"])

with tab_bong:
    render_user_tab("봉이", "bong")

with tab_kkoming:
    render_user_tab("꼬밍", "kkoming")
