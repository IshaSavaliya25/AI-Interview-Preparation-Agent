from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.interview import router as interview_router
from app.routes.evaluation import router as evaluation_router
from app.routes.rag import router as rag_router
from app.routes.memory import router as memory_router


app = FastAPI(
    title="AI Interview Preparation Agent",
    description="GenAI-powered personalized interview preparation system with RAG and Memory",
    version="1.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(interview_router)
app.include_router(evaluation_router)
app.include_router(rag_router)
app.include_router(memory_router)


@app.get("/")
def root():

    return {
        "message": "AI Interview Preparation Agent API"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }