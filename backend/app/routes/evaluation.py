from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.gemini_service import evaluate_answer
from app.services.rag_service import rag_service
from app.services.memory_service import memory_service


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

    use_rag: bool = Field(
        default=True,
        description="Whether to ground evaluation with RAG context"
    )


@router.post("/evaluate")
async def evaluate_interview_answer(
    request: EvaluationRequest
):

    try:

        context_chunks = []
        if request.use_rag:
            search_query = f"{request.role}: {request.question} - {request.user_answer}"
            try:
                context_chunks = rag_service.similarity_search(query=search_query, top_k=5)
            except Exception as search_err:
                print(f"[RAG] Warning during evaluation search: {search_err}")
                context_chunks = []

        result = evaluate_answer(
            role=request.role,
            question=request.question,
            user_answer=request.user_answer,
            difficulty=request.difficulty,
            context_chunks=context_chunks
        )

        sources = [
            {
                "source": c.get("source"),
                "page": c.get("page"),
                "score": c.get("score"),
                "snippet": c.get("text", "")[:160] + "..." if len(c.get("text", "")) > 160 else c.get("text", "")
            }
            for c in context_chunks
        ]
        result["rag_enabled"] = bool(context_chunks)
        result["sources"] = sources

        # Automatically persist turn into RAG long-term interview memory
        try:
            memory_service.record_turn(
                role=request.role,
                question=request.question,
                user_answer=request.user_answer,
                evaluation=result,
                difficulty=request.difficulty
            )
            result["memory_recorded"] = True
        except Exception as mem_err:
            print(f"[RAG Memory] Warning recording turn: {mem_err}")
            result["memory_recorded"] = False

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