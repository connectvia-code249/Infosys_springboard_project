'''import os
from dotenv import load_dotenv
load_dotenv() 
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_learning_context(topic: str, objectives: list[str]) -> str:
    prompt = f"""
You are a helpful programming tutor.

Topic: {topic}

Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Explain the topic in simple terms with one Python example.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()



def get_simple_explanation(topic: str, objectives: list[str]) -> str:
    prompt = f"""
Explain the following topic in VERY simple terms.

Topic: {topic}

Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Rules:
- Use simple words
- Short sentences
- Explain as if to a beginner
- No technical jargon
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


    return response.choices[0].message.content'''

'''import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

# ---------------- GROQ CLIENT ----------------
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),  # <-- Groq API key
    base_url="https://api.groq.com/openai/v1"  # <-- Groq base URL
)

def get_learning_context(topic: str, objectives: list[str]) -> str:
    prompt = f"""
You are a strict programming tutor.

Topic:
{topic}

Learning Objectives (these define the ONLY allowed scope):
{chr(10).join(f"- {obj}" for obj in objectives)}

Core Rules:
- Explain the topic ONLY to the extent needed to satisfy the objectives
- At least 70–80% of the content must directly support the objectives
- Every paragraph must clearly map to one or more objectives
- Do NOT introduce concepts that are not explicitly required by the objectives
- No historical background, no trivia, no future topics

Coverage Enforcement:
- EACH learning objective must be explained using at least 3 complete sentences
- Do NOT merge explanations of multiple objectives into a single sentence
- If an objective is not sufficiently explained, the output is invalid

Explanation Style:
- Theory-only explanation
- Use real-life analogies ONLY when they directly clarify an objective
- Integrate real-life examples naturally within the explanation
- Do NOT create a separate "example" section
- Keep explanations beginner-friendly but accurate

Strict Restrictions:
- Do NOT include code examples
- Do NOT mention programming languages, syntax, or libraries
- Do NOT explain anything outside the objective list
- If a sentence does not support an objective, exclude it

Quality Control:
- Maintain 70–80% relevance to objectives at all times
- Avoid redundancy while preserving depth
- Repetition should reinforce objectives, not expand scope

Output Format:
- A concise, structured explanation aligned tightly with the objectives
- No headings for examples
- No bullet points unless required for clarity
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def get_simple_explanation(topic: str, objectives: list[str]) -> str:
    prompt = f"""
Explain the topic using ONLY the learning objectives below.

Topic:
{topic}

Learning Objectives (absolute boundary):
{chr(10).join(f"- {obj}" for obj in objectives)}

Language Rules:
- Very simple words
- Short, clear sentences
- No technical jargon unless unavoidable
- Explain like teaching a beginner for the first time

Content Rules:
- Theory-only explanation
- Use real-life situations ONLY if they directly explain an objective
- Blend real-life examples into the explanation naturally
- Do NOT add separate sections or labels for examples

Coverage Enforcement:
- EACH learning objective must be explained using at least 3 complete sentences
- Do NOT merge explanations of multiple objectives into a single sentence
- If an objective is not sufficiently explained, the output is invalid

Strict Restrictions:
- Do NOT include code examples
- Do NOT introduce new ideas beyond the objectives
- Do NOT shrink the explanation too much
- Do NOT oversimplify essential meaning

Quality Control:
- Keep relevance to objectives between 70–80%
- Remove any sentence that does not clearly support an objective
- Ensure clarity without expanding scope
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()



def calculate_relevance_score(
    generated_content: str,
    objectives: list[str]
) -> float:
    prompt = f"""
You are an evaluator.

Your task:
Evaluate how relevant the given explanation is to the learning objectives.

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Explanation to Evaluate:
\"\"\"
{generated_content}
\"\"\"

Scoring Instructions:
- Score EACH learning objective separately from 0–100
- 100 = fully and clearly explained
- 70–89 = partially explained
- below 70 = weak or missing
- Penalize extra or irrelevant concepts
- Compute the average of all objective scores

Final Output Rules:
- Output ONLY the final average score
- Output ONLY a single number
- No text, no symbols, no line breaks
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return float(response.choices[0].message.content.strip())'''


