import streamlit as st
import requests


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="AI Interview Preparation Agent",
    page_icon="🤖",
    layout="wide"
)


# --------------------------------
# BACKEND URL
# --------------------------------

API_URL = "http://127.0.0.1:8000"


# --------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------

if "questions" not in st.session_state:
    st.session_state.questions = []

if "current_question" not in st.session_state:
    st.session_state.current_question = 0

if "evaluations" not in st.session_state:
    st.session_state.evaluations = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "difficulty" not in st.session_state:
    st.session_state.difficulty = ""

if "interview_sources" not in st.session_state:
    st.session_state.interview_sources = []

if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = None

if "memory_enabled" not in st.session_state:
    st.session_state.memory_enabled = False


# --------------------------------
# HELPER FUNCTIONS
# --------------------------------

def get_rag_status():
    try:
        response = requests.get(f"{API_URL}/api/rag/status", timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {})
        return {}
    except Exception:
        return {}


def upload_rag_document(uploaded_file):
    try:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "application/octet-stream"
            )
        }
        response = requests.post(f"{API_URL}/api/rag/upload", files=files, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "detail": response.text}
    except Exception as e:
        return {"success": False, "detail": str(e)}


def clear_rag_knowledge_base():
    try:
        response = requests.delete(f"{API_URL}/api/rag/clear", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def get_memory_status():
    try:
        response = requests.get(f"{API_URL}/api/memory/status", timeout=10)
        if response.status_code == 200:
            return response.json().get("data", {})
        return {}
    except Exception:
        return {}


def clear_interview_memory():
    try:
        response = requests.delete(f"{API_URL}/api/memory/clear", timeout=10)
        return response.status_code == 200
    except Exception:
        return False


def generate_interview(data):

    try:

        response = requests.post(
            f"{API_URL}/api/interview/generate",
            json=data,
            timeout=180
        )

        if response.status_code == 200:

            return response.json()

        else:

            st.error(
                f"Backend Error: {response.text}"
            )

            return None

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to backend. Make sure FastAPI is running."
        )

        return None

    except Exception as e:

        st.error(str(e))

        return None


def evaluate_answer(data):

    try:

        response = requests.post(
            f"{API_URL}/api/evaluation/evaluate",
            json=data,
            timeout=180
        )

        if response.status_code == 200:

            return response.json()

        else:

            st.error(
                f"Evaluation Error: {response.text}"
            )

            return None

    except Exception as e:

        st.error(str(e))

        return None


# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.title("🤖 AI Interview Agent")

    st.markdown("---")

    st.write(
        "Prepare for your dream job with AI-powered mock interviews."
    )

    st.markdown("---")

    st.subheader("How it works")

    st.write("1️⃣ Select your profile & role")
    st.write("2️⃣ (Optional) Upload resume/notes")
    st.write("3️⃣ Practice AI questions")
    st.write("4️⃣ Get RAG-grounded feedback")

    st.markdown("---")

    st.subheader("📚 RAG Knowledge Base")
    st.caption("Upload your resume, syllabus, or notes (.pdf, .txt, .md)")

    uploaded_doc = st.file_uploader(
        "Upload document",
        type=["pdf", "txt", "md"],
        key="rag_doc_uploader",
        label_visibility="collapsed"
    )

    if uploaded_doc is not None:
        if st.button("📥 Index Document", use_container_width=True):
            with st.spinner(f"Indexing '{uploaded_doc.name}' into FAISS..."):
                res = upload_rag_document(uploaded_doc)
            if res.get("success"):
                st.success(f"Indexed '{uploaded_doc.name}' successfully!")
                st.rerun()
            else:
                st.error(f"Upload failed: {res.get('detail', 'Unknown error')}")

    rag_status = get_rag_status()
    total_docs = rag_status.get("total_documents", 0)
    total_chunks = rag_status.get("total_chunks", 0)
    sources = rag_status.get("sources", [])

    if total_docs > 0:
        st.success(f"🟢 **RAG Active**: {total_docs} doc(s), {total_chunks} chunks")
        with st.expander("📁 Indexed Documents"):
            for s in sources:
                st.write(f"- 📄 `{s}`")
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
            clear_rag_knowledge_base()
            st.rerun()
    else:
        st.info("⚪ **Standard AI Mode** (No documents uploaded)")

    st.markdown("---")

    st.subheader("🧠 RAG Interview Memory")
    st.caption("Remembers your past answers, scores, and weak points across sessions.")

    mem_status = get_memory_status()
    total_mems = mem_status.get("total_memories", 0)
    avg_score = mem_status.get("average_past_score", 0.0)

    if total_mems > 0:
        st.success(f"🧠 **Active**: {total_mems} turn(s) recorded (Avg: {avg_score}/10)")
        with st.expander("🔍 Past Topics & Weaknesses"):
            weaknesses = mem_status.get("past_weaknesses", [])
            if weaknesses:
                st.write("**Topics to improve:**")
                for w in weaknesses:
                    st.write(f"- ⚠️ {w}")
            recent_q = mem_status.get("recent_questions", [])
            if recent_q:
                st.write("**Recent questions:**")
                for rq in recent_q[-3:]:
                    st.caption(f"• {rq}")
        if st.button("🗑️ Reset Interview Memory", use_container_width=True):
            clear_interview_memory()
            st.rerun()
    else:
        st.info("⚪ **No past memory yet** (Complete an interview to build memory)")

    st.markdown("---")

    if st.button("🔄 Start New Interview"):

        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.evaluations = []
        st.session_state.interview_sources = []
        st.session_state.current_evaluation = None
        st.session_state.interview_started = False

        st.rerun()


