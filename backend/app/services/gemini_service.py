import json
import re

from google import genai

from app.config import (
    GEMINI_API_KEY,
    PRIMARY_MODEL,
    FALLBACK_MODEL
)


client = genai.Client(api_key=GEMINI_API_KEY)


def call_gemini(prompt: str):

    models = [
        PRIMARY_MODEL,
        "gemini-flash-latest",
        FALLBACK_MODEL
    ]

    last_error = None

    for model in models:

        try:

            print(f"Trying model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.text:
                return response.text

        except Exception as e:

            last_error = e

            print(f"Model failed: {model}")
            print(str(e))

    raise Exception(
        f"All Gemini models failed: {str(last_error)}"
    )


def generate_interview_questions(
    role: str,
    experience: str,
    difficulty: str,
    interview_type: str,
    skills: list[str],
    number_of_questions: int = 5
):

    prompt = f"""
You are an expert technical interviewer.

Generate exactly {number_of_questions} interview questions.

Candidate Details:

Role: {role}

Experience: {experience}

Difficulty: {difficulty}

Interview Type: {interview_type}

Skills: {", ".join(skills)}

Return ONLY valid JSON.

Use exactly this format:

{{
    "questions": [
        {{
            "id": 1,
            "question": "Interview question here",
            "category": "Skill or topic",
            "difficulty": "{difficulty}"
        }}
    ]
}}

Rules:

- Generate exactly {number_of_questions} questions.
- Questions must be relevant to the role.
- Do not repeat questions.
- Do not include explanations.
- Do not include markdown.
- Return valid JSON only.
"""

    response_text = call_gemini(prompt)

    # Remove markdown JSON formatting if Gemini adds it
    response_text = re.sub(
        r"```json|```",
        "",
        response_text
    ).strip()

    try:

        return json.loads(response_text)

    except json.JSONDecodeError:

        raise Exception(
            "AI returned invalid JSON. Please try again."
        )

def evaluate_answer(
    role: str,
    question: str,
    user_answer: str,
    difficulty: str
):

    prompt = f"""
You are an expert technical interviewer evaluating a candidate.

Candidate Role:
{role}

Question:
{question}

Candidate Answer:
{user_answer}

Difficulty:
{difficulty}

Evaluate the answer fairly.

Evaluate these criteria:

1. Technical Accuracy (0-10)
2. Completeness (0-10)
3. Communication Clarity (0-10)
4. Overall Score (0-10)

Also provide:

- strengths
- weaknesses
- correct_answer
- improvement_suggestion

Return ONLY valid JSON.

Use exactly this format:

{{
    "technical_accuracy": 0,
    "completeness": 0,
    "communication": 0,
    "overall_score": 0,
    "strengths": [
        "strength 1"
    ],
    "weaknesses": [
        "weakness 1"
    ],
    "correct_answer": "Ideal answer here",
    "improvement_suggestion": "How the candidate can improve"
}}

Rules:

- Be constructive.
- Do not give unrealistic scores.
- Consider the difficulty level.
- Do not use markdown.
- Return valid JSON only.
"""

    response_text = call_gemini(prompt)

    import json
    import re

    response_text = re.sub(
        r"```json|```",
        "",
        response_text
    ).strip()

    try:

        return json.loads(response_text)

    except json.JSONDecodeError:

        raise Exception(
            "AI returned invalid evaluation JSON."
        )