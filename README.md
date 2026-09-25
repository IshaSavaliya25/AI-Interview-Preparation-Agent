# AI Interview Preparation Agent 🤖

An advanced, full-stack **Generative AI Mock Interview Platform** featuring **Document RAG (Retrieval-Augmented Generation)**, **Long-Term Interview Memory**, and **LLM-as-a-Judge Automated Rubric Evaluation** powered by **FastAPI**, **Streamlit**, and **Google Gemini**.

[![Architecture Workflow](https://img.shields.io/badge/Architecture-Workflow_Guide-blue)](WORKFLOW.md)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-brightgreen)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%20API-4285F4)](https://ai.google.dev/)
[![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS%20CPU-yellow)](https://github.com/facebookresearch/faiss)

---

## 🚀 Key Features

* **📄 Document RAG Knowledge Base:**
  * Upload resumes, job descriptions, or technical notes (`.pdf`, `.txt`, `.md`).
  * Text extraction via `pypdf` with page tracking and word-boundary sliding-window chunking.
  * Dense vector embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`).
  * High-performance cosine similarity retrieval via `faiss.IndexFlatIP`.
  * Questions and evaluations are grounded in your actual documents with source/page citations.

* **🧠 Long-Term RAG Interview Memory:**
  * Automatically embeds and stores each completed interview turn (question, candidate answer, score, strengths, and weaknesses).
  * Prevents repeating questions across sessions.
  * Formulates adaptive questions that re-test previous weak areas.

* **⚖️ LLM-as-a-Judge Rubric Evaluation:**
  * Multi-dimensional scoring on a 0–10 scale: *Technical Accuracy*, *Completeness*, *Communication Clarity*, and *Overall Score*.
  * Actionable feedback: Strengths, Areas to Improve, Improvement Suggestions, and an **Ideal Answer formatted in readable paragraphs**.

* **🛡️ Resilient Model Orchestration:**
  * Multi-model cascading fallback (`gemini-3.5-flash-lite` $\rightarrow$ `gemini-3.8-flash` $\rightarrow$ `gemini-3.1-flash-lite`).
  * Automatic JSON extraction and schema validation.

* **📊 Performance Analytics:**
  * Live interview progress indicator.
  * End-of-interview report with average performance tier and question-by-question breakdown.

---

## 🛠️ Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Streamlit, Requests |
| **Backend API** | FastAPI, Uvicorn, Pydantic, Python-Multipart |
| **Generative AI** | Google Gemini (`google-genai` SDK: `gemini-3.5-flash-lite`, `gemini-3.8-flash`) |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`, 384 dimensions) |
| **Vector Database**| FAISS (Facebook AI Similarity Search - `faiss-cpu`) |
| **Document Processing**| PyPDF (`pypdf`), Regex-based cleaning |

---

## 📁 Project Structure

```text
AI-Interview-Agent/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── interview.py         # /api/interview endpoints (generation)
│   │   │   ├── evaluation.py        # /api/evaluation endpoints (rubric scoring)
│   │   │   ├── rag.py               # /api/rag endpoints (document upload, search, status)
│   │   │   └── memory.py            # /api/memory endpoints (history, search, reset)
│   │   ├── services/
│   │   │   ├── gemini_service.py    # Gemini client, prompting, fallback, JSON parsing
│   │   │   ├── rag_service.py       # PDF/text extraction, chunking, FAISS index
│   │   │   └── memory_service.py    # Conversational RAG memory persistence
│   │   ├── config.py                # Environment configuration & model settings
│   │   └── main.py                  # FastAPI application setup & CORS
│   ├── requirements.txt             # Backend dependencies
│   └── .env                         # API keys and model configuration
│
├── frontend/
│   ├── app.py                       # Streamlit UI (Setup, Interview, Scorecards)
│   └── requirements.txt             # Frontend dependencies
│
├── WORKFLOW.md                      # Detailed technical architecture & sequence diagrams
├── README.md                        # Project documentation
└── .gitignore                       # Git ignore rules (virtualenvs, FAISS data, .env)
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/IshaSavaliya25/AI-Interview-Preparation-Agent.git
cd AI-Interview-Preparation-Agent
```

---

### 2. Backend Setup

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the `backend/` directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash-lite  
   ```
   *(Get your free API key at [Google AI Studio](https://aistudio.google.com/)).*

---

### 3. Frontend Setup

1. Open a second terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Create and activate a Python virtual environment:
   * **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Running the Application

### 1. Start the Backend API
In the backend terminal (with `venv` activated):
```bash
uvicorn app.main:app --reload --port 8000
```
Backend will be live at: `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

### 2. Start the Frontend UI
In the frontend terminal (with `venv` activated):
```bash
streamlit run app.py
```
The application will automatically open in your default browser at: `http://localhost:8501`.

---

## 🎯 How It Works

1. **Upload Resume or Notes (Optional RAG):**
   * Use the sidebar **📚 RAG Knowledge Base** to upload `.pdf`, `.txt`, or `.md` files.
   * Chunks are automatically embedded and saved in FAISS.
2. **Select Interview Profile:**
   * Enter your target job role, experience level, difficulty, interview type, and key skills.
   * Enable **🧠 Adaptive Memory Mode** to take advantage of past interview history.
3. **Practice Personalized Questions:**
   * The AI generates questions tailored to your skills, documents, and historical weak spots.
4. **Receive Instant Rubric Evaluation:**
   * Submit your response to view quantitative scores ($0-10$), qualitative strengths, weak points, verified document citations, and an **Ideal Answer in clear paragraphs**.
5. **Review Performance Report:**
   * View average score, performance tier (*Excellent*, *Good*, *Needs Improvement*), and question-by-question breakdown.

---

## 📡 API Reference Summary

For full architecture flowcharts and sequence diagrams, see [WORKFLOW.md](WORKFLOW.md).

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | API health check |
| `POST` | `/api/interview/generate` | Generates role-specific questions using Document & Memory RAG |
| `POST` | `/api/evaluation/evaluate` | Evaluates answer against rubric and records turn to memory |
| `POST` | `/api/rag/upload` | Uploads and indexes `.pdf`, `.txt`, `.md` into FAISS |
| `POST` | `/api/rag/search` | Semantic search over uploaded documents |
| `GET` | `/api/rag/status` | Current document count and chunk stats |
| `DELETE` | `/api/rag/clear` | Clears document knowledge base |
| `GET` | `/api/memory/status` | Interview memory history and average score |
| `POST` | `/api/memory/search` | Semantic search over previous interview Q&As |
| `DELETE` | `/api/memory/clear` | Resets interview memory history |

---

## 👩‍💻 Author

**Isha Savaliya**
* GitHub: [@IshaSavaliya25](https://github.com/IshaSavaliya25)
