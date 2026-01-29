'''from typing import TypedDict
from langgraph.graph import StateGraph, END

from Checkpoints import CHECKPOINTS
from context_generator import get_learning_context, get_simple_explanation
from llm_tester import generate_question, evaluate_answer


# Defines the state passed between LangGraph nodes

class LearningState(TypedDict):
    checkpoint_index: int   # Tracks which checkpoint the learner is on
    score: float            # Stores score obtained in the test


def choose_checkpoint():
    print("\nAvailable Checkpoints:")
    for cp in CHECKPOINTS:
        print(f"{cp['id']}. {cp['topic']}")

    while True:
        try:
            choice = int(input("\nEnter checkpoint number to start from: "))
            index = choice - 1
            if 0 <= index < len(CHECKPOINTS):
                return index
            else:
                print("Invalid checkpoint number. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def want_to_learn(state: LearningState):
    while True:
        choice = input("\nDo you want to learn a topic? (yes/no): ").lower()
        if choice in ["yes", "y"]:
            return "choose"
        elif choice in ["no", "n"]:
            return END


#NODE1
# Teaches the topic using LLM

def show_checkpoint(state: LearningState):
    index = state["checkpoint_index"]

    # Safety check
    if index >= len(CHECKPOINTS):
        return state

    checkpoint = CHECKPOINTS[index]

    print("\n---------------------------")
    print(f"CHECKPOINT {checkpoint['id']}")
    print("Topic:", checkpoint["topic"])

    # Display objectives
    print("Objectives:")
    for i, obj in enumerate(checkpoint["objectives"], start=1):
        print(f"  {i}. {obj}")

    # Generate learning content using ChatGPT API
    context = get_learning_context(
        checkpoint["topic"],
        checkpoint["objectives"]
    ) #passed to context_generator 

    print("\n--- Learning Context ---")
    print(context)
    print("-----------------------")

    # Display success criteria
    print(f"Pass Score Required: {checkpoint['success_criteria'] * 100}%")
    print("---------------------------")

    input("Press Enter when you are ready to take the test...")

    return state


# NODE2
# Generates random question and evaluates answer using LLM

def test_checkpoint(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- TEST ---")

    # Generate question dynamically
    question = generate_question(
        checkpoint["topic"],
        checkpoint["objectives"]
    ) 

    print(question)
    answer = input("Your answer: ")

    # LLM-based evaluation
    score = evaluate_answer(
        checkpoint["topic"],
        question,
        answer
    )

    print(f"Your Score: {score * 100:.0f}%")

    return {
        "checkpoint_index": index,
        "score": score
    }


#NODE3
# Decision Node

def decide_after_test(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    if state["score"] >= checkpoint["success_criteria"]:
        print("✅ Passed based on success criteria.\n")
        return "post_checkpoint_decision"
    else:
        print("❌ Failed. Explaining concept in simpler terms...\n")
        return "simple_reteach"


# increment_checkpoint Node
#NODE4

def increment_checkpoint(state: LearningState):
    return {
        "checkpoint_index": state["checkpoint_index"],
        "score": 0.0
    }


#NODE5

def simple_reteach(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- SIMPLE EXPLANATION (RE-TEACH) ---")

    simple_context = get_simple_explanation(
        checkpoint["topic"],
        checkpoint["objectives"]
    )

    print(simple_context)
    print("-----------------------------------")

    input("\nPress Enter to retry the test...")

    return state


def choose_next_checkpoint(state: LearningState):
    state["checkpoint_index"] = choose_checkpoint()
    state["score"] = 0.0
    return state


# LangGraph Configuration

graph = StateGraph(LearningState)

graph.add_node("choose_next_checkpoint", choose_next_checkpoint)
graph.add_node("show_checkpoint", show_checkpoint)
graph.add_node("test_checkpoint", test_checkpoint)
graph.add_node("simple_reteach", simple_reteach)
graph.add_node("post_checkpoint_decision", lambda state: state)

graph.set_entry_point("post_checkpoint_decision")

graph.add_conditional_edges(
    "post_checkpoint_decision",
    want_to_learn,
    {
        "choose": "choose_next_checkpoint",
        END: END
    }
)

graph.add_edge("choose_next_checkpoint", "show_checkpoint")

graph.add_edge("show_checkpoint", "test_checkpoint")

graph.add_conditional_edges(
    "test_checkpoint",
    decide_after_test
)

graph.add_edge("simple_reteach", "test_checkpoint")

learning_graph = graph.compile()


initial_state = {
    "checkpoint_index": 0,
    "score": 0.0
}

learning_graph.invoke(initial_state)'''

