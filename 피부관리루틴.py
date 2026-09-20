import datetime
import json
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


# --- 1. 구글 시트 및 데이터 기본 설정 ---
conn = st.connection("gsheets", type=GSheetsConnection)

CYCLE_LENGTH = 29
USERS = ["꼬밍", "봉이"]
LOCAL_DATA_FILE = Path(__file__).with_name("cycle_dates.json")


def load_local_data():
    """Google Sheets에 쓰기 권한이 없을 때 사용할 로컬 저장소를 읽는다."""
    try:
        data = json.loads(LOCAL_DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_local_data(name, date_str):
    """사용자별 날짜를 앱 파일과 같은 폴더의 JSON 파일에 저장한다."""
    data = load_local_data()
    data[name] = {"date": date_str, "cycle": CYCLE_LENGTH}
    LOCAL_DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_user_data(name):
    """사용자별 마지막 생리 시작일을 불러온다."""
    local_user = load_local_data().get(name, {})
    if isinstance(local_user, dict) and local_user.get("date"):
        try:
            return pd.to_datetime(local_user["date"]).date().isoformat()
        except (TypeError, ValueError):
            pass

    try:
        df = conn.read(ttl=0)
        user_row = df[df["name"] == name]
        if not user_row.empty:
            return pd.to_datetime(user_row.iloc[0]["date"]).date().isoformat()
    except (KeyError, TypeError, ValueError):
        pass

    return datetime.date.today().isoformat()


def save_user_data(name, date_str):
    """Google Sheets에 저장하고, 공개 읽기 전용이면 로컬에 저장한다."""
    try:
        df = conn.read(ttl=0)
    except Exception:
        df = pd.DataFrame(columns=["name", "date", "cycle"])

    for column in ["name", "date", "cycle"]:
        if column not in df.columns:
            df[column] = None

    if name in df["name"].values:
        df.loc[df["name"] == name, ["date", "cycle"]] = [date_str, CYCLE_LENGTH]
    else:
        new_row = pd.DataFrame(
            [{"name": name, "date": date_str, "cycle": CYCLE_LENGTH}]
        )
        df = pd.concat([df, new_row], ignore_index=True)

    try:
        conn.update(data=df)
        st.cache_data.clear()
        return "google_sheets"
    except Exception as error:
        if error.__class__.__name__ != "UnsupportedOperationError":
            raise

        save_local_data(name, date_str)
        return "local"


def calculate_cycle_day(start_date_str):
    """마지막 생리 시작일을 기준으로 오늘의 29일 주기 일차를 계산한다."""
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        delta = datetime.date.today() - start_date
        return (delta.days % CYCLE_LENGTH) + 1
    except (TypeError, ValueError):
        return None


# --- 2. 루틴 박스 ---
def show_routine_box(time, title, items):
    if time == "아침":
        st.success(f"**☀️ 아침: {title}**")
    elif time == "저녁":
        st.info(f"**🌙 저녁: {title}**")
    elif time == "스페셜":
        st.warning(f"**🌋 스페셜: {title}**")

    for item in items:
        st.markdown(f"▪️ {item}")


# --- 3. 내 몸 주식회사 가이드 ---
def display_hormone_guide(day):
    progress_val = min(max(day / CYCLE_LENGTH, 0.0), 1.0)
    st.progress(
        progress_val,
        text=(
            f"현재 {day}일차 / {CYCLE_LENGTH}일 주기 "
            f"({int(progress_val * 100)}%) 진행 중"
        ),
    )

    st.markdown(
        f"""
        <h3 style='text-align: center; margin-bottom: -10px;'>
            🥚 내 피부 깐달걀 프로젝트: Day {day}
        </h3>
        <hr style='margin-top: 15px; margin-bottom: 20px;'>
        """,
        unsafe_allow_html=True,
    )

    phase1_end = 5
    phase2_end = 13
    phase3_end = 17

    st.divider()

    # 🩸 1단계: 생리 중 (Day 1~5)
    if 1 <= day <= phase1_end:
        st.markdown("#### 🩸 1단계: 생리 중 (피부 휴식 & 수분 올인!)")
        st.caption(
            "🚨 피부 장벽이 약하고 민감한 시기. 자극을 줄이고 충분히 "
            "쉬어주기! (기기·리들샷·효소·바하 전부 쉬기)"
        )

        col1, col2 = st.columns(2)
        with col1:
            show_routine_box(
                "아침",
                "수분 방어 & 순한 탄력",
                [
                    "수분 토너 (장벽/진정 베이스)",
                    "나이아신아마이드 + 알파 아르부틴 (피부톤/잡티 케어)",
                    "수분 크림 (보습막 코팅)",
                    "선크림 (자외선 차단 필수)",
                ],
            )

        with col2:
            show_routine_box(
                "저녁",
                "장벽 진정",
                [
                    "더랩 토너 (수분 공급)",
                    "매트릭실 (탄력 케어)",
                    "멜라토닝크림 (필요 부위에 제품 사용법대로 사용)",
                    "라로슈포제 시카플라스트 밤 (장벽 진정 마무리)",
                ],
            )

    # ✨ 2단계: 황금기 (Day 6~13)
    elif phase1_end < day <= phase2_end:
        p2_day = day - phase1_end
        p2_schedule = {
            1: "🅰️ 리들샷",
            2: "🅱️ 흡수모드",
            3: "🅳 레티날",
            4: "🅱️ 흡수모드",
            5: "🅲 초음파모드",
            6: "🅱️ 흡수모드",
            7: "🅳 레티날",
            8: "💆‍♀️ 미백 마스크팩 단독 (휴식 데이 ✨)",
        }
        todays_pick = p2_schedule.get(p2_day, "🅱️ 흡수모드")

        st.markdown(
            f"#### ✨ 2단계: 황금기 (주기 {day}일차 - 집중 관리 기간!)"
        )
        st.caption(
            "✨ 리들샷·레티날·초음파는 서로 다른 날에! "
            "중간중간 흡수모드와 보습 루틴으로 쉬어가기."
        )

        show_routine_box(
            "아침",
            "미백 광채 집중 ✨",
            [
                "아로마티카 에센스 (항산화/결 정돈)",
                "나이아신아마이드 + 알파 아르부틴 (피부톤/잡티 케어 💡)",
                "구달 청귤 아이크림 (눈가 다크서클/잡티 케어 🍊)",
                "수분 크림",
                "선크림 (자외선 차단 필수 🛡️)",
            ],
        )

        st.markdown("##### ✨ 추천 오늘의 루틴")
        st.success(f"✔️ [{todays_pick}]")
        st.markdown("##### 👇 저녁 루틴 (선택)")

        tab1, tab2, tab3, tab4 = st.tabs(
            ["A. 리들샷", "B. 기기흡수", "C. 초음파모드", "D. 레티날"]
        )

        with tab1:
            show_routine_box(
                "저녁",
                "리들샷 데이",
                [
                    "순한 세안 후 물기 완전히 닦기",
                    "VT 리들샷 300 (부드럽게 눌러 흡수)",
                    "마데카크림 또는 시카플라스트 밤 (보습/장벽 마무리)",
                    "🚨 레티날·LHA·BHA·효소세안·멜라토닝크림은 오늘 쉬기",
                ],
            )

        with tab2:
            show_routine_box(
                "저녁",
                "기기 흡수모드",
                [
                    "더랩 토너 (수분 공급)",
                    "매트릭실 (탄력 케어)",
                    "나이아신아마이드 (피지/피부톤 케어)",
                    "마데카 프라임 (부스트샷젤 + 흡수모드)",
                    "일리윤 크림 (보습 마무리)",
                ],
            )

        with tab3:
            show_routine_box(
                "저녁",
                "초음파모드",
                [
                    "🍋 셀리맥스 잡티 미백 마스크팩",
                    "마데카 프라임 (팩 위에서 초음파모드)",
                    "마데카크림 (보습/재생 마무리)",
                ],
            )

        with tab4:
            show_routine_box(
                "저녁",
                "레티날 데이",
                [
                    "순한 세안",
                    "더랩 토너 (수분 공급)",
                    "더마팩토리 레티날 시카 앰플 (얼굴 전체에 얇게)",
                    "일리윤 크림 또는 마데카크림 (보습/장벽 마무리)",
                    "🚨 리들샷·LHA·BHA·효소세안 등 자극성 케어는 오늘 쉬기",
                    "☀️ 다음 날 선크림 필수",
                ],
            )

        st.write("")
        st.success(
            """
**🗓️ [황금기 8일 밀착 스케줄]**

* **Day 1:** 🅰️ 리들샷
* **Day 2:** 🅱️ 흡수모드
* **Day 3:** 🅳 레티날
* **Day 4:** 🅱️ 흡수모드
* **Day 5:** 🅲 초음파모드
* **Day 6:** 🅱️ 흡수모드
* **Day 7:** 🅳 레티날
* **Day 8:** 💆‍♀️ 미백 마스크팩 단독

💡 따갑거나 붉어지거나 각질이 올라오면 리들샷·레티날 대신
수분 + 보습 루틴으로 변경!
            """
        )

    # 🥚 3단계: 배란기 (Day 14~17)
    elif phase2_end < day <= phase3_end:
        p3_day = day - phase2_end
        p3_schedule = {
            1: "🧼 효소파우더",
            2: "💧 데일리 수분",
            3: "🌿 클레이 모공팩",
            4: "💧 데일리 수분",
        }
        todays_pick = p3_schedule.get(p3_day, "💧 데일리 수분")

        st.markdown(
            f"#### 🥚 3단계: 배란기 "
            f"(주기 {day}일차 - 모공 & 피지 관리)"
        )
        st.caption(
            "🧹 피지가 신경 쓰이기 시작하면 모공 관리를 가볍게! "
            "효소세안과 클레이팩 사이에는 수분 루틴으로 쉬어가기."
        )

        show_routine_box(
            "아침",
            "피지/다크닝 방어",
            [
                "AHC 위치하젤 토너 (나비존 중심)",
                "나이아신아마이드 + 알파 아르부틴 (피부톤/잡티 케어 💡)",
                "구달 청귤 아이크림 (눈가 케어 🍊)",
                "수분 크림 (얇게 보습)",
                "선크림 (자외선 차단 필수 🛡️)",
            ],
        )

        st.markdown("##### ✨ 추천 오늘의 루틴")
        st.success(f"✔️ [{todays_pick}]")
        st.markdown("##### 👇 저녁 루틴 (피부 상태에 따라 선택)")
        tab1, tab2, tab3 = st.tabs(
            ["A. 효소파우더", "B. 데일리 수분", "C. 클레이 모공팩"]
        )

        with tab1:
            show_routine_box(
                "저녁",
                "효소 세안 데이",
                [
                    "수이사이 효소 파우더 워시 (각질/피지 세정)",
                    "더랩 토너 (수분 공급)",
                    "매트릭실 (탄력 케어)",
                    "수분 크림 (보습 마무리)",
                    "🚨 리들샷·레티날·애크린겔 등 자극성 케어는 오늘 쉬기",
                ],
            )

        with tab2:
            show_routine_box(
                "저녁",
                "데일리 수분 진정",
                [
                    "순한 폼 클렌징",
                    "더랩 토너 (수분 공급)",
                    "매트릭실 (탄력 케어)",
                    "나이아신아마이드 + 알파 아르부틴 (피부톤/잡티 케어 ✨)",
                    "수분 크림 (보습 마무리)",
                ],
            )

        with tab3:
            show_routine_box(
                "저녁",
                "클레이 모공팩 데이",
                [
                    "순한 폼 클렌징 후 물기 닦기",
                    "클레이 모공팩 (피지 많은 T존/나비존 중심)",
                    "제품 권장시간 사용 후 씻어내기",
                    "더랩 토너 (수분 공급)",
                    "수분 크림 (보습 마무리)",
                    "🚨 효소세안·리들샷·레티날·애크린겔은 오늘 쉬기",
                ],
            )

        st.write("")
        st.success(
            """
**🗓️ [배란기 4일 모공 관리 스케줄]**

* **Day 1:** 🧼 효소파우더
* **Day 2:** 💧 데일리 수분
* **Day 3:** 🌿 클레이 모공팩
* **Day 4:** 💧 데일리 수분

💡 피부가 건조하거나 따가운 날에는 예정된 효소·클레이 대신
데일리 수분 루틴으로 변경!
            """
        )

    # 🌋 4단계: 황체기 (Day 18~29)
    elif phase3_end < day <= CYCLE_LENGTH:
        p4_day = day - phase3_end
        p4_schedule = {
            1: "🌿 데일리 진정",
            2: "🧫 애크린겔",
            3: "🌿 데일리 진정",
            4: "🌿 데일리 진정",
            5: "🌿 데일리 진정",
            6: "🧫 애크린겔",
            7: "🌿 데일리 진정",
            8: "🌿 데일리 진정",
            9: "🌿 데일리 진정",
            10: "🧫 애크린겔",
            11: "🌿 데일리 진정",
            12: "🌿 데일리 진정",
        }
        todays_pick = p4_schedule.get(p4_day, "🌿 데일리 진정")

        st.markdown(
            f"#### 🌋 4단계: 생리 전 황체기 "
            f"(주기 {day}일차 - 피지 & 트러블 관리)"
        )
        st.caption(
            "🌋 피지·요철이 신경 쓰이기 쉬운 시기. 피부가 평온하면 "
            "진정 루틴으로 쉬고, 필요할 때만 애크린겔로 대응하기!"
        )

        show_routine_box(
            "아침",
            "데일리 피지 방어",
            [
                "AHC 위치하젤 토너 (나비존 중심)",
                "나이아신아마이드 + 알파 아르부틴 (피지/피부톤 케어 💡)",
                "구달 청귤 아이크림 (눈가 케어)",
                "수분 크림 (얇게 보습)",
                "선크림 (자외선 차단 필수 🛡️)",
            ],
        )

        st.markdown("##### ✨ 추천 오늘의 루틴")
        st.success(f"✔️ [{todays_pick}]")
        st.markdown("##### 👇 저녁 루틴 (피부 상태에 따라 선택)")

        tab1, tab2 = st.tabs(["A. 데일리 진정", "B. 애크린겔"])

        with tab1:
            show_routine_box(
                "저녁",
                "데일리 수분 진정",
                [
                    "순한 폼 클렌징",
                    "더랩 토너 (수분 공급)",
                    "매트릭실 (탄력 케어)",
                    "나이아신아마이드 + 알파 아르부틴 (피부톤/잡티 케어)",
                    "수분 크림 (보습 마무리)",
                ],
            )
            st.caption("💡 피부가 평온한 날은 기본 루틴으로 쉬어가기.")

        with tab2:
            show_routine_box(
                "저녁",
                "애크린겔 데이",
                [
                    "순한 폼 클렌징",
                    "더랩 토너 (자극 없다면 가볍게)",
                    "애크린겔 (요철/피지가 고민되는 부위에 얇게)",
                    "일리윤 크림 또는 시카플라스트 밤 (보습 마무리)",
                    "🚨 효소세안·클레이팩·리들샷·레티날은 오늘 쉬기",
                    "☀️ 다음 날 선크림 꼼꼼하게",
                ],
            )
            st.caption("💡 요철이나 막힌 모공이 신경 쓰이는 날에만 부분 사용.")

        st.write("")
        st.success(
            """
**🗓️ [황체기 12일 스케줄]**

* **Day 1:** 🌿 데일리 진정
* **Day 2:** 🧫 애크린겔
* **Day 3:** 🌿 데일리 진정
* **Day 4:** 🌿 데일리 진정
* **Day 5:** 🌿 데일리 진정
* **Day 6:** 🧫 애크린겔
* **Day 7:** 🌿 데일리 진정
* **Day 8:** 🌿 데일리 진정
* **Day 9:** 🌿 데일리 진정
* **Day 10:** 🧫 애크린겔
* **Day 11:** 🌿 데일리 진정
* **Day 12:** 🌿 데일리 진정

💡 피부가 따갑거나 붉어지면 예정된 액티브 대신 수분·보습 루틴으로 변경!
            """
        )

    else:
        st.error("주기 일차는 1일부터 29일 사이여야 해.")


# --- 4. 사용자 선택 및 사이드바 ---
with st.sidebar:
    st.header("⚙️ 뷰티 설정")
    selected_user = st.radio(
        "사용자를 선택해줘!",
        USERS,
        horizontal=True,
        key="selected_user",
    )

    saved_date = load_user_data(selected_user)
    current_day = calculate_cycle_day(saved_date)

    st.divider()
    st.subheader(f"👤 {selected_user}")
    st.write(f"📅 마지막 생리 시작일: `{saved_date}`")

    new_date = st.date_input(
        "마지막 생리 시작일 변경",
        value=datetime.datetime.strptime(saved_date, "%Y-%m-%d").date(),
        key=f"cycle_start_{selected_user}",
    )

    if st.button("날짜 저장하기", use_container_width=True):
        storage = save_user_data(selected_user, new_date.isoformat())
        if storage == "google_sheets":
            st.success(f"{selected_user}의 날짜를 Google Sheets에 저장했어!")
        else:
            st.success(f"{selected_user}의 날짜를 이 컴퓨터에 저장했어!")
            st.caption(
                "ℹ️ 현재 Google Sheet가 공개 읽기 전용이라 로컬 저장소를 사용했어."
            )
        st.rerun()

    st.divider()
    if current_day is not None:
        st.markdown(f"#### 🩸 오늘은 Day {current_day}")
        sidebar_progress = current_day / CYCLE_LENGTH
        st.progress(
            sidebar_progress,
            text=(
                f"{current_day}일차 / {CYCLE_LENGTH}일 주기 "
                f"({int(sidebar_progress * 100)}%)"
            ),
        )
    else:
        st.error("저장된 날짜 형식에 문제가 있어.")


# --- 5. 메인 화면 ---
st.caption(f"현재 선택: {selected_user} · {CYCLE_LENGTH}일 고정 주기")
if current_day is not None:
    display_hormone_guide(current_day)
else:
    st.error("저장된 날짜 형식에 문제가 있어. 날짜를 다시 선택해 저장해줘!")
