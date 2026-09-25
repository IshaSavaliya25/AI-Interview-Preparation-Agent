from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.memory_service import memory_service

router = APIRouter(
    prefix="/api/memory",
    tags=["RAG Interview Memory"]
)


class MemorySearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@router.get("/status")
async def get_memory_status():
    """
    Get current long-term interview memory status and past performance stats.
    """
    try:
        status = memory_service.get_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    """
    Semantically search past interview questions, answers, and weak points.
    """
    try:
        results = memory_service.retrieve_memories(request.query, request.top_k)
        return {
            "success": True,
            "query": request.query,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_memory():
    """
    Clear all past interview memories.
    """
    try:
        res = memory_service.clear_memory()
        return {
            "success": True,
            "message": res["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