'''from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()


from Checkpoints import CHECKPOINTS
from context_generator import get_learning_context, get_simple_explanation, calculate_relevance_score
from llm_tester import generate_1question, evaluate_answer, generate_2question, generate_3question

# Defines the state passed between LangGraph nodes
class LearningState(TypedDict):
    checkpoint_index: int   # Tracks which checkpoint the learner is on
    score: float            # Stores average score obtained in the test
    scores: list            # Stores individual question scores


# ----------------------- Helper Functions -----------------------

def choose_checkpoint():
    print("\nAvailable Checkpoints:")
    for cp in CHECKPOINTS:
        print(f"{cp['id']}. {cp['topic']}")

    try:
        choice = int(input("\nEnter checkpoint number to start from: "))
        index = choice - 1
        if 0 <= index < len(CHECKPOINTS):
            return index
        else:
            print("❌ Invalid checkpoint number. Program ending.")
            exit(0)
    except ValueError:
        print("❌ Invalid input. Program ending.")
        exit(0)


def want_to_learn(state: LearningState):
    while True:
        choice = input("\nDo you want to learn a topic? (yes/no): ").lower()
        if choice in ["yes", "y"]:
            return "choose"
        elif choice in ["no", "n"]:
            return END


# ----------------------- Nodes -----------------------

# NODE1: Show checkpoint content
def show_checkpoint(state: LearningState):
    index = state["checkpoint_index"]

    if index >= len(CHECKPOINTS):
        return state

    checkpoint = CHECKPOINTS[index]

    print("\n---------------------------")
    print(f"CHECKPOINT {checkpoint['id']}")
    print("Topic:", checkpoint["topic"])

    print("Objectives:")
    for i, obj in enumerate(checkpoint["objectives"], start=1):
        print(f"  {i}. {obj}")

    # Generate learning context via LLM
    context = get_learning_context(checkpoint["topic"], checkpoint["objectives"])
    relevance_score = calculate_relevance_score(context, checkpoint["objectives"])
    print("\n--- Learning Context ---")
    print(context)
    print("-----------------------")
    print("\n--- RELEVANCE SCORE ---")
    print(f"Relevance Score: {relevance_score}/100")    
    print("-----------------------")

    print(f"Pass Score Required: {checkpoint['success_criteria'] * 100}%")
    print("---------------------------")

    input("Press Enter when you are ready to take the test...")

    return state


# NODE2: Test checkpoint and evaluate
def test_checkpoint(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- TEST ---")

    # Reset scores for this test attempt
    state["scores"] = []

    question_generators = [
        generate_1question,
        generate_2question,
        generate_3question
    ]
    prev= []
    for i, gen_fn in enumerate(question_generators, start=1):
        print(f"\nQuestion {i}:")
        question = gen_fn(checkpoint["topic"], checkpoint["objectives"],prev)
        prev.append(question)
        print(question)

        answer = input("Your answer: ")

        # ALWAYS evaluate immediately
        question_score = evaluate_answer(
            checkpoint["topic"],
            question,
            answer
        )

        print(f"Score for Question {i}: {question_score * 100:.0f}%")
        state["scores"].append(question_score)

    # Calculate average score AFTER all 3 questions
    avg_score = sum(state["scores"]) / len(state["scores"])
    state["score"] = avg_score

    print(f"\n✅ Final Average Score: {avg_score * 100:.0f}%")

    return state



# NODE3: Decide after test using average score
def decide_after_test(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    if state["score"] >= checkpoint["success_criteria"]:
        print("✅ Passed based on success criteria.\n")
        return "post_checkpoint_decision"
    else:
        print("❌ Failed. Explaining concept in simpler terms...\n")
        return "simple_reteach"


# NODE4: Increment checkpoint resets score
def increment_checkpoint(state: LearningState):
    return {
        "checkpoint_index": state["checkpoint_index"],
        "score": 0.0,
        "scores": []  # reset list for new checkpoint
    }


# NODE5: Simple re-teach
def simple_reteach(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- SIMPLE EXPLANATION (RE-TEACH) ---")

    simple_context = get_simple_explanation(checkpoint["topic"], checkpoint["objectives"])
    relevance_score = calculate_relevance_score(simple_context, checkpoint["objectives"])
    print(simple_context)
    print("-----------------------------------")
    print("\n--- RELEVANCE SCORE ---")
    print(f"Relevance Score: {relevance_score}/100")    
    print("-----------------------------------")

    input("\nPress Enter to retry the test...")

    return state


def choose_next_checkpoint(state: LearningState):
    state["checkpoint_index"] = choose_checkpoint()
    state["score"] = 0.0
    state["scores"] = []
    return state


# ----------------------- LangGraph Configuration -----------------------

graph = StateGraph(LearningState)

# Add nodes
graph.add_node("choose_next_checkpoint", choose_next_checkpoint)
graph.add_node("show_checkpoint", show_checkpoint)
graph.add_node("test_checkpoint", test_checkpoint)
graph.add_node("simple_reteach", simple_reteach)
graph.add_node("post_checkpoint_decision", lambda state: state)

# Entry point
graph.set_entry_point("post_checkpoint_decision")

# Conditional edges
graph.add_conditional_edges(
    "post_checkpoint_decision",
    want_to_learn,
    {
        "choose": "choose_next_checkpoint",
        END: END
    }
)

graph.add_edge("choose_next_checkpoint", "show_checkpoint")
graph.add_edge("show_checkpoint", "test_checkpoint")

graph.add_conditional_edges(
    "test_checkpoint",
    decide_after_test
)

graph.add_edge("simple_reteach", "test_checkpoint")

# Compile the graph
learning_graph = graph.compile()

# ----------------------- Invoke -----------------------

initial_state = {
    "checkpoint_index": 0,
    "score": 0.0,
    "scores": []
}

learning_graph.invoke(initial_state)'''


