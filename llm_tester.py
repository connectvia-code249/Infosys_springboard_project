
'''import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_1question(topic: str, objectives: list[str]) -> str:
    """
    Generates ONE short conceptual question (one-word answer type) per call.
    Ensures the model does NOT return the answer.
    """
    prompt = f"""
Generate ONE short conceptual question that can be answered in ONE WORD.

Topic: {topic}

Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Important: ONLY provide the question. DO NOT include the answer or any hints.
Keep it short and clear. 
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_2question(topic: str, objectives: list[str]) -> str:
    """
    Generates ONE short conceptual question (one-word answer type) per call.
    Ensures the model does NOT return the answer.
    """
    prompt = f"""
Generate ONE short conceptual question that can be answered as true/false.

Topic: {topic}

Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Important: ONLY provide the question. DO NOT include the answer or any hints.
Keep it short and clear. 
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def generate_3question(topic: str, objectives: list[str]) -> str:
    """
    Generates ONE short conceptual question (one-word answer type) per call.
    Ensures the model does NOT return the answer.
    """
    prompt = f"""
Generate ONE short conceptual question that can be answered in one or two sentences.

Topic: {topic}

Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Important: ONLY provide the question. DO NOT include the answer or any hints.
Keep it short and clear. 
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def evaluate_answer(topic: str, question: str, answer: str) -> float:
    """
    Evaluates the learner's answer, returns a score between 0 and 1.
    """
    prompt = f"""
You are an evaluator.

Topic: {topic}
Question: {question}
Learner Answer: {answer}

Evaluate the answer and return ONLY a number between 0 and 1.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return float(response.choices[0].message.content.strip())'''

'''import os
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- GROQ CLIENT SETUP ----------------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- SHARED MCQ PROMPT BUILDER ----------------
def _mcq_prompt(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prev_qs = "\n".join(f"- {q}" for q in previous_questions) if previous_questions else "None"

    return f"""
Generate ONE multiple-choice conceptual question (MCQ) with four options labeled A, B, C, D.

Topic:
{topic}

Context / Learning Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Previously Asked Questions (DO NOT repeat or paraphrase):
{prev_qs}

Rules:
- The question must be directly based on the given context.
- The correct answer MUST be inferable from the context/objectives.
- Exactly ONE option must be correct.
- Do NOT mention which option is correct.
- Do NOT include explanations, hints, or extra text.

Output strictly in this format:

Question: <question text>
A. <option>
B. <option>
C. <option>
D. <option>
"""

# ---------------- QUESTION GENERATORS ----------------
def generate_1question(topic: str, objectives: list[str], previous_questions=None) -> str:
    if previous_questions is None:
        previous_questions = []

    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_2question(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def generate_3question(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# ---------------- ANSWER EVALUATION ----------------
def evaluate_answer(topic: str, question: str, answer: str) -> float:
    prompt = f"""
You are an evaluator.

Topic: {topic}
Question: {question}
Learner Answer: {answer}

Evaluate correctness and return ONLY a number between 0 and 1.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return float(response.choices[0].message.content.strip())'''


import os
from dotenv import load_dotenv


# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- GROQ CLIENT SETUP ----------------
from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)


# ---------------- SHARED MCQ PROMPT BUILDER ----------------
def _mcq_prompt(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prev_qs = "\n".join(f"- {q}" for q in previous_questions) if previous_questions else "None"

    return f"""
Generate ONE multiple-choice conceptual question (MCQ) with four options labeled A, B, C, D.

Topic:
{topic}

Context / Learning Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Previously Asked Questions (DO NOT repeat or paraphrase):
{prev_qs}

Rules:
- The question must be directly based on the given context.
- The correct answer MUST be inferable from the context/objectives.
- Exactly ONE option must be correct.
- Do NOT mention which option is correct.
- Do NOT include explanations, hints, or extra text.

Output strictly in this format:

Question: <question text>
A. <option>
B. <option>
C. <option>
D. <option>
"""

# ---------------- QUESTION GENERATORS ----------------
def generate_1question(topic: str, objectives: list[str], previous_questions=None) -> str:
    if previous_questions is None:
        previous_questions = []

    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = llm.invoke(prompt)
    return response.content


def generate_2question(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = llm.invoke(prompt)
    return response.content


def generate_3question(topic: str, objectives: list[str], previous_questions: list[str]) -> str:
    prompt = _mcq_prompt(topic, objectives, previous_questions)

    response = llm.invoke(prompt)
    return response.content

# ---------------- ANSWER EVALUATION ----------------
def evaluate_answer(topic: str, question: str, answer: str) -> float:
    prompt = f"""
You are an evaluator.

Topic: {topic}
Question: {question}
Learner Answer: {answer}

Evaluate correctness and return ONLY a number between 0 and 1. 
"""

    response = llm.invoke(prompt)

    try:
        score = float(response.content.strip())
    except ValueError:
        score = 0.0  # fallback if LLM misbehaves

    return score