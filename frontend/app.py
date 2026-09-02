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


# --------------------------------
# HELPER FUNCTIONS
# --------------------------------

def generate_interview(data):

    try:

        response = requests.post(
            f"{API_URL}/api/interview/generate",
            json=data,
            timeout=60
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
            timeout=60
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

    st.write("1️⃣ Select your profile")
    st.write("2️⃣ Generate interview")
    st.write("3️⃣ Answer questions")
    st.write("4️⃣ Get AI feedback")

    st.markdown("---")

    if st.button("🔄 Start New Interview"):

        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.evaluations = []
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
                "number_of_questions": number_of_questions

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

        st.markdown("---")

        if st.button(
            "🔄 Start Another Interview"
        ):

            st.session_state.questions = []
            st.session_state.current_question = 0
            st.session_state.evaluations = []
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

        st.markdown("---")

        st.subheader(question["question"])

        st.markdown("---")

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

                    "difficulty": st.session_state.difficulty

                }

                with st.spinner(
                    "AI is evaluating your answer..."
                ):

                    result = evaluate_answer(payload)

                if result and result.get("success"):

                    evaluation = result["data"]

                    st.session_state.evaluations.append(
                        evaluation
                    )

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

                    st.code(
                        evaluation["correct_answer"]
                    )

                    if st.button(
                        "Next Question ➡️",
                        use_container_width=True
                    ):

                        st.session_state.current_question += 1

                        st.rerun()