from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini_service import evaluate_answer


router = APIRouter(
    prefix="/api/evaluation",
    tags=["Answer Evaluation"]
)


class EvaluationRequest(BaseModel):

    role: str = Field(...)

    question: str = Field(...)

    user_answer: str = Field(
        ...,
        min_length=1
    )

    difficulty: str = Field(
        default="Medium"
    )


@router.post("/evaluate")
async def evaluate_interview_answer(
    request: EvaluationRequest
):

    try:

        result = evaluate_answer(
            role=request.role,
            question=request.question,
            user_answer=request.user_answer,
            difficulty=request.difficulty
        )

        return {
            "success": True,
            "message": "Answer evaluated successfully",
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )   