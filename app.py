'''import streamlit as st
from Checkpoints import CHECKPOINTS
from context_generator import (
    get_learning_context,
    get_simple_explanation,
    calculate_relevance_score
)
from llm_tester import (
    generate_1question,
    generate_2question,
    generate_3question,
    evaluate_answer
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Autonomous Adaptive Learning Agent",
    page_icon="🎓",
    layout="wide"
)

st.markdown("# 🤖 Autonomous Adaptive Learning System")

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------
if "stage" not in st.session_state:
    st.session_state.stage = "choose"

if "checkpoint_index" not in st.session_state:
    st.session_state.checkpoint_index = None

if "questions" not in st.session_state:
    st.session_state.questions = []

if "scores" not in st.session_state:
    st.session_state.scores = []

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "context" not in st.session_state:
    st.session_state.context = ""

if "simple" not in st.session_state:
    st.session_state.simple = ""

if "finished_topics" not in st.session_state:
    st.session_state.finished_topics = []

if "recent_topics" not in st.session_state:
    st.session_state.recent_topics = []

if "attempt_count" not in st.session_state:
    st.session_state.attempt_count = 0

if "total_points" not in st.session_state:
    st.session_state.total_points = 0

if "topic_points" not in st.session_state:
    st.session_state.topic_points = {}

# --------------------------------------------------
# TABS
# --------------------------------------------------
tabs = st.tabs(["🏠 Home", "📚 Topics & Objectives", "🕘 Recently Visited", "✅ Finished Topics"])
home_tab, topics_tab, recent_tab, finished_tab = tabs

# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------
with st.sidebar:
    st.title("🎓 Navigation")

    options = {
        f"{cp['id']}. {cp['topic']}": i
        for i, cp in enumerate(CHECKPOINTS)
    }

    choice = st.selectbox("Select Topic", options.keys())

    selected_index = options[choice]
    selected_topic = CHECKPOINTS[selected_index]["topic"]
    is_completed = selected_topic in st.session_state.finished_topics

    if st.button("🚀 Start Learning", disabled=is_completed):
        st.session_state.checkpoint_index = selected_index
        st.session_state.stage = "learn"

        if selected_topic not in st.session_state.recent_topics:
            st.session_state.recent_topics.append(selected_topic)

        st.session_state.questions = []
        st.session_state.scores = []
        st.session_state.current_q = 0
        st.session_state.context = ""
        st.session_state.simple = ""
        st.session_state.attempt_count = 0

        st.rerun()

    if is_completed:
        st.warning("✅ This checkpoint is already completed.")

    st.divider()
    st.subheader("🏆 Scoreboard")
    st.metric("Total Points", st.session_state.total_points)

# --------------------------------------------------
# HOME TAB
# --------------------------------------------------
with home_tab:
    st.subheader("Welcome 👋")
    st.info("Select a topic from the sidebar and click Start Learning to begin.")

# --------------------------------------------------
# TOPICS TAB
# --------------------------------------------------
with topics_tab:
    st.subheader("All Topics")
    for cp in CHECKPOINTS:
        with st.expander(f"{cp['id']}. {cp['topic']}"):
            for obj in cp["objectives"]:
                st.write(f"- {obj}")

# --------------------------------------------------
# RECENT TAB
# --------------------------------------------------
with recent_tab:
    st.subheader("Recently Visited")
    if st.session_state.recent_topics:
        for topic in reversed(st.session_state.recent_topics):
            st.write(f"- {topic}")
    else:
        st.info("No recent topics yet.")

# --------------------------------------------------
# FINISHED TAB
# --------------------------------------------------
with finished_tab:
    st.subheader("Completed Topics")
    if st.session_state.finished_topics:
        for topic in st.session_state.finished_topics:
            points = st.session_state.topic_points.get(topic, 0)
            st.success(f"{topic} — {points} pts")
    else:
        st.info("No completed topics yet.")

# --------------------------------------------------
# LEARNING STAGE
# --------------------------------------------------
if st.session_state.stage == "learn" and st.session_state.checkpoint_index is not None:

    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📖 Explanation: {cp['topic']}")

        st.markdown("### 🎯 Objectives")
        for obj in cp["objectives"]:
            st.write(f"- {obj}")

        if not st.session_state.context:
            with st.spinner("Generating learning content..."):
                context = get_learning_context(cp["topic"], cp["objectives"])
                st.session_state.context = context

        with st.container(border=True):
            st.write(st.session_state.context)

    with col2:
        st.subheader("📝 Test Section")
        st.info("When ready, start the test.")

        if st.button("Start Test"):
            st.session_state.stage = "test"
            st.session_state.attempt_count += 1
            st.rerun()

# --------------------------------------------------
# TEST STAGE
# --------------------------------------------------
elif st.session_state.stage == "test":

    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    generators = [
        generate_1question,
        generate_2question,
        generate_3question
    ]

    progress = st.session_state.current_q / 3
    st.progress(progress)

    if st.session_state.current_q < 3:

        if len(st.session_state.questions) <= st.session_state.current_q:
            with st.spinner("Generating question..."):
                q = generators[st.session_state.current_q](
                    cp["topic"],
                    cp["objectives"],
                    st.session_state.questions
                )
                st.session_state.questions.append(q)

        question_text = st.session_state.questions[st.session_state.current_q]

        st.markdown(f"""
        <div style='padding:20px;
                    border-radius:12px;
                    background-color:#1E293B'>
        <h4>Question {st.session_state.current_q + 1}</h4>
        <p>{question_text}</p>
        </div>
        """, unsafe_allow_html=True)

        answer = st.radio(
            "Select Your Answer",
            ["A", "B", "C", "D"],
            key=f"ans_{st.session_state.current_q}"
        )

        if st.button("Submit Answer"):
            with st.spinner("Evaluating..."):
                score = evaluate_answer(
                    cp["topic"],
                    question_text,
                    answer
                )
                st.session_state.scores.append(score)

            st.success(f"Score: {score * 100:.0f}%")
            st.session_state.current_q += 1
            st.rerun()

    else:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)

        st.subheader("📊 Final Result")
        st.metric("Average Score", f"{avg * 100:.0f}%")
        st.bar_chart(st.session_state.scores)

        if avg >= cp["success_criteria"]:

            topic_name = cp["topic"]
            attempt = st.session_state.attempt_count

            # -------- 5TH ATTEMPT BLOCK --------
            if attempt >= 5:
                st.error("⚠️ Try attempting the checkpoint again and come back to the homescreen.")

                st.session_state.stage = "choose"
                st.session_state.checkpoint_index = None
                st.session_state.questions = []
                st.session_state.scores = []
                st.session_state.current_q = 0
                st.session_state.context = ""
                st.session_state.simple = ""
                st.session_state.attempt_count = 0

                st.rerun()

            else:
                points_awarded = 10 - (attempt - 1) * 2

                st.success("✅ Passed! Topic Completed.")
                st.balloons()

                st.success(f"🏆 Points Earned: {points_awarded}")

                if topic_name not in st.session_state.finished_topics:
                    st.session_state.topic_points[topic_name] = points_awarded
                    st.session_state.total_points += points_awarded
                    st.session_state.finished_topics.append(topic_name)

                st.metric("💎 Total Points", st.session_state.total_points)

                if st.button("🏠 Return to Home"):
                    st.session_state.stage = "choose"
                    st.session_state.checkpoint_index = None
                    st.session_state.questions = []
                    st.session_state.scores = []
                    st.session_state.current_q = 0
                    st.session_state.context = ""
                    st.session_state.simple = ""
                    st.session_state.attempt_count = 0
                    st.rerun()

        else:
            st.error("❌ Failed. Re-teaching in simpler terms.")
            if st.button("View Simple Explanation"):
                with st.spinner("Generating simplified explanation..."):
                    simple = get_simple_explanation(
                        cp["topic"],
                        cp["objectives"]
                    )
                    st.session_state.simple = simple

                st.session_state.stage = "reteach"
                st.rerun()

# --------------------------------------------------
# RETEACH STAGE
# --------------------------------------------------
elif st.session_state.stage == "reteach":

    st.subheader("🔁 Simplified Explanation")

    with st.container(border=True):
        st.write(st.session_state.simple)

    if st.button("🔄 Retry Test"):
        st.session_state.questions = []
        st.session_state.scores = []
        st.session_state.current_q = 0
        st.session_state.stage = "test"
        st.session_state.attempt_count += 1
        st.rerun()
'''
import streamlit as st
import json
import os
import hashlib