# --------------------------------
# PAGE 1: INTERVIEW SETUP
# --------------------------------

if not st.session_state.interview_started:

    st.title("AI Interview Preparation Agent")

    st.subheader(
        "Practice personalized interviews powered by Generative AI"
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        role = st.text_input(
            "Target Job Role",
            placeholder="Example: Data Engineer"
        )

        experience = st.selectbox(
            "Experience Level",
            [
                "Fresher",
                "0-1 Years",
                "1-3 Years",
                "3-5 Years",
                "5+ Years"
            ]
        )

        difficulty = st.selectbox(
            "Difficulty Level",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )

    with col2:

        interview_type = st.selectbox(
            "Interview Type",
            [
                "Technical",
                "HR",
                "Behavioral",
                "Mixed"
            ]
        )

        skills_input = st.text_area(
            "Skills",
            placeholder="Python, SQL, Pandas, MySQL"
        )

        number_of_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=10,
            value=5
        )

        use_memory_toggle = st.checkbox(
            "🧠 Adaptive Memory Mode (Avoid repeating past questions & re-test previous weaknesses)",
            value=True
        )

    st.markdown("---")

    if st.button(
        "🚀 Generate My Interview",
        use_container_width=True
    ):

        if not role:

            st.warning(
                "Please enter your target job role."
            )

        elif not skills_input:

            st.warning(
                "Please enter at least one skill."
            )

        else:

            skills = [
                skill.strip()
                for skill in skills_input.split(",")
                if skill.strip()
            ]

            payload = {

                "role": role,
                "experience": experience,
                "difficulty": difficulty,
                "interview_type": interview_type,
                "skills": skills,
                "number_of_questions": number_of_questions,
                "use_rag": True,
                "use_memory": use_memory_toggle

            }

            with st.spinner(
                "AI is generating your personalized interview..."
            ):

                result = generate_interview(payload)

            if result and result.get("success"):

                st.session_state.questions = (
                    result["data"]["questions"]
                )

                st.session_state.role = role

                st.session_state.difficulty = difficulty

                st.session_state.experience = experience

                st.session_state.current_question = 0

                st.session_state.evaluations = []

                st.session_state.interview_sources = (
                    result["data"].get("sources", [])
                )

                st.session_state.memory_enabled = (
                    result["data"].get("memory_enabled", False)
                )

                st.session_state.current_evaluation = None

                st.session_state.interview_started = True

                st.rerun()


# --------------------------------
# PAGE 2: INTERVIEW
# --------------------------------

