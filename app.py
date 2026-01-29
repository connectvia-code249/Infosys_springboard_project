'''import streamlit as st
from Checkpoint_graph import run_checkpoint_graph

st.set_page_config(page_title="Autonomous Learning Agent")

st.title("🤖 Autonomous Learning Agent")

# ---------------- SESSION STATE ----------------
if "started" not in st.session_state:
    st.session_state.started = False

if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}

if "output" not in st.session_state:
    st.session_state.output = None


# ---------------- USER INPUT ----------------
topic = st.text_input("Enter learning topic")

if st.button("Start Learning"):
    st.session_state.started = True
    st.session_state.graph_state = {
        "topic": topic
    }

# ---------------- RUN AGENT ----------------
if st.session_state.started:

    st.subheader("Agent Output")

    result = run_checkpoint_graph(st.session_state.graph_state)

    st.session_state.graph_state = result.get("state", st.session_state.graph_state)
    st.session_state.output = result.get("output", "")

    st.write(st.session_state.output)

    if st.button("Next Step"):
        st.experimental_rerun()'''

import streamlit as st
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

st.set_page_config(page_title="Adaptive Learning Agent", layout="centered")
st.title("🎓 Adaptive Learning Agent")

# ---------------- SESSION STATE INIT ----------------
if "checkpoint_index" not in st.session_state:
    st.session_state.checkpoint_index = None
    st.session_state.stage = "choose"
    st.session_state.questions = []
    st.session_state.scores = []
    st.session_state.current_q = 0
    st.session_state.context = ""

# ---------------- CHECKPOINT SELECTION ----------------
if st.session_state.stage == "choose":
    st.subheader("Choose a Checkpoint")

    options = {
        f"{cp['id']}. {cp['topic']}": i
        for i, cp in enumerate(CHECKPOINTS)
    }

    choice = st.selectbox("Select topic", options.keys())

    if st.button("Start Learning"):
        st.session_state.checkpoint_index = options[choice]
        st.session_state.stage = "learn"
        st.rerun()


# ---------------- LEARNING CONTEXT ----------------
elif st.session_state.stage == "learn":
    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    st.subheader(cp["topic"])
    st.write("### Objectives")
    for obj in cp["objectives"]:
        st.write(f"- {obj}")

    if not st.session_state.context:
        context = get_learning_context(cp["topic"], cp["objectives"])
        st.session_state.context = context
        st.session_state.relevance = calculate_relevance_score(
            context, cp["objectives"]
        )

    st.divider()
    st.write(st.session_state.context)

    st.info(f"Relevance Score: {st.session_state.relevance}/100")
    st.success(f"Pass Score Required: {cp['success_criteria'] * 100:.0f}%")

    if st.button("Take Test"):
        st.session_state.stage = "test"
        st.rerun()


# ---------------- TEST MODE ----------------
elif st.session_state.stage == "test":
    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    generators = [
        generate_1question,
        generate_2question,
        generate_3question
    ]

    if st.session_state.current_q < 3:
        if len(st.session_state.questions) <= st.session_state.current_q:
            q = generators[st.session_state.current_q](
                cp["topic"],
                cp["objectives"],
                st.session_state.questions
            )
            st.session_state.questions.append(q)

        st.write(f"### Question {st.session_state.current_q + 1}")
        st.code(st.session_state.questions[st.session_state.current_q])

        answer = st.radio(
            "Your Answer",
            ["A", "B", "C", "D"],
            key=f"ans_{st.session_state.current_q}"
        )

        if st.button("Submit Answer"):
            score = evaluate_answer(
                cp["topic"],
                st.session_state.questions[st.session_state.current_q],
                answer
            )
            st.session_state.scores.append(score)
            st.success(f"Score: {score * 100:.0f}%")
            st.session_state.current_q += 1
            st.rerun()


    else:
        avg = sum(st.session_state.scores) / len(st.session_state.scores)
        st.subheader("📊 Final Result")
        st.write(f"Average Score: {avg * 100:.0f}%")

        if avg >= cp["success_criteria"]:
            st.success("✅ Passed! Moving to next checkpoint.")
            if st.button("Continue"):
                st.session_state.checkpoint_index += 1
                st.session_state.stage = "learn"
                st.session_state.questions = []
                st.session_state.scores = []
                st.session_state.current_q = 0
                st.session_state.context = ""
                st.rerun()

        else:
            st.error("❌ Failed. Re-teaching in simpler terms.")
            if st.button("View Simple Explanation"):
                simple = get_simple_explanation(
                    cp["topic"],
                    cp["objectives"]
                )
                st.session_state.simple = simple
                st.session_state.stage = "reteach"
                st.rerun()


# ---------------- SIMPLE RE-TEACH ----------------
elif st.session_state.stage == "reteach":
    cp = CHECKPOINTS[st.session_state.checkpoint_index]

    st.subheader("🔁 Simple Explanation")
    st.write(st.session_state.simple)

    relevance = calculate_relevance_score(
        st.session_state.simple,
        cp["objectives"]
    )
    st.info(f"Relevance Score: {relevance}/100")

    if st.button("Retry Test"):
        st.session_state.questions = []
        st.session_state.scores = []
        st.session_state.current_q = 0
        st.session_state.stage = "test"
        st.rerun()