from Checkpoints import CHECKPOINTS
from context_generator import (
    get_learning_context,
    get_simple_explanation,
    calculate_relevance_score
)
from llm_tester import (
    generate_1question,
    generate_2question,
    generate_3question,
    evaluate_answer
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Autonomous Adaptive Learning Agent",
    page_icon="🎓",
    layout="wide"
)

st.markdown("# 🤖 Autonomous Adaptive Learning System")

# --------------------------------------------------
# USER AUTH SYSTEM
# --------------------------------------------------

USER_DB = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w") as f:
            json.dump({}, f)
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

def create_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "total_points": 0,
        "finished_topics": [],
        "topic_points": {},
        "recent_topics": []
    }
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    return username in users and users[username]["password"] == hash_password(password)

def load_user_progress(username):
    users = load_users()
    return users.get(username, {})

def save_user_progress(username):
    users = load_users()
    users[username]["total_points"] = st.session_state.total_points
    users[username]["finished_topics"] = st.session_state.finished_topics
    users[username]["topic_points"] = st.session_state.topic_points
    users[username]["recent_topics"] = st.session_state.recent_topics
    save_users(users)

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

default_states = {
    "logged_in": False,
    "username": None,
    "stage": "choose",
    "checkpoint_index": None,
    "questions": [],
    "scores": [],
    "current_q": 0,
    "context": "",
    "simple": "",
    "finished_topics": [],
    "recent_topics": [],
    "attempt_count": 0,
    "total_points": 0,
    "topic_points": {}
}

for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# LOGIN / SIGNUP
# --------------------------------------------------

if not st.session_state.logged_in:

    st.title("🔐 Login or Sign Up")

    mode = st.radio("Select Option", ["Login", "Sign Up"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if mode == "Sign Up":
        if st.button("Create Account"):
            if create_user(username, password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists.")

    else:
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username

                data = load_user_progress(username)
                st.session_state.total_points = data.get("total_points", 0)
                st.session_state.finished_topics = data.get("finished_topics", [])
                st.session_state.topic_points = data.get("topic_points", {})
                st.session_state.recent_topics = data.get("recent_topics", [])

                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.stop()

# --------------------------------------------------
# TABS
# --------------------------------------------------

tabs = st.tabs(["🏠 Home", "📚 Topics & Objectives", "🕘 Recently Visited", "✅ Finished Topics"])
home_tab, topics_tab, recent_tab, finished_tab = tabs

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("🎓 Navigation")
    st.write(f"👤 Logged in as: {st.session_state.username}")

    if st.button("🚪 Logout"):
        save_user_progress(st.session_state.username)
        st.session_state.clear()
        st.rerun()

    options = {
        f"{cp['id']}. {cp['topic']}": i
        for i, cp in enumerate(CHECKPOINTS)
    }

    choice = st.selectbox("Select Topic", options.keys())
    selected_index = options[choice]
    selected_topic = CHECKPOINTS[selected_index]["topic"]
    is_completed = selected_topic in st.session_state.finished_topics

    if st.button("🚀 Start Learning", disabled=is_completed):
        st.session_state.checkpoint_index = selected_index
        st.session_state.stage = "learn"

        if selected_topic not in st.session_state.recent_topics:
            st.session_state.recent_topics.append(selected_topic)

        st.session_state.questions = []
        st.session_state.scores = []
        st.session_state.current_q = 0
        st.session_state.context = ""
        st.session_state.simple = ""
        st.session_state.attempt_count = 0

        save_user_progress(st.session_state.username)
        st.rerun()

    if is_completed:
        st.warning("✅ This checkpoint is already completed.")

    st.divider()
    st.subheader("🏆 Scoreboard")
    st.metric("Total Points", st.session_state.total_points)

# --------------------------------------------------
# HOME TAB
# --------------------------------------------------

with home_tab:
    st.subheader("Welcome 👋")
    st.info("Select a topic from the sidebar and click Start Learning to begin.")

# --------------------------------------------------
# TOPICS TAB
# --------------------------------------------------

with topics_tab:
    st.subheader("All Topics")
    for cp in CHECKPOINTS:
        with st.expander(f"{cp['id']}. {cp['topic']}"):
            for obj in cp["objectives"]:
                st.write(f"- {obj}")

# --------------------------------------------------
# RECENT TAB
# --------------------------------------------------

with recent_tab:
    st.subheader("Recently Visited")
    if st.session_state.recent_topics:
        for topic in reversed(st.session_state.recent_topics):
            st.write(f"- {topic}")
    else:
        st.info("No recent topics yet.")

# --------------------------------------------------
# FINISHED TAB
# --------------------------------------------------

with finished_tab:
    st.subheader("Completed Topics")
    if st.session_state.finished_topics:
        for topic in st.session_state.finished_topics:
            pts = st.session_state.topic_points.get(topic, 0)
            st.success(f"{topic} — {pts} pts")
    else:
        st.info("No completed topics yet.")

# --------------------------------------------------
# LEARNING STAGE
# --------------------------------------------------

if st.session_state.stage == "learn" and st.session_state.checkpoint_index is not None:

    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📖 Explanation: {cp['topic']}")
        st.markdown("### 🎯 Objectives")
        for obj in cp["objectives"]:
            st.write(f"- {obj}")

        if not st.session_state.context:
            with st.spinner("Generating learning content..."):
                st.session_state.context = get_learning_context(cp["topic"], cp["objectives"])

        with st.container(border=True):
            st.write(st.session_state.context)

    with col2:
        st.subheader("📝 Test Section")
        if st.button("Start Test"):
            st.session_state.stage = "test"
            st.session_state.attempt_count += 1
            st.rerun()

# --------------------------------------------------
# TEST STAGE
# --------------------------------------------------

elif st.session_state.stage == "test":

    cp = CHECKPOINTS[st.session_state.checkpoint_index]
    generators = [generate_1question, generate_2question, generate_3question]

    progress = st.session_state.current_q / 3
    st.progress(progress)

    if st.session_state.current_q < 3:

        if len(st.session_state.questions) <= st.session_state.current_q:
            with st.spinner("Generating question..."):
                q = generators[st.session_state.current_q](
                    cp["topic"],
                    cp["objectives"],
                    st.session_state.questions
                )
                st.session_state.questions.append(q)

        question_text = st.session_state.questions[st.session_state.current_q]

        st.markdown(f"""
        <div style='padding:20px;border-radius:12px;background-color:#1E293B'>
        <h4>Question {st.session_state.current_q + 1}</h4>
        <p>{question_text}</p>
        </div>
        """, unsafe_allow_html=True)

        answer = st.radio(
            "Select Your Answer",
            ["A", "B", "C", "D"],
            key=f"ans_{st.session_state.current_q}"
        )

        if st.button("Submit Answer"):
            with st.spinner("Evaluating..."):
                score = evaluate_answer(cp["topic"], question_text, answer)
                st.session_state.scores.append(score)

            st.success(f"Score: {score * 100:.0f}%")
            st.session_state.current_q += 1
            st.rerun()

    else:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)

        st.subheader("📊 Final Result")
        st.metric("Average Score", f"{avg * 100:.0f}%")
        st.bar_chart(st.session_state.scores)

        if avg >= cp["success_criteria"]:

            topic = cp["topic"]
            attempt = st.session_state.attempt_count

            if attempt >= 5:
                st.error("⚠️ Try attempting the checkpoint again and return to home.")
                st.session_state.stage = "choose"
                st.rerun()

            else:
                points = 10 - (attempt - 1) * 2
                st.success("✅ Passed! Topic Completed.")
                st.balloons()
                st.success(f"🏆 Points Earned: {points}")

                if topic not in st.session_state.finished_topics:
                    st.session_state.finished_topics.append(topic)
                    st.session_state.topic_points[topic] = points
                    st.session_state.total_points += points
                    save_user_progress(st.session_state.username)

                st.metric("💎 Total Points", st.session_state.total_points)

                if st.button("🏠 Return to Home"):
                    st.session_state.stage = "choose"
                    st.rerun()

        else:
            st.error("❌ Failed. Re-teaching in simpler terms.")
            if st.button("View Simple Explanation"):
                st.session_state.simple = get_simple_explanation(
                    cp["topic"],
                    cp["objectives"]
                )
                st.session_state.stage = "reteach"
                st.rerun()

# --------------------------------------------------
# RETEACH
# --------------------------------------------------

elif st.session_state.stage == "reteach":

    st.subheader("🔁 Simplified Explanation")

    with st.container(border=True):
        st.write(st.session_state.simple)

    if st.button("🔄 Retry Test"):
        st.session_state.questions = []
        st.session_state.scores = []
        st.session_state.current_q = 0
        st.session_state.stage = "test"
        st.session_state.attempt_count += 1
        st.rerun()
