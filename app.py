import random
import streamlit as st

st.set_page_config(page_title="IRON FIST ARENA", page_icon="🥊", layout="centered")

# ---------------------------------------------------------
# (1) 데이터 구조 (리스트): 캐릭터 및 기술 목록
# ---------------------------------------------------------
characters = [
    "🥋 진 (가라테)",
    "⚡ 카즈야 (풍신류)",
    "🐆 킹 (프로레슬링)",
    "🦊 화랑 (태권도)",
]

skills = [
    "👊 초풍신권 (타격)",
    "🛡️ 철벽 가드 (방어)",
    "🤼 자이언트 스윙 (잡기)",
    "🔥 레이지 아츠 (필살기·HP 35 이하 각성)",
]


# ---------------------------------------------------------
# (2) 함수 (def) & (3) 조건문 (if-elif-else): 기술 충돌 판정 로직
# ---------------------------------------------------------
def judge_clash(p1_skill, p2_skill, p1_hp, p2_hp):
    s1 = p1_skill.split("(")[1].split(")")[0]
    s2 = p2_skill.split("(")[1].split(")")[0]

    p1_dmg, p2_dmg = 0, 0
    p1_heal, p2_heal = 0, 0

    # 1) 필살기(레이지 아츠)가 포함된 경우
    if "필살기" in s1 or "필살기" in s2:
        if "필살기" in s1 and "필살기" in s2:
            p2_dmg = 35 if p1_hp <= 35 else 10
            p1_dmg = 35 if p2_hp <= 35 else 10
            msg = "💥 양쪽 레이지 아츠 정면 충돌! 엄청난 충격파가 발생했습니다!"
        elif "필살기" in s1:
            if s2 == "방어":
                p2_dmg = 10
                msg = "🛡️ 2P가 철벽 가드로 1P의 레이지 아츠를 막아냈습니다! (10 데미지)"
            elif p1_hp <= 35:
                p2_dmg = 45
                msg = "🔥 [RAGE ART!] 1P의 체력 35 이하 각성 필살기 작렬! (45 데미지)"
            else:
                p1_dmg = 20
                msg = "⚠️ 1P의 레이지 미발동(HP 35 초과)! 빈틈을 노린 2P의 반격! (1P 20 피해)"
        else:
            if s1 == "방어":
                p1_dmg = 10
                msg = "🛡️ 1P가 철벽 가드로 2P의 레이지 아츠를 막아냈습니다! (10 데미지)"
            elif p2_hp <= 35:
                p1_dmg = 45
                msg = "🔥 [RAGE ART!] 2P의 체력 35 이하 각성 필살기 작렬! (45 데미지)"
            else:
                p2_dmg = 20
                msg = "⚠️ 2P의 레이지 미발동(HP 35 초과)! 빈틈을 노린 1P의 반격! (2P 20 피해)"
        return p1_dmg, p2_dmg, p1_heal, p2_heal, msg

    # 2) 기본 삼각 상성 판정 (타격 > 잡기 > 방어 > 타격)
    if s1 == s2:
        if s1 == "방어":
            msg = "👀 서로 가드를 올린 채 거리를 잽니다. (피해 없음)"
        else:
            p1_dmg, p2_dmg = 15, 15
            msg = f"⚔️ 같은 {s1} 기술이 부딪혀 크로스 카운터 발생! (서로 15 데미지)"
    elif s1 == "타격" and s2 == "잡기":
        p2_dmg = 25
        msg = "👊 1P의 타격이 2P의 잡기를 카운터쳤습니다! (2P 25 데미지)"
    elif s1 == "잡기" and s2 == "방어":
        p2_dmg = 25
        msg = "🤼 1P의 잡기가 2P의 가드를 뚫고 메다꽂았습니다! (2P 25 데미지)"
    elif s1 == "방어" and s2 == "타격":
        p2_dmg = 15
        p1_heal = 5
        msg = "🛡️ 1P가 타격을 완벽히 가드하고 반격했습니다! (2P 15 데미지 / 1P +5 회복)"
    elif s2 == "타격" and s1 == "잡기":
        p1_dmg = 25
        msg = "👊 2P의 타격이 1P의 잡기를 카운터쳤습니다! (1P 25 데미지)"
    elif s2 == "잡기" and s1 == "방어":
        p1_dmg = 25
        msg = "🤼 2P의 잡기가 1P의 가드를 뚫고 메다꽂았습니다! (1P 25 데미지)"
    else:  # s2 == "방어" and s1 == "타격"
        p1_dmg = 15
        p2_heal = 5
        msg = "🛡️ 2P가 타격을 완벽히 가드하고 반격했습니다! (1P 15 데미지 / 2P +5 회복)"

    return p1_dmg, p2_dmg, p1_heal, p2_heal, msg


# 온라인 친구 대전용 공용 방 저장소 (서버 메모리 공유)
@st.cache_resource
def get_online_rooms():
    return {}


rooms = get_online_rooms()

