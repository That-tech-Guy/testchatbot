import streamlit as st
import random
import time
import json
from pathlib import Path

st.set_page_config(page_title="🔮 AI Quiz Show", layout="centered")

# =========================
#         DATA
# =========================

# Sample Questions (keep adding as needed)

@st.cache_data(show_spinner=False)
def load_questions(path: str = "files/questions.json"):
    """
    Load and validate questions from a JSON file inside the 'files' folder.
    Returns a list of dicts with keys: question, options, answer, (optional metadata).
    """
    p = Path(path)
    if not p.exists():
        st.error(f"Questions file not found: {p}")
        return []

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        st.error(f"Failed to parse {p}: {e}")
        return []

    valid = []
    for i, q in enumerate(data):
        if not isinstance(q, dict):
            st.warning(f"Skipping item {i}: not a dict")
            continue
        question = q.get("question")
        options = q.get("options")
        answer = q.get("answer")

        if not question or not isinstance(question, str):
            st.warning(f"Skipping item {i}: missing/invalid 'question'")
            continue
        if not options or not isinstance(options, list) or not all(isinstance(o, str) for o in options):
            st.warning(f"Skipping item {i}: invalid 'options'")
            continue
        if answer not in options:
            st.warning(f"Skipping item {i}: 'answer' not in options")
            continue

        valid.append(q)
    return valid

# Optional: add reload button in the sidebar
with st.sidebar:
    if st.button("🔄 Reload questions"):
        load_questions.clear()
    st.caption("Questions are loaded from files/questions.json")

# Load the questions
questions = load_questions("files/questions.json")

# ECCB Member States
eccb_countries = [
    "Anguilla", "Antigua and Barbuda", "Dominica", "Grenada",
    "Montserrat", "St. Kitts and Nevis", "St. Lucia",
    "St. Vincent and the Grenadines", "Other"
]

# Avatar catalog (emoji groups)
AVATAR_CATALOG = {
    "Island Vibes": ["🌴", "🏝️", "🌊", "🍍", "⚓️"],
    "Sea Life": ["🐠", "🐢", "🦈", "🦞", "🐬"],
    "Birds": ["🦜", "🦩", "🦉"],
    "Fun": ["🎵", "🎯", "🎮", "🎓", "💡"],
}

# =========================
#     AVATAR PICKER UI
# =========================
def avatar_picker():
    """Persist selection in st.session_state.picked_avatar as user interacts.
       Returns latest selection dict or None:
       {'kind': 'emoji'|'image', 'emoji': str|None, 'image_bytes': bytes|None}
    """
    if "picked_avatar" not in st.session_state:
        st.session_state.picked_avatar = None

    st.subheader("Choose your avatar")
    tabs = st.tabs(["🧩 Emoji avatars", "✨ Special emoji", "🖼️ Upload image"])

    # --- Tab 1: Emoji catalog ---
    with tabs[0]:
        colA, colB = st.columns([1, 2])
        with colA:
            category = st.selectbox("Category", list(AVATAR_CATALOG.keys()), key="av_cat")
        emojis = AVATAR_CATALOG[category]

        choice = st.radio("Pick one", emojis, horizontal=True, key="av_choice")
        with colB:
            st.markdown(
                f"<div style='font-size:72px; line-height:1; text-align:center;'>{choice}</div>",
                unsafe_allow_html=True
            )

        # Persist automatically
        st.session_state.picked_avatar = {"kind": "emoji", "emoji": choice, "image_bytes": None}

    # --- Tab 2: Special emoji (typed) ---
    with tabs[1]:
        custom_emoji = st.text_input("Type any emoji (e.g., 🐳, 😎, 🚀)", key="av_custom")
        if custom_emoji.strip():
            st.markdown(
                f"<div style='font-size:72px; line-height:1; text-align:center;'>{custom_emoji}</div>",
                unsafe_allow_html=True
            )
            st.session_state.picked_avatar = {"kind": "emoji", "emoji": custom_emoji.strip(), "image_bytes": None}

    # --- Tab 3: Upload image ---
    with tabs[2]:
        img = st.file_uploader("Upload a square PNG/JPG (suggested ~256×256)", type=["png", "jpg", "jpeg"], key="av_upload")
        if img is not None:
            img_bytes = img.read()
            st.image(img_bytes, width=120)
            st.session_state.picked_avatar = {"kind": "image", "emoji": None, "image_bytes": img_bytes}

    return st.session_state.picked_avatar