import os
from dotenv import load_dotenv
load_dotenv()



# ---------------- GROQ CLIENT ----------------
from langchain_groq import ChatGroq
import os

llm= ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)


def get_learning_context(topic: str, objectives: list[str]) -> str:
    prompt = f"""
You are a strict programming tutor.

Topic:
{topic}

Learning Objectives (these define the ONLY allowed scope):
{chr(10).join(f"- {obj}" for obj in objectives)}

Core Rules:
- Explain the topic ONLY to the extent needed to satisfy the objectives
- At least 70–80% of the content must directly support the objectives
- Every paragraph must clearly map to one or more objectives
- Do NOT introduce concepts that are not explicitly required by the objectives
- No historical background, no trivia, no future topics

Coverage Enforcement:
- EACH learning objective must be explained using at least 3 complete sentences
- Do NOT merge explanations of multiple objectives into a single sentence
- If an objective is not sufficiently explained, the output is invalid

Explanation Style:
- Theory-only explanation
- Use real-life analogies ONLY when they directly clarify an objective
- Integrate real-life examples naturally within the explanation
- Do NOT create a separate "example" section
- Keep explanations beginner-friendly but accurate

Strict Restrictions:
- Do NOT include code examples
- Do NOT mention programming languages, syntax, or libraries
- Do NOT explain anything outside the objective list
- If a sentence does not support an objective, exclude it

Quality Control:
- Maintain 70–80% relevance to objectives at all times
- Avoid redundancy while preserving depth
- Repetition should reinforce objectives, not expand scope

Output Format:
- A concise, structured explanation aligned tightly with the objectives
- No headings for examples
- No bullet points unless required for clarity
"""

    response = llm.invoke(prompt)
    return response.content



def get_simple_explanation(topic: str, objectives: list[str]) -> str:
    prompt = f"""
Explain the topic using ONLY the learning objectives below.

Topic:
{topic}

Learning Objectives (absolute boundary):
{chr(10).join(f"- {obj}" for obj in objectives)}

Language Rules:
- Very simple words
- Short, clear sentences
- No technical jargon unless unavoidable
- Explain like teaching a beginner for the first time

Content Rules:
- Theory-only explanation
- Use real-life situations ONLY if they directly explain an objective
- Blend real-life examples into the explanation naturally
- Do NOT add separate sections or labels for examples

Coverage Enforcement:
- EACH learning objective must be explained using at least 3 complete sentences
- Do NOT merge explanations of multiple objectives into a single sentence
- If an objective is not sufficiently explained, the output is invalid

Strict Restrictions:
- Do NOT include code examples
- Do NOT introduce new ideas beyond the objectives
- Do NOT shrink the explanation too much
- Do NOT oversimplify essential meaning

Quality Control:
- Keep relevance to objectives between 70–80%
- Remove any sentence that does not clearly support an objective
- Ensure clarity without expanding scope
"""

    response = llm.invoke(prompt)
    return response.content



def calculate_relevance_score(
    generated_content: str,
    objectives: list[str]
) -> float:
    prompt = f"""
You are an evaluator.

Your task:
Evaluate how relevant the given explanation is to the learning objectives.

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in objectives)}

Explanation to Evaluate:
\"\"\"
{generated_content}
\"\"\"

Scoring Instructions:
- Score EACH learning objective separately from 0–100
- 100 = fully and clearly explained
- 70–89 = partially explained
- below 70 = weak or missing
- Penalize extra or irrelevant concepts
- Compute the average of all objective scores

Final Output Rules:
- Output ONLY the final average score
- Output ONLY a single number
- No text, no symbols, no line breaks
"""

    response = llm.invoke(prompt)
    return response.content




