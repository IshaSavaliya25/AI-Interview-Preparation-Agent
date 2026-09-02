from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini_service import generate_interview_questions


router = APIRouter(
    prefix="/api/interview",
    tags=["Interview"]
)


class InterviewRequest(BaseModel):

    role: str
    experience: str
    difficulty: str
    interview_type: str

    skills: list[str] = Field(
        default_factory=list
    )

    number_of_questions: int = Field(
        default=5,
        ge=1,
        le=20
    )


@router.post("/generate")
async def generate_interview(
    request: InterviewRequest
):

    try:

        result = generate_interview_questions(
            role=request.role,
            experience=request.experience,
            difficulty=request.difficulty,
            interview_type=request.interview_type,
            skills=request.skills,
            number_of_questions=request.number_of_questions
        )

        return {
            "success": True,
            "message": "Interview generated successfully",
            "data": {
                "role": request.role,
                "experience": request.experience,
                "difficulty": request.difficulty,
                "interview_type": request.interview_type,
                "skills": request.skills,
                "questions": result["questions"]
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )