import streamlit as st
import random
import time
import os
import base64
from visualizer import render_grid_animation


# --- 유틸리티 함수: 움짤(GIF) 및 소리(MP3) 재생 ---
def get_random_file(folder_path, extensions=(".gif", ".mp3")):
    """해당 폴더에서 확장자에 맞는 파일을 랜덤으로 1개 선택합니다."""
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(extensions)]
        if files:
            return os.path.join(folder_path, random.choice(files))
    return None


def play_audio(folder_path):
    """지정된 폴더에서 랜덤 mp3 파일을 찾아 안 보이게 자동 재생합니다."""
    audio_path = get_random_file(folder_path, extensions=(".mp3",))
    if audio_path:
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio autoplay="true" style="display:none;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)


def show_gif(folder_path):
    """지정된 폴더에서 랜덤 gif 파일을 찾아 중앙에 예쁘게 표시합니다."""
    gif_path = get_random_file(folder_path, extensions=(".gif",))
    if gif_path:
        with open(gif_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="display:flex; justify-content:center; margin-top:20px; margin-bottom:20px;">
                    <img src="data:image/gif;base64,{b64}" width="250" style="border-radius:15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)


# --- 페이지 기본 설정 (모바일 친화적) ---
st.set_page_config(
    page_title="개똥 구구단 연습하기",
    page_icon="🎈",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- 커스텀 CSS (모바일 버튼 크기 최적화 및 터치 영역 확대) ---
st.markdown(
    """
    <style>
    /* 화면 여백 최대한 줄이기 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    div.stButton > button {
        width: 100%;
        height: 60px;
        border-radius: 20px;
        background-color: #FFF9CE;
        border: 3px solid #FFC93C;
        box-shadow: 0 6px 0 #FFC93C;
        transition: all 0.1s ease-in-out;
    }
    div.stButton > button p {
        font-size: 26px !important;
        font-weight: 900 !important;
        color: #FF5E5E !important;
        margin: 0;
    }
    div.stButton > button:hover {
        border-color: #FFB300;
        background-color: #FFFEF0;
        transform: translateY(-2px);
        box-shadow: 0 10px 0 #FFB300;
    }
    div.stButton > button:hover p {
        color: #FF5E5E !important;
    }
    div.stButton > button:active {
        transform: translateY(6px);
        box-shadow: 0 2px 0 #FFC93C;
    }
    .big-font {
        font-size: 32px !important;
        font-weight: bold !important;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 10px;
        margin-top: 5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 사용할 이모지 리스트 ---
EMOJIS = ["🍎", "🐶", "🚀", "🐼", "🍓", "⚽", "🚗", "🌟", "🍔", "🐯"]

# --- 상태 관리 초기화 ---
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.score = 0
    st.session_state.total = 0
    st.session_state.round_count = 0
    st.session_state.game_over = False
    st.session_state.answered = False
    st.session_state.message = ""
    st.session_state.show_wrong_feedback = False
    st.session_state.show_correct_feedback = False
    # 문제 출제를 위한 트리거 플래그
    st.session_state.need_new_question = True


def generate_question(mode):
    """새로운 문제를 생성하고 세션 상태에 저장합니다."""
    # 10라운드 종료 여부 확인 (종료 시 새 문제 출제 방지)
    if st.session_state.round_count >= 10:
        st.session_state.game_over = True
        st.session_state.need_new_question = False
        return

    st.session_state.round_count += 1

    # N단 선택
    if mode == "2~9 랜덤":
        num1 = random.randint(2, 9)
    else:
        num1 = int(mode.replace("단", ""))

    num2 = random.randint(1, 9)
    correct_ans = num1 * num2

    # 오답 생성 로직 (비슷한 숫자로 헷갈리게)
    wrong1 = correct_ans + random.choice([-1, 1, -2, 2, num1, -num1])
    if wrong1 <= 0:
        wrong1 = correct_ans + random.randint(3, 5)

    wrong2 = correct_ans + random.choice([-3, 3, -num2, num2])
    if wrong2 <= 0 or wrong2 == wrong1:
        wrong2 = correct_ans + random.randint(6, 10)

    options = [
        correct_ans,
        list(set([wrong1, wrong2]))[0],
        list(set([wrong1, wrong2, wrong1 + 1]))[-1],
    ]
    if len(set(options)) < 3:  # 혹시라도 중복되면 확실히 다르게 강제 처리
        options = [
            correct_ans,
            correct_ans + 5,
            correct_ans - 3 if correct_ans > 3 else correct_ans + 7,
        ]

    random.shuffle(options)

    st.session_state.num1 = num1
    st.session_state.num2 = num2
    st.session_state.correct_ans = correct_ans
    st.session_state.options = options
    st.session_state.emoji = random.choice(EMOJIS)
    st.session_state.answered = False
    st.session_state.message = ""
    st.session_state.show_wrong_feedback = False
    st.session_state.need_new_question = False


# --- UI 레이아웃 ---
st.sidebar.title("설정 ⚙️")
selected_mode = st.sidebar.selectbox(
    "어떤 단을 연습할까요?", ["2~9 랜덤"] + [f"{i}단" for i in range(2, 10)]
)

# 사이드바에서 모드를 바꿨을 때 새로운 문제를 강제로 내도록 처리
if "prev_mode" not in st.session_state or st.session_state.prev_mode != selected_mode:
    st.session_state.prev_mode = selected_mode
    st.session_state.round_count = 0
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.need_new_question = True

# 새로운 문제 생성 필요시 실행
if st.session_state.need_new_question:
    generate_question(selected_mode)

if st.session_state.get("show_balloon", False):
    st.balloons()
    st.session_state.show_balloon = False

# 점수 영역
if not st.session_state.game_over:
    st.write(
        f"📈 단계: **{st.session_state.round_count} / 10** &nbsp;&nbsp;|&nbsp;&nbsp; 🏆 현재 점수: **{st.session_state.score}점**"
    )

    # 메인 문제 표시 영역
    st.markdown(
        f'<p class="big-font">{st.session_state.num1} X {st.session_state.num2} = ?</p>',
        unsafe_allow_html=True,
    )

    # 시각화 (애니메이션 렌더링)
    # 구구단의 개념 (A행 B열)
    render_grid_animation(
        st.session_state.num1, st.session_state.num2, st.session_state.emoji
    )


def handle_answer(selected):
    if selected == st.session_state.correct_ans:
        st.session_state.score += 10
        st.session_state.total += 1
        st.session_state.show_correct_feedback = True
        st.rerun()
    else:
        # 오답 시 피드백 모드로 전환
        st.session_state.total += 1
        st.session_state.show_wrong_feedback = True
        st.rerun()


st.write("---")

if st.session_state.game_over:
    if st.session_state.score >= 80:
        result_msg = "강봄 나이스~ 🎉"
        folder = "gif/high score"
    else:
        result_msg = "공부 다시해라 ^^"
        folder = "gif/low score"

    st.markdown(
        f'<p class="big-font" style="color:#FF5E5E; font-size: 48px !important;">{result_msg}<br>최종 점수: {st.session_state.score}점</p>',
        unsafe_allow_html=True,
    )

    # 결과 움짤/소리 재생
    play_audio(folder)
    show_gif(folder)

    if st.button("처음부터 다시 연습하기 🚀", use_container_width=True):
        st.session_state.round_count = 0
        st.session_state.score = 0
        st.session_state.game_over = False
        st.session_state.show_wrong_feedback = False
        st.session_state.show_correct_feedback = False
        st.session_state.need_new_question = True
        st.rerun()
else:
    if st.session_state.get("show_correct_feedback", False):
        st.balloons()
        st.markdown(
            "<p class='big-font' style='color:#4CAF50; font-size: 36px !important; margin-bottom:15px;'>정답입니다! 👏</p>",
            unsafe_allow_html=True,
        )

        # 정답 움짤/소리 재생
        play_audio("gif/correct")
        show_gif("gif/correct")

        if st.button("다음 문제 👉", use_container_width=True):
            st.session_state.show_correct_feedback = False
            st.session_state.need_new_question = True
            st.rerun()

    elif st.session_state.get("show_wrong_feedback", False):
        # 오답 피드백 화면
        st.markdown(
            "<p class='big-font' style='color:#FF5E5E; font-size: 28px !important; margin-bottom:15px;'>땡! 이거지롱~👇</p>",
            unsafe_allow_html=True,
        )

        # 오답 움짤/소리 재생
        play_audio("gif/incorrect")
        show_gif("gif/incorrect")
        col1, col2, col3 = st.columns(3)
        opts = st.session_state.options
        correct = st.session_state.correct_ans

        for idx, col in enumerate([col1, col2, col3]):
            val = opts[idx]
            if val == correct:
                html = f"""
                <div style="position:relative; width:100%; height:60px; border-radius:20px; background-color:#FFF9CE; border:3px solid #FFC93C; display:flex; align-items:center; justify-content:center;">
                    <p style="font-size:26px; font-weight:900; color:#FF5E5E; margin:0; z-index:2;">{val}</p>
                    <div style="position:absolute; top:-10px; bottom:-10px; left:-5px; right:-5px; border:5px solid #FF3366; border-radius:50%; z-index:3; opacity:0.9; transform: rotate(-5deg);"></div>
                </div>
                """
            else:
                html = f"""
                <div style="position:relative; width:100%; height:60px; border-radius:20px; background-color:#F5F5F5; border:3px solid #E0E0E0; display:flex; align-items:center; justify-content:center; opacity:0.6;">
                    <p style="font-size:26px; font-weight:900; color:#A0A0A0; margin:0;">{val}</p>
                </div>
                """
            col.markdown(html, unsafe_allow_html=True)

        if st.button("다음 문제 👉", use_container_width=True):
            st.session_state.show_wrong_feedback = False
            st.session_state.need_new_question = True
            st.rerun()
    else:
        # 보기 버튼 (모바일에 꽉 차게 정렬, 가운데 정렬)
        col1, col2, col3 = st.columns(3)
        opts = st.session_state.options

        with col1:
            if st.button(str(opts[0]), key="btn_0", use_container_width=True):
                handle_answer(opts[0])
        with col2:
            if st.button(str(opts[1]), key="btn_1", use_container_width=True):
                handle_answer(opts[1])
        with col3:
            if st.button(str(opts[2]), key="btn_2", use_container_width=True):
                handle_answer(opts[2])
