from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import rag_service

router = APIRouter(
    prefix="/api/rag",
    tags=["RAG Knowledge Base"]
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query string")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant chunks to retrieve")


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Extract text, chunk, compute embeddings, and store into FAISS vector database.
    Supported file types: .pdf, .txt, .md
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    ext = file.filename.lower().split(".")[-1]
    if ext not in ["pdf", "txt", "md"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '.{ext}'. Supported formats: .pdf, .txt, .md"
        )

    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        result = rag_service.add_document(content, file.filename)

        return {
            "success": True,
            "message": f"Successfully indexed '{file.filename}' into vector store.",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")


@router.post("/search")
async def search_knowledge_base(request: SearchRequest):
    """
    Perform semantic vector search using cosine similarity to retrieve top-k chunks.
    """
    try:
        results = rag_service.similarity_search(query=request.query, top_k=request.top_k)
        return {
            "success": True,
            "query": request.query,
            "count": len(results),
            "data": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/status")
async def get_rag_status():
    """
    Get current FAISS index status, number of documents, and chunk count.
    """
    try:
        status = rag_service.get_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch RAG status: {str(e)}")


@router.delete("/clear")
async def clear_rag_index():
    """
    Reset and clear all indexed documents from the vector store.
    """
    try:
        result = rag_service.clear_index()
        return {
            "success": True,
            "message": result["message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")
