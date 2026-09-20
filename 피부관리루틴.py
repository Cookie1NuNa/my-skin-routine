import streamlit as st

from streamlit_gsheets import GSheetsConnection

import pandas as pd

import datetime





# --- 1. 구글 시트 및 데이터 기본 설정 ---

conn = st.connection("gsheets", type=GSheetsConnection)

CYCLE_LENGTH = 29
USERS = ["꼬밍", "봉이"]



def load_user_data(name):

    try:

        df = conn.read(ttl=0)

        user_row = df[df["name"] == name]

        if not user_row.empty:

            return pd.to_datetime(user_row.iloc[0]["date"]).date().isoformat()

    except (KeyError, TypeError, ValueError):

        pass

    return str(datetime.date.today()) 



def save_user_data(name, date_str):

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

        new_row = pd.DataFrame([{"name": name, "date": date_str, "cycle": CYCLE_LENGTH}])

        df = pd.concat([df, new_row], ignore_index=True)

    conn.update(data=df)

    st.cache_data.clear()



# 주기는 두 사용자 모두 29일로 고정

def calculate_cycle_day(start_date_str):

    try:

        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()

        today = datetime.date.today()

        delta = today - start_date

        return (delta.days % CYCLE_LENGTH) + 1

    except:

        return None



# --- 2. 루틴 박스 세로 정렬 디자인 ---

def show_routine_box(time, title, items):

    if time == "아침":

        st.success(f"**☀️ 아침: {title}**")

    elif time == "저녁":

        st.info(f"**🌙 저녁: {title}**")

    elif time == "스페셜":

        st.warning(f"**🌋 스페셜: {title}**")



    # 리스트로 받은 화장품을 세로로 하나씩 출력

    for item in items:

        st.markdown(f"▪️ {item}")



# --- 3. ⭐️ 내 몸 주식회사 가이드 ---

