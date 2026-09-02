# AI Interview Agent 🤖

An AI-powered Interview Agent designed to simulate technical and professional interviews. The application helps users practice interview questions, receive AI-generated responses, and improve their interview preparation experience.

## 🚀 Features

* AI-powered interview interaction
* Dynamic interview question generation
* Interactive user interface
* Real-time responses
* Interview practice for different roles and domains
* Frontend built using Streamlit
* Backend API for AI processing
* Secure environment variable configuration
* Easy local setup and execution

## 🛠️ Tech Stack

### Frontend

* Python
* Streamlit
* Requests

### Backend

* Python
* API-based backend
* AI/LLM integration

### Tools

* Python Virtual Environment (venv)
* pip
* Git & GitHub

## 📁 Project Structure

```text
AI-Interview-Agent/
│
├── backend/
│   ├── venv/
│   ├── app.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── venv/
│   ├── app.py
│   └── requirements.txt
│
├── README.md
└── .gitignore
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/IshaSavaliya25/AI-Interview-Preparation-Agent.git
cd AI-Interview-Preparation-Agent
```

### 2. Backend Setup

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

If you don't have a requirements file:

```bash
pip install fastapi uvicorn
```

### 3. Frontend Setup

Open another terminal and navigate to the frontend folder:

```bash
cd frontend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install streamlit requests --timeout 300 --retries 10
```

## ▶️ Running the Application

### Start the Backend

Navigate to the backend folder:

```bash
cd backend
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Run the backend server:

```bash
uvicorn app:app --reload
```

The backend will typically run at:

```text
http://127.0.0.1:8000
```

### Start the Frontend

Open another terminal and navigate to the frontend folder:

```bash
cd frontend
```

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Run Streamlit:

```bash
streamlit run app.py
```

The application will open automatically in your browser.

## 🔐 Environment Variables

Create a `.env` file inside the backend folder.

Example:

```env
API_KEY=your_api_key_here
```

## 📦 Creating requirements.txt

To generate the requirements file:

```bash
pip freeze > requirements.txt
```

For the frontend:

```bash
cd frontend
pip freeze > requirements.txt
```

For the backend:

```bash
cd backend
pip freeze > requirements.txt
```

## 🎯 How It Works

1. The user opens the AI Interview Agent.
2. The user selects an interview role or domain.
3. The AI generates relevant interview questions.
4. The user provides answers.
5. The system processes the answers using AI.
6. Feedback and suggestions are generated.
7. The user can continue practicing and improving.

<!-- ## 🔮 Future Improvements

* Voice-based interview interaction
* Speech-to-text support
* Resume-based interview questions
* Multiple AI models
* Interview history
* User authentication
* Database integration -->

## 👩‍💻 Author

**Isha Savaliya**