# =========================
#     SESSION STATE INIT
# =========================
if "setup_done" not in st.session_state:
    st.session_state.setup_done = False
if "question_index" not in st.session_state:
    st.session_state.question_index = 0
if "selected_option" not in st.session_state:
    st.session_state.selected_option = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "last_run_time" not in st.session_state:
    st.session_state.last_run_time = None
if "score" not in st.session_state:
    st.session_state.score = 0
if "scored_flags" not in st.session_state:
    st.session_state.scored_flags = {}  # prevents double-scoring across reruns

# =========================
#       PRE-QUIZ SETUP
# =========================
if not st.session_state.setup_done:
    st.title("🧠 AI Quiz Show - Setup")
    st.markdown("Welcome! Please enter your details before starting the quiz.")

    username = st.text_input("Enter your username:")
    country = st.selectbox("Select your country:", eccb_countries)
    picked = avatar_picker()  # persists as user interacts
    num_questions = st.slider(
        "Number of questions to attempt:",
        min_value=1, max_value=len(questions), value=len(questions)
    )

    if st.button("🚀 Start Quiz"):
        if username.strip() == "":
            st.warning("Please enter a username before starting.")
        elif picked is None:
            st.warning("Please choose an avatar before starting.")
        else:
            # store user details & avatar
            st.session_state.username = username.strip()
            st.session_state.country = country
            st.session_state.avatar_kind = picked["kind"]
            st.session_state.avatar_emoji = picked["emoji"]
            st.session_state.avatar_image_bytes = picked["image_bytes"]
            st.session_state.setup_done = True

            # build quiz set
            st.session_state.quiz_questions = random.sample(questions, num_questions)
            st.session_state.question_index = 0
            st.session_state.last_run_time = time.time()
            st.session_state.selected_option = None
            st.session_state.score = 0
            st.session_state.scored_flags = {}

            st.rerun()
    st.stop()

# =========================
#       QUIZ LOGIC
# =========================

# Guard end-of-quiz refresh
if st.session_state.question_index >= len(st.session_state.quiz_questions):
    st.balloons()

    colA, colB = st.columns([1, 4])
    with colA:
        if st.session_state.get("avatar_kind") == "image" and st.session_state.get("avatar_image_bytes"):
            st.image(st.session_state.avatar_image_bytes, width=80)
        else:
            emoji = st.session_state.get("avatar_emoji", "🧠")
            st.markdown(f"<div style='font-size:72px; line-height:1;'>{emoji}</div>", unsafe_allow_html=True)

    with colB:
        st.markdown(f"## 🎉 Quiz Complete, {st.session_state.username} from {st.session_state.country}!")
        st.markdown(f"### 🏆 Your Score: **{st.session_state.score} / {len(st.session_state.quiz_questions)}**")
        st.progress(st.session_state.score / max(1, len(st.session_state.quiz_questions)))
    st.markdown("Refresh the page to try again.")
    st.stop()

q = st.session_state.quiz_questions[st.session_state.question_index]

# --- Styles ---
st.markdown("""
    <style>
        .big-question { font-size: 28px; font-weight: bold; color: #007bff; }
        .option-button { font-size: 22px; padding: 0.5em; margin: 0.3em; }
        .headerbar { font-size: 16px; padding: 8px 12px; background: #f7fbff; border: 1px solid #e3f2ff; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Header with avatar + username + country + running score
st.markdown("<div class='headerbar'>", unsafe_allow_html=True)
col_avatar, col_meta = st.columns([1, 6])
with col_avatar:
    if st.session_state.get("avatar_kind") == "image" and st.session_state.get("avatar_image_bytes"):
        st.image(st.session_state.avatar_image_bytes, width=42)
    else:
        emoji = st.session_state.get("avatar_emoji", "🧠")
        st.markdown(f"<div style='font-size:38px; line-height:1;'>{emoji}</div>", unsafe_allow_html=True)
with col_meta:
    st.markdown(
        f"<b>{st.session_state.username}</b> — {st.session_state.country}<br>"
        f"Question {st.session_state.question_index + 1} of {len(st.session_state.quiz_questions)} "
        f"| Score: <b>{st.session_state.score}</b>",
        unsafe_allow_html=True
    )
st.markdown("</div>", unsafe_allow_html=True)

# Placeholders (so we can cleanly clear UI between phases/questions)
question_placeholder = st.empty()
options_placeholder = st.empty()
answer_placeholder = st.empty()
progress_placeholder = st.empty()
info_placeholder = st.empty()

elapsed = time.time() - st.session_state.last_run_time

# === PHASE 1: Question & Buttons (0–5s) ===
if elapsed < 5:
    question_placeholder.markdown(f"<div class='big-question'>🧠 {q['question']}</div>", unsafe_allow_html=True)
    info_placeholder.info("⏳ Choose an option or wait. Showing answer in 5 seconds...")
    progress_placeholder.progress(min(elapsed / 5, 1.0))

    with options_placeholder.container():
        cols = st.columns(2)
        for i, option in enumerate(q["options"]):
            if cols[i % 2].button(option, key=f"opt_{st.session_state.question_index}_{i}"):
                st.session_state.selected_option = option
                # jump straight to reveal phase
                st.session_state.last_run_time = time.time() - 5.01
                st.rerun()

    time.sleep(0.12)
    st.rerun()

# === PHASE 2: Reveal Answers (5–10s) ===
elif elapsed < 10:
    question_placeholder.markdown(f"<div class='big-question'>🧠 {q['question']}</div>", unsafe_allow_html=True)
    options_placeholder.empty()  # hide buttons during reveal

    # Score ONCE (when entering reveal)
    qkey = st.session_state.question_index
    if not st.session_state.scored_flags.get(qkey, False):
        if st.session_state.selected_option == q["answer"]:
            st.session_state.score += 1
        st.session_state.scored_flags[qkey] = True

    with answer_placeholder.container():
        for option in q["options"]:
            if option == q["answer"]:
                label = f"✅ {option}"
                if st.session_state.selected_option == option:
                    label += " — Your choice"
                st.success(label)
            else:
                label = f"❌ {option}"
                if st.session_state.selected_option == option:
                    label += " — Your choice"
                st.error(label)

    progress_placeholder.progress(min((elapsed - 5) / 5, 1.0))
    info_placeholder.info("➡️ Next question in 5 seconds...")

    time.sleep(0.12)
    st.rerun()

# === PHASE 3: Advance (>=10s) ===
else:
    # Clean up UI before next question
    question_placeholder.empty()
    options_placeholder.empty()
    answer_placeholder.empty()
    progress_placeholder.empty()
    info_placeholder.empty()

    st.session_state.question_index += 1
    st.session_state.last_run_time = time.time()
    st.session_state.selected_option = None

    if st.session_state.question_index >= len(st.session_state.quiz_questions):
        st.balloons()

        colA, colB = st.columns([1, 4])
        with colA:
            if st.session_state.get("avatar_kind") == "image" and st.session_state.get("avatar_image_bytes"):
                st.image(st.session_state.avatar_image_bytes, width=80)
            else:
                emoji = st.session_state.get("avatar_emoji", "🧠")
                st.markdown(f"<div style='font-size:72px; line-height:1;'>{emoji}</div>", unsafe_allow_html=True)

        with colB:
            st.markdown(f"## 🎉 Quiz Complete, {st.session_state.username} from {st.session_state.country}!")
            st.markdown(f"### 🏆 Your Score: **{st.session_state.score} / {len(st.session_state.quiz_questions)}**")
            st.progress(st.session_state.score / max(1, len(st.session_state.quiz_questions)))
        st.markdown("Refresh the page to try again.")
        st.stop()

    st.rerun()