else:

    questions = st.session_state.questions

    current_index = (
        st.session_state.current_question
    )

    # Interview finished

    if current_index >= len(questions):

        st.title("🎉 Interview Completed!")

        st.subheader("Your Final Performance Report")

        st.markdown("---")

        evaluations = (
            st.session_state.evaluations
        )

        if evaluations:

            average_score = sum(
                evaluation["overall_score"]
                for evaluation in evaluations
            ) / len(evaluations)

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Average Score",
                    f"{average_score:.1f}/10"
                )

            with col2:

                st.metric(
                    "Questions Answered",
                    len(evaluations)
                )

            with col3:

                if average_score >= 8:

                    performance = "Excellent"

                elif average_score >= 6:

                    performance = "Good"

                else:

                    performance = "Needs Improvement"

                st.metric(
                    "Performance",
                    performance
                )

            st.markdown("---")

            st.subheader("Question-wise Performance")

            for i, evaluation in enumerate(evaluations):

                with st.expander(
                    f"Question {i + 1} — Score: {evaluation['overall_score']}/10"
                ):

                    st.write(
                        "**Technical Accuracy:**",
                        evaluation["technical_accuracy"],
                        "/10"
                    )

                    st.write(
                        "**Completeness:**",
                        evaluation["completeness"],
                        "/10"
                    )

                    st.write(
                        "**Communication:**",
                        evaluation["communication"],
                        "/10"
                    )

                    st.write(
                        "**Improvement Suggestion:**"
                    )

                    st.write(
                        evaluation[
                            "improvement_suggestion"
                        ]
                    )

                    if evaluation.get("sources"):
                        doc_names = list({s.get("source") for s in evaluation["sources"] if s.get("source")})
                        if doc_names:
                            st.caption(f"📚 Verified against: `{', '.join(doc_names)}`")

        st.markdown("---")

        if st.button(
            "🔄 Start Another Interview"
        ):

            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.evaluations = []
            st.session_state.interview_sources = []
            st.session_state.current_evaluation = None
            st.session_state.interview_started = False

            st.rerun()


    # --------------------------------
    # CURRENT QUESTION
    # --------------------------------

    else:

        question = questions[current_index]

        st.title("🎯 Mock Interview")

        progress = (
            current_index / len(questions)
        )

        st.progress(progress)

        st.write(
            f"### Question {current_index + 1} of {len(questions)}"
        )

        st.caption(
            f"Category: {question['category']} | "
            f"Difficulty: {question['difficulty']}"
        )

        if st.session_state.interview_sources:
            src_names = list({s.get("source") for s in st.session_state.interview_sources if s.get("source")})
            if src_names:
                st.caption(f"📚 Grounded in candidate documents: `{', '.join(src_names)}`")

        if st.session_state.get("memory_enabled"):
            st.caption("🧠 Adaptive Memory: AI reviewed your past sessions to prevent repeat questions and re-test weak spots.")

        st.markdown("---")

        st.subheader(question["question"])

        st.markdown("---")

        evaluation = st.session_state.current_evaluation

        if evaluation is None:

            user_answer = st.text_area(
                "Your Answer",
                placeholder="Type your answer here...",
                height=200,
                key=f"answer_{current_index}"
            )

            if st.button(
                "Submit Answer 🤖",
                use_container_width=True
            ):

                if not user_answer.strip():

                    st.warning(
                        "Please write an answer before submitting."
                    )

                else:

                    payload = {

                        "role": st.session_state.role,

                        "question": question["question"],

                        "user_answer": user_answer,

                        "difficulty": st.session_state.difficulty,

                        "use_rag": True

                    }

                    with st.spinner(
                        "AI is evaluating your answer..."
                    ):

                        result = evaluate_answer(payload)

                    if result and result.get("success"):

                        eval_data = result["data"]

                        st.session_state.evaluations.append(
                            eval_data
                        )

                        st.session_state.current_evaluation = eval_data

                        st.rerun()

        else:

            st.success(
                "Answer evaluated successfully!"
            )

            st.markdown("---")

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Technical",
                    f"{evaluation['technical_accuracy']}/10"
                )

            with col2:

                st.metric(
                    "Completeness",
                    f"{evaluation['completeness']}/10"
                )

            with col3:

                st.metric(
                    "Communication",
                    f"{evaluation['communication']}/10"
                )

            with col4:

                st.metric(
                    "Overall",
                    f"{evaluation['overall_score']}/10"
                )

            st.markdown("### 💪 Strengths")

            for strength in evaluation["strengths"]:

                st.success(strength)

            st.markdown("### 📈 Areas to Improve")

            for weakness in evaluation["weaknesses"]:

                st.warning(weakness)

            st.markdown("### 💡 AI Improvement Suggestion")

            st.info(
                evaluation[
                    "improvement_suggestion"
                ]
            )

            st.markdown("### ✅ Ideal Answer")

            ideal_answer = evaluation.get("correct_answer", "").strip()
            st.markdown(ideal_answer)

            if evaluation.get("rag_enabled") and evaluation.get("sources"):
                with st.expander("📚 RAG Sources & Context Used for Evaluation"):
                    for s in evaluation["sources"]:
                        st.markdown(f"**Document:** `{s.get('source')}` | **Page:** {s.get('page', 1)} | **Relevance Score:** `{s.get('score', 'N/A')}`")
                        if s.get("snippet"):
                            st.caption(f"> \"{s['snippet']}\"")

            st.markdown("---")

            if st.button(
                "Next Question ➡️",
                use_container_width=True
            ):

                st.session_state.current_question += 1
                st.session_state.current_evaluation = None

                st.rerun()