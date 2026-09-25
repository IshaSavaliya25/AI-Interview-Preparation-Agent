# 🔄 System Workflow & Architecture Documentation

This document provides a comprehensive end-to-end technical overview of the **AI Interview Preparation Agent**, covering the system architecture, the Document RAG pipeline, the Long-Term Interview Memory pipeline, and the user interaction lifecycle.

---

## 1. High-Level System Architecture

```mermaid
graph TD
    User([👤 Candidate / User])

    subgraph "Frontend Layer (Streamlit :8501)"
        UI[Interactive UI]
        Uploader[Document Uploader]
        QView[Sequential Question View]
        EView[Feedback & Scorecard View]
        MView[Memory & History Panel]
    end

    subgraph "Backend API Layer (FastAPI :8000)"
        App[FastAPI Core]
        RAGRouter["/api/rag/* Router"]
        InterviewRouter["/api/interview/* Router"]
        EvalRouter["/api/evaluation/* Router"]
        MemRouter["/api/memory/* Router"]
    end

    subgraph "RAG Services & Vector Storage"
        RAGService[RAG Service]
        MemService[Memory Service]
        ST["Embedding Model<br/>(all-MiniLM-L6-v2)"]
        FAISSDoc["FAISS Knowledge Base Index<br/>(Resumes / Notes / JDs)"]
        FAISSMem["FAISS Interview Memory Index<br/>(Past Q&A / Weaknesses)"]
    end

    subgraph "GenAI Intelligence Layer"
        GeminiService[Gemini Orchestration & Failover]
        GeminiAPI["Google Gemini Models<br/>(gemini-3.5-flash-lite / gemini-3.8-flash)"]
    end

    User <--> UI
    UI --> Uploader & QView & EView & MView

    Uploader -->|Multipart File Upload| RAGRouter
    QView -->|Generate Interview Request| InterviewRouter
    EView -->|Submit Answer Request| EvalRouter
    MView -->|Memory Query / Reset| MemRouter

    RAGRouter --> RAGService
    InterviewRouter --> RAGService & MemService & GeminiService
    EvalRouter --> RAGService & MemService & GeminiService
    MemRouter --> MemService

    RAGService <--> ST
    RAGService <--> FAISSDoc
    MemService <--> ST
    MemService <--> FAISSMem

    GeminiService <--> GeminiAPI
```

---

## 2. Document RAG Pipeline Workflow

The Document RAG pipeline enables the agent to tailor questions and cross-examine answers against external candidate documents (e.g., resumes, job descriptions, technical notes).

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate
    participant UI as Streamlit UI
    participant API as FastAPI Backend
    participant RAG as RAG Service
    participant ST as SentenceTransformers
    participant FAISS as FAISS Vector Store

    User->>UI: Uploads Resume/Notes (.pdf, .txt, .md)
    UI->>API: POST /api/rag/upload (File)
    API->>RAG: add_document(file_bytes, filename)
    Note over RAG: 1. Text Extraction (pypdf for PDF, UTF-8 for TXT/MD)<br/>2. Text Cleaning & Whitespace Normalization<br/>3. Sliding-window Chunking with Overlap
    RAG->>ST: model.encode(chunks)
    ST-->>RAG: 384-dimensional dense vectors
    Note over RAG: Normalize L2 vectors for Cosine Similarity
    RAG->>FAISS: index.add(vectors) & save to disk
    RAG-->>API: {chunks_added, total_documents}
    API-->>UI: 200 OK: "Successfully indexed document"
    UI-->>User: Badge: 🟢 RAG Active (X documents, Y chunks)
```

---

## 3. Question Generation Workflow (Dual RAG: Documents + Memory)

When generating interview questions, the system combines **candidate preferences**, **retrieved document knowledge**, and **past interview history**.

```mermaid
flowchart TD
    Start([User clicks 'Generate My Interview']) --> CollectInputs[Collect Role, Experience, Difficulty, Skills]
    CollectInputs --> CheckRAG{Documents Indexed?}

    CheckRAG -->|Yes| DocSearch[Semantic Search in Document FAISS: Top 5 Chunks]
    CheckRAG -->|No| SkipDoc[Context = Empty]

    DocSearch --> CheckMem{Past Memory Enabled?}
    SkipDoc --> CheckMem

    CheckMem -->|Yes| MemSearch[Semantic Search in Memory FAISS: Top 5 Past Turns]
    CheckMem -->|No| SkipMem[Past Memory = Empty]

    DocSearch & MemSearch --> BuildPrompt[Construct Grounded Prompt with:<br/>1. Role & Candidate Skills<br/>2. Retrieved Document Context<br/>3. Past Questions & Weaknesses]
    SkipDoc & SkipMem --> BuildPrompt

    BuildPrompt --> CallGemini[Call Gemini with Automatic Multi-Model Fallback]
    CallGemini --> ParseJSON[Clean Markdown & Parse Structured JSON]
    ParseJSON --> ValidateCount{Question Count Valid?}

    ValidateCount -->|Yes| ReturnUI[Render Sequential Interactive Interview UI]
    ValidateCount -->|No| RetryOrError[Normalize IDs & Return]
```

---

## 4. Answer Evaluation & Memory Ingestion Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Candidate
    participant UI as Streamlit UI
    participant API as FastAPI Backend
    participant RAG as Document RAG
    participant LLM as Gemini AI Service
    participant MEM as Memory Service (FAISS)

    User->>UI: Types response & clicks "Submit Answer"
    UI->>API: POST /api/evaluation/evaluate
    API->>RAG: similarity_search(role + question + answer, top_k=5)
    RAG-->>API: Top 5 relevant document snippets + page citations

    API->>LLM: evaluate_answer(role, question, answer, context_chunks)
    Note over LLM: Evaluates Rubric:<br/>- Technical Accuracy (0-10)<br/>- Completeness (0-10)<br/>- Communication (0-10)<br/>- Overall Score (0-10)<br/>- Strengths & Weaknesses<br/>- Ideal Answer (paragraphs)<br/>- Improvement Suggestions
    LLM-->>API: Structured Evaluation Scorecard

    API->>MEM: record_turn(role, question, answer, evaluation)
    Note over MEM: Embeds turn & persists to memory.faiss
    MEM-->>API: Memory Saved

    API-->>UI: 200 OK: Evaluation Data + Citations
    UI->>User: Displays Score Metrics, Feedback, Ideal Answer & Citations
    User->>UI: Clicks "Next Question ➡️"
    Note over UI: Increments question index cleanly without state loss
```

---

## 5. RAG Long-Term Memory Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Idle: Fresh Session

    state "Session 1" as S1 {
        Q1: Candidate Answers Question
        E1: AI Evaluates & Notes Weakness
        Q1 --> E1
    }

    state "Vector Store Memory" as VSM {
        M1: Embed Q&A, Score, Weaknesses
        M2: Store in memory.faiss
        M1 --> M2
    }

    state "Session 2 (Adaptive)" as S2 {
        R1: Query Past Weaknesses & Questions
        R2: Gemini Instructed: DO NOT Repeat
        R3: Formulate Questions on Weak Topics
        R1 --> R2
        R2 --> R3
    }

    Idle --> S1: Practice Interview
    E1 --> VSM: Automatic Turn Ingestion
    VSM --> S2: Next Interview Round
    S2 --> [*]: Candidate Masters Concepts
```

---

## 6. API Route Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Server health check. |
| `POST` | `/api/interview/generate` | Generates role-specific questions grounded with Document RAG and adapted via Memory RAG. |
| `POST` | `/api/evaluation/evaluate` | Rubric-evaluates candidate response against document context and auto-records to memory. |
| `POST` | `/api/rag/upload` | Extracts, chunks, embeds, and indexes `.pdf`, `.txt`, or `.md` files. |
| `POST` | `/api/rag/search` | Semantic similarity search returning top $k$ chunks with cosine scores. |
| `GET` | `/api/rag/status` | Current count of indexed documents, chunks, and source names. |
| `DELETE` | `/api/rag/clear` | Clears all documents from the vector store. |
| `GET` | `/api/memory/status` | Current count of remembered interview turns and average historical score. |
| `POST` | `/api/memory/search` | Semantic search over previous interview Q&A turns. |
| `DELETE` | `/api/memory/clear` | Clears interview history memory. |