# AI 대전(개인 세션) 상태 초기화
if "ai_state" not in st.session_state:
    st.session_state.ai_state = {
        "p1_char": characters[0],
        "p2_char": characters[1],
        "p1_hp": 100,
        "p2_hp": 100,
        "round": 1,
        "round_logs": [],
        "last_msg": "상성: 👊 타격 > 🤼 잡기 > 🛡️ 가드 > 👊 타격 (HP 35 이하 시 🔥 필살기 각성!)",
        "game_over": False,
    }

# 상단 타이틀
st.title("🥊 IRON FIST ARENA")
st.caption("👊 타격 > 🤼 잡기 > 🛡️ 가드 > 👊 타격 | 체력 35 이하 시 🔥 레이지 아츠 각성!")

# 대전 모드 선택
mode = st.radio(
    "대전 모드를 선택하세요",
    ["🤖 AI 대전 (1인용)", "🌐 온라인 친구 대전 (방 코드 접속)"],
    horizontal=True,
)
st.divider()

# =========================================================
# 모드 A: AI 대전 (1인용)
# =========================================================
if mode == "🤖 AI 대전 (1인용)":
    state = st.session_state.ai_state

    c1, c2 = st.columns(2)
    with c1:
        state["p1_char"] = st.selectbox(
            "1P (나) 캐릭터", characters, index=characters.index(state["p1_char"]), disabled=(state["round"] > 1)
        )
    with c2:
        state["p2_char"] = st.selectbox(
            "2P (AI 상대) 캐릭터", characters, index=characters.index(state["p2_char"]), disabled=(state["round"] > 1)
        )

    my_skill = st.selectbox("사용할 기술 선택", skills, key="ai_skill_select")

    if st.button("⚔️ 기술 확정 및 라운드 진행!", type="primary", use_container_width=True, disabled=state["game_over"]):
        # AI 기술 선택 (AI 체력이 35 이하면 필살기도 후보에 포함)
        ai_candidates = skills if state["p2_hp"] <= 35 else skills[:3]
        ai_skill = random.choice(ai_candidates)

        p1_dmg, p2_dmg, p1_heal, p2_heal, msg = judge_clash(
            my_skill, ai_skill, state["p1_hp"], state["p2_hp"]
        )

        state["p1_hp"] = min(100, max(0, state["p1_hp"] - p1_dmg + p1_heal))
        state["p2_hp"] = min(100, max(0, state["p2_hp"] - p2_dmg + p2_heal))
        state["last_msg"] = f"[{state['round']}R] {msg}"

        state["round_logs"].append(
            {
                "라운드": f"{state['round']}R",
                "1P(나) 기술": my_skill.split(" ")[1],
                "2P(AI) 기술": ai_skill.split(" ")[1],
                "1P 피해": f"-{p1_dmg}" + (f" (+{p1_heal})" if p1_heal else ""),
                "2P 피해": f"-{p2_dmg}" + (f" (+{p2_heal})" if p2_heal else ""),
                "판정 결과": msg,
            }
        )
        state["round"] += 1

        if state["p1_hp"] == 0 or state["p2_hp"] == 0:
            state["game_over"] = True
        st.rerun()

    st.divider()
    st.info(state["last_msg"])

    hp1, hp2 = st.columns(2)
    with hp1:
        st.metric(f"1P {state['p1_char']}", f"{state['p1_hp']} / 100 HP")
        st.progress(state["p1_hp"] / 100)
    with hp2:
        st.metric(f"2P {state['p2_char']}", f"{state['p2_hp']} / 100 HP")
        st.progress(state["p2_hp"] / 100)

    if state["game_over"]:
        if state["p1_hp"] > state["p2_hp"]:
            st.success(f"🏆 K.O.! {state['p1_char']} 승리!")
            st.balloons()
        elif state["p2_hp"] > state["p1_hp"]:
            st.error(f"💀 K.O.! {state['p2_char']}에게 패배했습니다.")
        else:
            st.warning("🤝 DOUBLE K.O.! 무승부입니다!")

        if st.button("🔄 새 경기 시작하기", use_container_width=True):
            st.session_state.ai_state = {
                "p1_char": state["p1_char"],
                "p2_char": state["p2_char"],
                "p1_hp": 100,
                "p2_hp": 100,
                "round": 1,
                "round_logs": [],
                "last_msg": "새 경기가 시작되었습니다! 기술을 선택하세요.",
                "game_over": False,
            }
            st.rerun()

    # (4) 반복문 (for)을 이용한 전투 기록 테이블 출력
    if len(state["round_logs"]) > 0:
        st.subheader("📜 라운드별 기술 충돌 기록")
        table_rows = []
        for log in state["round_logs"]:
            table_rows.append(log)
        st.table(table_rows)

# =========================================================
# 모드 B: 온라인 친구 대전 (방 코드 접속)
# =========================================================
else:
    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        room_code = st.text_input("방 코드 입력 (친구와 똑같은 숫자/단어 입력)", value="7777")
    with r_col2:
        role = st.selectbox("내 역할", ["1P (방장)", "2P (도전자)"])

    if room_code not in rooms:
        rooms[room_code] = {
            "p1_char": characters[0],
            "p2_char": characters[2],
            "p1_hp": 100,
            "p2_hp": 100,
            "round": 1,
            "p1_move": None,
            "p2_move": None,
            "round_logs": [],
            "last_msg": f"[{room_code}] 방에 입장했습니다! 각자 기술을 고르고 [기술 확정]을 누르세요.",
            "game_over": False,
        }

    room = rooms[room_code]

    c1, c2 = st.columns(2)
    with c1:
        if role == "1P (방장)" and room["round"] == 1 and room["p1_move"] is None:
            room["p1_char"] = st.selectbox("1P 캐릭터 선택", characters, index=characters.index(room["p1_char"]))
        else:
            st.text_input("1P 캐릭터", value=room["p1_char"], disabled=True)
    with c2:
        if role == "2P (도전자)" and room["round"] == 1 and room["p2_move"] is None:
            room["p2_char"] = st.selectbox("2P 캐릭터 선택", characters, index=characters.index(room["p2_char"]))
        else:
            st.text_input("2P 캐릭터", value=room["p2_char"], disabled=True)

    online_skill = st.selectbox("이번 라운드에 낼 기술 (상대에게 비공개)", skills, key="online_skill_select")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("✅ 기술 확정 (Ready)", type="primary", use_container_width=True, disabled=room["game_over"]):
            if role == "1P (방장)":
                room["p1_move"] = online_skill
            else:
                room["p2_move"] = online_skill

            # 두 플레이어 모두 기술을 확정했으면 즉시 판정 실행
            if room["p1_move"] is not None and room["p2_move"] is not None:
                p1_dmg, p2_dmg, p1_heal, p2_heal, msg = judge_clash(
                    room["p1_move"], room["p2_move"], room["p1_hp"], room["p2_hp"]
                )
                room["p1_hp"] = min(100, max(0, room["p1_hp"] - p1_dmg + p1_heal))
                room["p2_hp"] = min(100, max(0, room["p2_hp"] - p2_dmg + p2_heal))
                room["last_msg"] = f"[{room['round']}R] {msg}"

                room["round_logs"].append(
                    {
                        "라운드": f"{room['round']}R",
                        "1P 기술": room["p1_move"].split(" ")[1],
                        "2P 기술": room["p2_move"].split(" ")[1],
                        "1P 피해": f"-{p1_dmg}" + (f" (+{p1_heal})" if p1_heal else ""),
                        "2P 피해": f"-{p2_dmg}" + (f" (+{p2_heal})" if p2_heal else ""),
                        "판정 결과": msg,
                    }
                )
                room["round"] += 1
                room["p1_move"] = None
                room["p2_move"] = None

                if room["p1_hp"] == 0 or room["p2_hp"] == 0:
                    room["game_over"] = True
            st.rerun()

    with btn_col2:
        if st.button("🔄 상대방 상태 새로고침", use_container_width=True):
            st.rerun()

    # 현재 입력 대기 상태 표시
    p1_status = "🟢 선택 완료" if room["p1_move"] else "⏳ 고민 중..."
    p2_status = "🟢 선택 완료" if room["p2_move"] else "⏳ 고민 중..."
    st.caption(f"현재 라운드({room['round']}R) 준비 현황 — 1P: {p1_status} | 2P: {p2_status}")

    st.divider()
    st.info(room["last_msg"])

    hp1, hp2 = st.columns(2)
    with hp1:
        st.metric(f"1P {room['p1_char']}", f"{room['p1_hp']} / 100 HP")
        st.progress(room["p1_hp"] / 100)
    with hp2:
        st.metric(f"2P {room['p2_char']}", f"{room['p2_hp']} / 100 HP")
        st.progress(room["p2_hp"] / 100)

    if room["game_over"]:
        if room["p1_hp"] > room["p2_hp"]:
            st.success(f"🏆 K.O.! 1P ({room['p1_char']}) 승리!")
            st.balloons()
        elif room["p2_hp"] > room["p1_hp"]:
            st.success(f"🏆 K.O.! 2P ({room['p2_char']}) 승리!")
            st.balloons()
        else:
            st.warning("🤝 DOUBLE K.O.! 무승부입니다!")

        if st.button("🔄 이 방에서 재대결하기", use_container_width=True):
            rooms[room_code] = {
                "p1_char": room["p1_char"],
                "p2_char": room["p2_char"],
                "p1_hp": 100,
                "p2_hp": 100,
                "round": 1,
                "p1_move": None,
                "p2_move": None,
                "round_logs": [],
                "last_msg": "재대결이 시작되었습니다! 각자 기술을 선택하세요.",
                "game_over": False,
            }
            st.rerun()

    # (4) 반복문 (for)을 이용한 전투 기록 테이블 출력
    if len(room["round_logs"]) > 0:
        st.subheader("📜 라운드별 기술 충돌 기록")
        table_rows = []
        for log in room["round_logs"]:
            table_rows.append(log)
        st.table(table_rows)