from typing import TypedDict
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
load_dotenv()
import os


from Checkpoints import CHECKPOINTS
from context_generator import get_learning_context, get_simple_explanation, calculate_relevance_score
from llm_tester import generate_1question, evaluate_answer, generate_2question, generate_3question

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Infosys_Spring"

# Defines the state passed between LangGraph nodes
class LearningState(TypedDict):
    checkpoint_index: int   # Tracks which checkpoint the learner is on
    score: float            # Stores average score obtained in the test
    scores: list            # Stores individual question scores


# ----------------------- Helper Functions -----------------------

def choose_checkpoint():
    print("\nAvailable Checkpoints:")
    for cp in CHECKPOINTS:
        print(f"{cp['id']}. {cp['topic']}")

    try:
        choice = int(input("\nEnter checkpoint number to start from: "))
        index = choice - 1
        if 0 <= index < len(CHECKPOINTS):
            return index
        else:
            print("❌ Invalid checkpoint number. Program ending.")
            exit(0)
    except ValueError:
        print("❌ Invalid input. Program ending.")
        exit(0)


def want_to_learn(state: LearningState):
    while True:
        choice = input("\nDo you want to learn a topic? (yes/no): ").lower()
        if choice in ["yes", "y"]:
            return "choose"
        elif choice in ["no", "n"]:
            return END


# ----------------------- Nodes -----------------------

# NODE1: Show checkpoint content
def show_checkpoint(state: LearningState):
    index = state["checkpoint_index"]

    if index >= len(CHECKPOINTS):
        return state

    checkpoint = CHECKPOINTS[index]

    print("\n---------------------------")
    print(f"CHECKPOINT {checkpoint['id']}")
    print("Topic:", checkpoint["topic"])

    print("Objectives:")
    for i, obj in enumerate(checkpoint["objectives"], start=1):
        print(f"  {i}. {obj}")

    # Generate learning context via LLM
    context = get_learning_context(checkpoint["topic"], checkpoint["objectives"])
    relevance_score = calculate_relevance_score(context, checkpoint["objectives"])
    print("\n--- Learning Context ---")
    print(context)
    print("-----------------------")
    print("\n--- RELEVANCE SCORE ---")
    print(f"Relevance Score: {relevance_score}/100")    
    print("-----------------------")

    print(f"Pass Score Required: {checkpoint['success_criteria'] * 100}%")
    print("---------------------------")

    input("Press Enter when you are ready to take the test...")

    return state


