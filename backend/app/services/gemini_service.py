import json
import re

from google import genai

from app.config import (
    GEMINI_API_KEY,
    PRIMARY_MODEL,
    FALLBACK_MODEL
)


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(api_key=GEMINI_API_KEY)


# ==========================================
# CALL GEMINI WITH FALLBACK MODELS
# ==========================================

def call_gemini(prompt: str):

    models = [
        PRIMARY_MODEL,
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash",
        FALLBACK_MODEL
    ]

    # Remove duplicate and empty model names
    models = list(
        dict.fromkeys(
            model for model in models if model
        )
    )

    last_error = None

    for model in models:

        try:

            print(f"\nTrying Gemini model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response and response.text:

                print(
                    f"Successfully received response from: {model}"
                )

                return response.text

            print(
                f"Empty response received from model: {model}"
            )

        except Exception as e:

            last_error = e

            print(f"Model failed: {model}")
            print(f"Error: {str(e)}")

    raise Exception(
        f"All Gemini models failed. Last error: {str(last_error)}"
    )


# ==========================================
# CLEAN GEMINI JSON RESPONSE
# ==========================================

def clean_json_response(response_text: str):

    if not response_text:
        raise Exception("Gemini returned an empty response.")

    response_text = response_text.strip()

    # Remove markdown code blocks
    response_text = re.sub(
        r"^```(?:json)?\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    response_text = re.sub(
        r"\s*```$",
        "",
        response_text
    )

    response_text = response_text.strip()

    # Extract JSON object
    json_match = re.search(
        r"\{.*\}",
        response_text,
        re.DOTALL
    )

    if json_match:
        response_text = json_match.group(0)

    return response_text


# ==========================================
# GENERATE INTERVIEW QUESTIONS
# ==========================================

def generate_interview_questions(
    role: str,
    experience: str,
    difficulty: str,
    interview_type: str,
    skills: list[str],
    number_of_questions: int = 5,
    context_chunks: list[dict] = None,
    past_memories: list[dict] = None
):

    skills_text = ", ".join(skills) if skills else "Not specified"

    context_prompt = ""
    if context_chunks:
        context_parts = []
        for idx, chunk in enumerate(context_chunks, start=1):
            src = chunk.get("source", "Document")
            pg = chunk.get("page", 1)
            txt = chunk.get("text", "").strip()
            context_parts.append(f"[Chunk {idx} | Source: {src}, Page: {pg}]\n{txt}")

        joined_chunks = "\n\n".join(context_parts)
        context_prompt = f"""
KNOWLEDGE BASE CONTEXT (Retrieved from candidate documents/resume):
--------------------------------------------------
{joined_chunks}
--------------------------------------------------

CONTEXT GROUNDING INSTRUCTIONS:
- Tailor questions to probe the candidate's actual projects, tools, frameworks, and domain concepts identified in the above context.
- Keep the requested difficulty, role, and skills aligned.
"""

    memory_prompt = ""
    if past_memories:
        memory_parts = []
        for idx, mem in enumerate(past_memories, start=1):
            q_text = mem.get("question", "")
            score = mem.get("score", "N/A")
            weaknesses = ", ".join(mem.get("weaknesses", [])) or "None noted"
            memory_parts.append(
                f"[Past Turn {idx}]\n"
                f"- Previously Asked Question: \"{q_text}\"\n"
                f"- Past Score: {score}/10\n"
                f"- Past Weaknesses: {weaknesses}"
            )
        joined_memories = "\n\n".join(memory_parts)
        memory_prompt = f"""
PAST INTERVIEW MEMORY (Retrieved from candidate's previous sessions):
--------------------------------------------------
{joined_memories}
--------------------------------------------------

MEMORY ADAPTATION INSTRUCTIONS:
1. STRICTLY DO NOT REPEAT any of the questions previously asked above.
2. If past weaknesses are noted, formulate questions that test if the candidate has improved in those specific topics.
"""

    prompt = f"""
You are an expert AI interviewer.

Generate EXACTLY {number_of_questions} unique interview questions.

CANDIDATE DETAILS:

Role: {role}
Experience Level: {experience}
Difficulty Level: {difficulty}
Interview Type: {interview_type}
Skills: {skills_text}
{context_prompt}
{memory_prompt}
STRICT REQUIREMENTS:

1. Generate exactly {number_of_questions} questions.
2. The questions array must contain exactly {number_of_questions} objects.
3. Each question must have a unique ID.
4. IDs must start from 1 and continue sequentially.
5. Questions must be relevant to the candidate's role.
6. Questions must consider the candidate's skills and referenced context.
7. Questions must match the requested difficulty.
8. Do not repeat questions.
9. Do not include answers.
10. Do not include explanations.
11. Do not use markdown.
12. Return only valid JSON.

RETURN FORMAT:

{{
    "questions": [
        {{
            "id": 1,
            "question": "Interview question here",
            "category": "Relevant skill or topic",
            "difficulty": "{difficulty}"
        }}
    ]
}}

IMPORTANT:

Generate exactly {number_of_questions} question objects inside
the questions array.

Return only the JSON object.
"""

    print("\n" + "=" * 50)
    print("GENERATING INTERVIEW QUESTIONS")
    print("=" * 50)

    print(f"Role: {role}")
    print(f"Number requested: {number_of_questions}")

    response_text = call_gemini(prompt)

    print("\nRaw Gemini Response:")
    print(response_text)

    cleaned_response = clean_json_response(response_text)

    try:

        result = json.loads(cleaned_response)

    except json.JSONDecodeError as e:

        print("\nInvalid JSON received:")
        print(cleaned_response)

        raise Exception(
            f"AI returned invalid JSON: {str(e)}"
        )

    # Validate response

    if not isinstance(result, dict):

        raise Exception(
            "AI response must be a JSON object."
        )

    if "questions" not in result:

        raise Exception(
            "AI response does not contain a questions field."
        )

    if not isinstance(result["questions"], list):

        raise Exception(
            "Questions must be a JSON array."
        )

    generated_count = len(result["questions"])

    print(f"\nQuestions generated: {generated_count}")
    print(f"Questions requested: {number_of_questions}")

    # Ensure exact count

    if generated_count != number_of_questions:

        raise Exception(
            f"AI generated {generated_count} questions, "
            f"but {number_of_questions} were requested."
        )

    # Validate questions

    required_fields = [
        "id",
        "question",
        "category",
        "difficulty"
    ]

    for index, question_data in enumerate(
        result["questions"],
        start=1
    ):

        if not isinstance(question_data, dict):

            raise Exception(
                f"Question {index} is invalid."
            )

        for field in required_fields:

            if field not in question_data:

                raise Exception(
                    f"Question {index} is missing field: {field}"
                )

        # Normalize ID
        question_data["id"] = index

        # Ensure correct difficulty
        question_data["difficulty"] = difficulty

    print("\nInterview questions generated successfully!")

    return result


# ==========================================
# EVALUATE USER ANSWER
# ==========================================

def evaluate_answer(
    role: str,
    question: str,
    user_answer: str,
    difficulty: str,
    context_chunks: list[dict] = None
):

    context_prompt = ""
    if context_chunks:
        context_parts = []
        for idx, chunk in enumerate(context_chunks, start=1):
            src = chunk.get("source", "Document")
            pg = chunk.get("page", 1)
            txt = chunk.get("text", "").strip()
            context_parts.append(f"[Chunk {idx} | Source: {src}, Page: {pg}]\n{txt}")

        joined_chunks = "\n\n".join(context_parts)
        context_prompt = f"""
KNOWLEDGE BASE CONTEXT (Retrieved from candidate documents/resume):
--------------------------------------------------
{joined_chunks}
--------------------------------------------------

CONTEXT GROUNDING INSTRUCTIONS:
- Use the knowledge base context above to verify technical accuracy and check whether the candidate's answer aligns with specific tools, frameworks, metrics, or methods referenced in the documentation.
"""

    prompt = f"""
You are an expert AI technical interviewer.

Evaluate the candidate's answer fairly and constructively.

CANDIDATE ROLE:
{role}

QUESTION:
{question}

CANDIDATE ANSWER:
{user_answer}

DIFFICULTY LEVEL:
{difficulty}
{context_prompt}
Evaluate:

1. Technical Accuracy from 0 to 10
2. Completeness from 0 to 10
3. Communication Clarity from 0 to 10
4. Overall Score from 0 to 10

Also provide:

- strengths
- weaknesses
- correct_answer (written in clear, well-structured paragraphs explaining the ideal solution)
- improvement_suggestion

Return ONLY valid JSON.

Use this format:

{{
    "technical_accuracy": 0,
    "completeness": 0,
    "communication": 0,
    "overall_score": 0,
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "weaknesses": [
        "Weakness 1",
        "Weakness 2"
    ],
    "correct_answer": "Ideal answer",
    "improvement_suggestion": "How to improve"
}}

Do not include markdown.
Do not include text outside JSON.
"""

    print("\n" + "=" * 50)
    print("EVALUATING ANSWER")
    print("=" * 50)

    response_text = call_gemini(prompt)

    print("\nRaw Evaluation Response:")
    print(response_text)

    cleaned_response = clean_json_response(response_text)

    try:

        result = json.loads(cleaned_response)

    except json.JSONDecodeError as e:

        print("\nInvalid Evaluation JSON:")
        print(cleaned_response)

        raise Exception(
            f"AI returned invalid evaluation JSON: {str(e)}"
        )

    required_fields = [
        "technical_accuracy",
        "completeness",
        "communication",
        "overall_score",
        "strengths",
        "weaknesses",
        "correct_answer",
        "improvement_suggestion"
    ]

    for field in required_fields:

        if field not in result:

            raise Exception(
                f"AI evaluation missing field: {field}"
            )

    # Normalize scores

    score_fields = [
        "technical_accuracy",
        "completeness",
        "communication",
        "overall_score"
    ]

    for field in score_fields:

        try:

            score = float(result[field])

            score = max(
                0,
                min(10, score)
            )

            result[field] = round(score, 1)

        except (ValueError, TypeError):

            result[field] = 0

    # Ensure strengths is list

    if not isinstance(result["strengths"], list):

        result["strengths"] = [
            str(result["strengths"])
        ]

    # Ensure weaknesses is list

    if not isinstance(result["weaknesses"], list):

        result["weaknesses"] = [
            str(result["weaknesses"])
        ]

    print("\nAnswer evaluated successfully!")

    return result