def display_hormone_guide(day):

    progress_val = min(day / CYCLE_LENGTH, 1.0)

    st.progress(
        progress_val,
        text=f"현재 {day}일차 / {CYCLE_LENGTH}일 주기 ({int(progress_val * 100)}%) 진행 중",
    )



    st.markdown(f"""

        <h3 style='text-align: center; margin-bottom: -10px;'>🥚 내 피부 깐달걀 프로젝트: Day {day}</h3>

        <hr style='margin-top: 15px; margin-bottom: 20px;'>

        """, unsafe_allow_html=True)



    # 29일 고정 구간

    phase1_end = 5

    phase2_end = 13

    phase3_end = 17





    # 🌟 생리 주기 if/elif 시작하기 바로 위쪽에 넣기!



    st.divider() # ➖ 깔끔하게 가로선 하나 딱 그어주기!





    # 🩸 1단계: 생리 중 (Day 1~5)

    if 1 <= day <= phase1_end:

        st.markdown("#### 🩸 1단계: 생리 중 (피부 휴식 & 수분 올인!)")

        st.caption("🚨 피부 장벽이 제일 약하고 민감한 시기. 무조건 자극을 줄이고 푹 쉬게 해줘야 해! (기기, 리들샷, 효소, 바하 전부 ❌)")



        col1, col2 = st.columns(2)

        with col1:

            show_routine_box("아침", "🫗수분 방어& 순한 탄력", [

                "라로슈포제 토너 (장벽/진정 베이스 튼튼하게 깔기)",

                "매트릭실 (탄력 베이스 - 절대 문지르지 말고 톡톡 두드려 흡수! ✋)",

                "구달 아이크림 (다크서클 집중 케어 - 평소보다 듬뿍! 🍊)",

                "+ 보르피린 ( 딱 1방울! 아이크림 믹싱💉)",

                "에스트라 크림 (보습막코팅)",

                "선크림 (비타민C-> 자외선 차단 필수!!)"

            ])

        with col2:

            show_routine_box("저녁", "🌙 장벽 진정 & 국소 볼륨", [

                "더랩 토너 (수분 여러 번 촵촵 💧)",

                "히알루로닉 앰플 (수분/진정)",

                "보르피린 크림 믹싱 (눈밑/팔자 딱 1방울! 💉)",

                "라로슈포제 시카플라스트 밤 (장벽 진정 듬뿍 덮기)"

            ])



        st.write("") # 살짝 여백 주기

        st.success("""

        **⚠️ 보르피린 주의사항**

        * **💧 단독보다는 '믹스'해서 한 방울만!:**욕심내서 단독으로 듬뿍 얹으면 모공이 숨을 못 쉬어서 트러블 날수있음

        * **🎯 무조건 푹 꺼져서 볼륨이 필요한 눈 밑 다크서클, 팔자주름, 목주름 같은 곳에만 타겟팅해서 발라야 해.

        * **✋ '문질문질' 금지, 무조건 '톡톡톡' : **슥슥 문지르면 얇은 피부에 마찰이 생겨서 오히려 잔주름이 더 짙어질 수 있음

        * **🧴 보르피린 사용기간:**최소 2~3개월 꾸준한 사용; 단기간에 즉각적인 효과가 나타나는 성분이 아님다.

        * **🚨 비립종 주의보 (눈가 경계령) :**눈가에 오돌토돌한 하얀 알갱이(비립종)가 조금이라도 보인다면, 그 부위는 당장 사용을 며칠 멈추고 푹 쉬게 해줘야 해!

        """)





    # ✨ 2단계 (황금기): Day 6 ~ 13

    elif phase1_end < day <= phase2_end:

        # 👇 1. 오늘이 황금기 8일 중 며칠 차인지 계산 (1~8일)

        p2_day = day - phase1_end  



        # 8일치 밀착 스케줄 딕셔너리

        p2_schedule = {

            1: "🅰️ 리들샷 데이", 2: "🅱️ 기기 흡수 모드", 3: "🅲 초음파 스페셜",

            4: "🅰️ 리들샷 데이", 5: "🅱️ 기기 흡수 모드", 

            6: "💆‍♀️ 미백 마스크팩 단독 (🚨기기 쉬는 날!)", 

            7: "🅱️ 기기 흡수 모드", 8: "🅲 초음파 스페셜 (황금기 피날레! ✨)"

        }

        todays_pick = p2_schedule.get(p2_day, "🅱️ 기기 흡수 모드")



        st.markdown(f"#### ✨ 2단계: 황금기 (주기 {day}일차 - 영양 흡수 200%!)")

        st.caption("🏆 피부 재생력 만렙 구간! 리들샷과 기기를 적극 활용해서 광채 피부 만들기!")



        show_routine_box("아침", "미백 광채 집중 ✨", [

            "아로마티카 에센스 (항산화/결 정돈)",

            "나이아신아마이드 + 알파 아르부틴 (잡티 싹! 전체 톤업 💡)",

            "구달 청귤 아이크림 (눈가 다크서클 환하게 톡톡 🍊)",

            "에스트라 크림 (수분 코팅)",

            "선크림 (무조건 듬뿍! 자외선 철벽 방어 🛡️)"

        ])





        st.markdown("##### ✨추천 오늘의루틴")

        st.success(f"✔️ [{todays_pick}]**")



        st.markdown("##### 👇 저녁 루틴 (선택)")

        tab1, tab2, tab3 = st.tabs(["A. 리들샷 데이", "B. 기기 흡수", "C. 초음파 스페셜"])



        with tab1:

            show_routine_box("저녁", "리들샷 (길 뚫기)", [

                "비플레인 LHA 토너 (순한 각질/닦토)",

                "VT 리들샷 300 (턴오버/길 뚫기)",

                "알파 아르부틴 (잡티/미백 집중)",

                "마데카크림 타임리버스 (재생/속탄력)"

            ])

        with tab2:

            show_routine_box("저녁", "기기 흡수 모드", [

                "더랩 토너 (속건조 방어)",

                "매트릭실 (전체 탄력)",

                "나이아신아마이드 (피지/미백)",

                "마데카 프라임 (부스트샷젤 +흡수모드)",

                "에스트라 크림 (보습 코팅)"

            ])

        with tab3:

            show_routine_box("저녁", "초음파 스페셜", [

                "셀리맥스 잡티 미백 마스크팩 (황금기 미백 끌올! ⚡)",

                "마데카 프라임 (팩 위에서 초음파 모드!)",

                "보르피린 크림믹싱 (눈밑/팔자 콕콕)",

                "마데카크림 (재생 마무리)"

            ])



        st.write("")

        st.success("""

        **🗓️ [황금기 8일 밀착 스케줄] **



        * **Day 1 [스타트] :** 🅰️ 리들샷 데이 (막힌 모공 뻥 뚫어주기)

        * **Day 2 [영양팍팍]:** 🅱️ 기기 흡수 모드 (뚫린 길로 앰플 쫙쫙!)

        * **Day 3 [치트키] :** 🅲 초음파 스페셜 (팩 + 기기로 미백/탄력 극대화)

        * **Day 4 [길뚫기] :** 🅰️ 리들샷 데이 (한 번 더 고속도로 개통!)

        * **Day 5 [영양팍팍]:** 🅱️ 기기 흡수 모드

        * **Day 6 [진정휴식]:** 💆‍♀️ 미백 마스크팩 단독 (기기 마찰 없이 영양만 흡수)

        * **Day 7 [영양팍팍]:** 🅱️ 기기 흡수 모드

        * **Day 8 [피날레] :** 🅲 초음파 스페셜 (황금기 마무리! 최상의 컨디션 완성 🏆)

        """)





    # 🥚 3단계: 배란기 (Day 14~17)

    elif phase2_end < day <= phase3_end:

        st.markdown("#### 🥚 3단계: 배란기 (모공 청소 & 피지 조절)")

        st.caption("🧹 슬슬 피지량이 늘어나기 시작하는 타이밍! 모공이 막히지 않게 새로 산 효소 파우더로 부드럽게 청소해 줄 때야.")





        show_routine_box("아침", "피지/다크닝 방어", [

                "AHC 위치하젤 토너 (나비존 닦토/피지조절)",

                "나이아신아마이드 + 알파 아르부틴 (비타민C 대체! 피지/미백 콤보 💡)",

                "구달 청귤 아이크림 (눈가 다크서클/잡티 케어 🍊)",

                "에스트라 크림 (평소보다 얇게 보습막)",

                "선크림 (자외선 필수 🛡️)"

            ])



        st.markdown("##### 👇 저녁 루틴 (선택)")

        tab1, tab2 = st.tabs(["A. 효소파우더(1회)", "B. 데일리 수분"])  





        with tab1:

            show_routine_box("저녁", "효소 세안 데이", [

                "수이사이 효소 파우더 워시 (묵은 각질/피지 딥클렌징 🧼)",

                "AHC 위치하젤 토너 (모공 수렴 닦토)",

                "히알루로닉 앰플 (수분 꽉꽉 채우기 필수! 💧)",

                "나이아신아마이드 (피지 조절)",

                "매트릭실 (탄력 충전)",

                "에스트라 크림 (마무리 보습)"

            ])



        with tab2:

            show_routine_box("저녁", "데일리 수분 진정", [

                "순한 폼 클렌징 (자극 없는 가벼운 세안 🧼)",

                "더랩 토너 (수분 길 열어주기 촵촵)",

                "히알루로닉 앰플 & 매트릭실 (수분 탄력 콤보)",

                "나이아신아마이드 + 알파 아르부틴 (잡티 방어 ✨)",

                "에스트라 크림 (보습 코팅)"

            ])







   # 🌋 4단계 (황체기): Day 18 ~ 29 (12일)

    elif phase3_end < day <= CYCLE_LENGTH:

        # 👇 오늘이 4단계 12일 중 며칠 차인지 계산

        p4_day = day - phase3_end  



        # 29일 주기에 맞춘 12일치 스케줄 딕셔너리

        p4_schedule = {

            1: "🧫 애크린겔(주2회)", 2: "🌿 데일리 진정", 3: "🧼 효소세안(주1-2회)",

            4: "🌿 데일리 진정", 5: "🧫 애크린겔(주2회)", 6: "🌿 데일리 진정",

            7: "🌿 녹두클레이(주1회)", 8: "🌿 데일리 진정", 9: "🧫 애크린겔(주2회)",

            10: "🌿 데일리 진정", 11: "🌿 데일리 진정", 12: "🌿 데일리 진정"

        }

        todays_pick = p4_schedule.get(p4_day, "🌿 데일리 진정")



        st.markdown(f"#### 🌋 4단계: 생리 전 황체기 (주기 {day}일차 - 요철 & 트러블 비상!)")

        st.caption("🚨 피지가 폭발하는 시기! '애크린겔'과 '녹두팩'으로 신부 피부 완벽 사수!")





        # 아침 루틴 (고정: 번들거림 & 다크닝 방어)

        show_routine_box("아침", "☀️ 데일리 피지 방어", [

            "AHC 위치하젤 토너 (나비존 닦토)",

            "나이아신아마이드 + 알파 아르부틴 (피지 조절 & 다크닝 방어 💡)",

            "구달 청귤 아이크림 (눈가 다크서클 케어)",

            "에스트라 크림 (아주 얇게만!)",

            "선크림 (무조건 필수 🛡️)"

        ])



        st.markdown("##### ✨추천 오늘의루틴")

        st.success(f"✔️ [{todays_pick}]**")





        st.markdown("##### 👇 저녁 루틴 (피부 상태에 따라 선택)")

        tab1, tab2, tab3 = st.tabs(["🌿 데일리 진정", "🧫 애크린겔 데이(주2회)", "🧼 딥클렌징&팩 데이"])



        with tab1:

            show_routine_box("저녁", "데일리 수분 진정", [

                "순한 폼 클렌징 (자극 최소화 🧼)",

                "더랩 토너 (수분 촵촵)",

                "히알루로닉 앰플 & 매트릭실 (수분 탄력 콤보)",

                "나이아신아마이드 (피지 조절)",

                "에스트라 크림 (얇게 보습 마무리)"

            ])

            st.caption("💡 피부가 딱히 뒤집어지지 않고 평온할 때 하는 기본 루틴이야.")



        with tab2:

            show_routine_box("저녁", "요철/피지 집중 관리", [

                "순한 폼 클렌징 (🚨효소 파우더 금지!)",

                "애크린겔 (나비존 요철 부위에만 쌀알만큼 톡톡! 🧫)",

                "히알루로닉 앰플 레어링 (바하 바른 후 수분 듬뿍! 필수 💧)",

                "매트릭실 (탄력 충전)",

                "토리든 수분 파스크팩",

                "시카플라스트 밤 (자극받은 부위 위주로 마무리)"

            ])

            st.caption("🚨 주의: 애크린겔 바른 날은 절대 문지르지 말고, 다음 날 아침 폼 세안 필수!")



        with tab3:

            show_routine_box("저녁", "모공 딥클렌징 & 진정", [

                "수이사이 효소 파우더 워시 (묵은 각질 정리 🧼)",

                "녹두 모델링팩 (피지 흡착 & 쿨링 진정 🌿)",

                "히알루로닉 앰플 (팩 떼어낸 후 듬뿍!)",

                "나이아신아마이드 (모공 쫀쫀하게 잡기)",

                "에스트라 크림 (마무리)"

            ])

            st.caption("💡 나비존이 유독 번들거리고 모공이 답답해 보일 때 추천!")



        # 4단계 핵심 주의사항 펼쳐두기

        st.warning("""

        **⚠️ 주의사항**

        * **💉 보르피린 주의:** 유분이 제일 많은 시기니까, 눈가/팔자에 바를 때 평소보다 반 방울만! 비립종 기미 보이면 바로 쉬어가기.

        * **🚫 자극 금지:** 리들샷이나 마데카 프라임 기기는 피부가 예민하다면 잠시 쉬어줘도 좋아. (황금기에 몰빵하자!)

        * **💧 보습 듬뿍 & 진정 팩 필수 : **건조함주의

        """)



        st.write("")

        st.success("""

        **🗓️ [황체기 12일 생존 스케줄] 이중 자극 멈춰! 고민 없이 따라 하기 🛡️**



        * **Day 1 [요철타파] :** 🧫 애크린겔 데이 (4단계 진입! 요철 방어 시작)

        * **Day 2 [수분휴식] :** 🌿 데일리 진정 (수분 듬뿍 휴식)

        * **Day 3 [각질싹쓸] :** 🧼 효소 세안 데이 (묵은 각질 시원하게 청소)

        * **Day 4 [수분휴식] :** 🌿 데일리 진정 (평화롭게 수분 충전)

        * **Day 5 [요철타파] :** 🧫 애크린겔 데이 (요철 한 번 더 꾹 눌러주기)

        * **Day 6 [수분휴식] :** 🌿 데일리 진정 (장벽 지키기)

        * **Day 7 [모공청소] :** 🌿 녹두 클레이 데이 (피지 분비 최고조! 모공 쏙 빼고 쿨링)

        * **Day 8 [수분휴식] :** 🌿 데일리 진정 (팩 했으니 수분 촵촵)

        * **Day 9 [요철타파] :** 🧫 애크린겔 데이 (생리 직전 트러블 기미 철벽 방어!)

        * **Day 10 [수분휴식] :** 🌿 데일리 진정 (피부 장벽을 편안하게 진정)

        * **Day 11 [수분휴식] :** 🌿 데일리 진정 (자극 없이 수분과 보습에 집중)

        * **Day 12 [마무리]  :** 🌿 데일리 진정 (내일이면 1단계! 튼튼한 보습으로 마무리)

        """)


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
        save_user_data(selected_user, new_date.isoformat())
        st.success(f"{selected_user}의 날짜를 저장했어!")
        st.rerun()

    st.divider()
    st.markdown(f"#### 🩸 오늘은 Day {current_day}")
    sidebar_progress = current_day / CYCLE_LENGTH
    st.progress(
        sidebar_progress,
        text=f"{current_day}일차 / {CYCLE_LENGTH}일 주기 ({int(sidebar_progress * 100)}%)",
    )


# --- 5. 메인 화면 ---
st.caption(f"현재 선택: {selected_user} · 29일 고정 주기")
if current_day:
    display_hormone_guide(current_day)
else:
    st.error("저장된 날짜 형식에 문제가 있어. 날짜를 다시 선택해 저장해줘!")