# NODE2: Test checkpoint and evaluate
def test_checkpoint(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- TEST ---")

    # Reset scores for this test attempt
    state["scores"] = []

    question_generators = [
        generate_1question,
        generate_2question,
        generate_3question
    ]
    prev= []
    for i, gen_fn in enumerate(question_generators, start=1):
        print(f"\nQuestion {i}:")
        question = gen_fn(checkpoint["topic"], checkpoint["objectives"],prev)
        prev.append(question)
        print(question)

        answer = input("Your answer: ")

        # ALWAYS evaluate immediately
        question_score = evaluate_answer(
            checkpoint["topic"],
            question,
            answer
        )

        print(f"Score for Question {i}: {question_score * 100:.0f}%")
        state["scores"].append(question_score)

    # Calculate average score AFTER all 3 questions
    avg_score = sum(state["scores"]) / len(state["scores"])
    state["score"] = avg_score

    print(f"\n✅ Final Average Score: {avg_score * 100:.0f}%")

    return state



# NODE3: Decide after test using average score
def decide_after_test(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    if state["score"] >= checkpoint["success_criteria"]:
        print("✅ Passed based on success criteria.\n")
        return "post_checkpoint_decision"
    else:
        print("❌ Failed. Explaining concept in simpler terms...\n")
        return "simple_reteach"


# NODE4: Increment checkpoint resets score
def increment_checkpoint(state: LearningState):
    return {
        "checkpoint_index": state["checkpoint_index"],
        "score": 0.0,
        "scores": []  # reset list for new checkpoint
    }


# NODE5: Simple re-teach
def simple_reteach(state: LearningState):
    index = state["checkpoint_index"]
    checkpoint = CHECKPOINTS[index]

    print("\n--- SIMPLE EXPLANATION (RE-TEACH) ---")

    simple_context = get_simple_explanation(checkpoint["topic"], checkpoint["objectives"])
    relevance_score = calculate_relevance_score(simple_context, checkpoint["objectives"])
    print(simple_context)
    print("-----------------------------------")
    print("\n--- RELEVANCE SCORE ---")
    print(f"Relevance Score: {relevance_score}/100")    
    print("-----------------------------------")

    input("\nPress Enter to retry the test...")

    return state


def choose_next_checkpoint(state: LearningState):
    state["checkpoint_index"] = choose_checkpoint()
    state["score"] = 0.0
    state["scores"] = []
    return state


# ----------------------- LangGraph Configuration -----------------------

graph = StateGraph(LearningState)

# Add nodes
graph.add_node("choose_next_checkpoint", choose_next_checkpoint)
graph.add_node("show_checkpoint", show_checkpoint)
graph.add_node("test_checkpoint", test_checkpoint)
graph.add_node("simple_reteach", simple_reteach)
graph.add_node("post_checkpoint_decision", lambda state: state)

# Entry point
graph.set_entry_point("post_checkpoint_decision")

# Conditional edges
graph.add_conditional_edges(
    "post_checkpoint_decision",
    want_to_learn,
    {
        "choose": "choose_next_checkpoint",
        END: END
    }
)

graph.add_edge("choose_next_checkpoint", "show_checkpoint")
graph.add_edge("show_checkpoint", "test_checkpoint")

graph.add_conditional_edges(
    "test_checkpoint",
    decide_after_test
)

graph.add_edge("simple_reteach", "test_checkpoint")

# Compile the graph
learning_graph = graph.compile()

# ----------------------- Invoke -----------------------

initial_state = {
    "checkpoint_index": 0,
    "score": 0.0,
    "scores": []
}

learning_graph.invoke(initial_state)
