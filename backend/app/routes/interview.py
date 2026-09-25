from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini_service import generate_interview_questions
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service


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

    use_rag: bool = Field(
        default=True,
        description="Whether to incorporate retrieved knowledge base context"
    )

    use_memory: bool = Field(
        default=True,
        description="Whether to adapt to past interview performance and avoid repeating questions"
    )


@router.post("/generate")
async def generate_interview(
    request: InterviewRequest
):

    try:

        context_chunks = []
        if request.use_rag:
            query = f"{request.role} {request.interview_type} " + " ".join(request.skills)
            try:
                context_chunks = rag_service.similarity_search(query=query, top_k=5)
            except Exception as search_err:
                print(f"[RAG] Warning during interview search: {search_err}")
                context_chunks = []

        past_memories = []
        if request.use_memory:
            mem_query = f"{request.role} " + " ".join(request.skills)
            try:
                past_memories = memory_service.retrieve_memories(query=mem_query, top_k=5)
            except Exception as mem_err:
                print(f"[RAG Memory] Warning during memory retrieval: {mem_err}")
                past_memories = []

        result = generate_interview_questions(
            role=request.role,
            experience=request.experience,
            difficulty=request.difficulty,
            interview_type=request.interview_type,
            skills=request.skills,
            number_of_questions=request.number_of_questions,
            context_chunks=context_chunks,
            past_memories=past_memories
        )

        sources = [
            {
                "source": c.get("source"),
                "page": c.get("page"),
                "score": c.get("score")
            }
            for c in context_chunks
        ]

        return {
            "success": True,
            "message": "Interview generated successfully",
            "data": {
                "role": request.role,
                "experience": request.experience,
                "difficulty": request.difficulty,
                "interview_type": request.interview_type,
                "skills": request.skills,
                "questions": result["questions"],
                "rag_enabled": bool(context_chunks),
                "sources": sources,
                "memory_enabled": bool(past_memories),
                "memories_used": len(past_memories)
            }
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )