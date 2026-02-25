# 🚢 Titanic Data Chat Agent

An AI-powered conversational data analyst built using **FastAPI**, **LangChain (v1+)**, **Gemini (Google Generative AI)**, and **Streamlit**.

This project allows users to ask natural language questions about the Titanic dataset and receive:

* ✅ Accurate numerical answers
* 📊 Automatically generated visualizations
* 🔁 Context-aware follow-up responses
* ⚡ Real-time chat interface with streaming UX

---

# 🧠 Project Overview

The Titanic Data Chat Agent is a full-stack AI system that combines:

* A **tool-calling LLM agent** (LangChain v1+)
* A **safe Python execution tool** for dataframe analysis
* Automatic **Matplotlib plot capture (base64 rendering)**
* A modern **Streamlit chat UI**
* Production-ready backend deployed via **Render**

Unlike legacy ReAct agents, this project uses the **modern LangChain `create_agent()` API**, ensuring:

* No output parsing errors
* Stable Gemini tool-calling behavior
* Automatic retry on Python execution errors
* Clean architecture separation

---

# 🏗️ Architecture

```
User (Browser)
        ↓
Streamlit Frontend (Chat UI)
        ↓
FastAPI Backend (Render)
        ↓
LangChain Tool-Calling Agent
        ↓
Python Execution Tool (df + matplotlib)
        ↓
Titanic Dataset (pandas DataFrame)
```

---

# ✨ Features

## 🔹 Natural Language Data Analysis

Ask questions like:

* What is the average age of passengers?
* Survival rate by gender
* Average fare by passenger class
* How many passengers embarked from each port?

## 🔹 Automatic Visualizations

* Histograms
* Bar charts
* Distribution plots
* Any matplotlib-generated chart

Charts are automatically:

* Captured off-screen using `matplotlib.use("Agg")`
* Converted to base64
* Rendered in Streamlit

## 🔹 Tool-Calling Agent (Modern LangChain)

* Uses `create_agent()` (LangChain v1+)
* Gemini-native structured tool calling
* No ReAct parsing issues
* Automatic retry on code errors

## 🔹 Safe Python Execution

* Code executed in controlled local environment
* Access limited to:

  * `df` (Titanic DataFrame)
  * `matplotlib.pyplot`
* Errors returned to LLM for correction

## 🔹 Session-Based Memory

* Context-aware follow-up questions
* Maintained at API layer
* Lightweight in-memory session tracking

## 🔹 Polished UX

* Chat-style interface
* "Thinking..." spinner
* Simulated streaming output
* Sidebar with sample questions
* Clear chat button

---

# 📂 Folder Structure

```
Titanic-DataSet-Chat-Agent/
│   .env.example
│   .gitignore
│   README.md
│
├───backend
│   │   requirements.txt
│   │
│   └───app
│       │   agent.py
│       │   config.py
│       │   main.py
│       │   __init__.py
│       │
│       └───data
│               titanic.csv
│
└───frontend
        app.py
        requirements.txt
```

---

# ⚙️ Setup Instructions (Local Development)

---

## 🔹 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Titanic-DataSet-Chat-Agent
```

---

## 🔹 2. Setup Backend

### Create Virtual Environment

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔹 3. Configure Environment Variables

Inside `backend/`, create a `.env` file.

Example:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

You can copy `.env.example` and rename it.

⚠️ Never commit `.env` to GitHub.

---

## 🔹 4. Run Backend

From `backend/` directory:

```bash
uvicorn app.main:app --reload
```

Test:

```
http://127.0.0.1:8000/health
```

---

## 🔹 5. Setup Frontend

Open a new terminal:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser.

---

# 🚀 Deployment Guide

---

## 🌐 Backend → Render

1. Push repository to GitHub
2. Go to [https://render.com](https://render.com)
3. Create New → Web Service
4. Select repository
5. Configure:

* Root Directory: `backend`
* Build Command:

  ```
  pip install -r requirements.txt
  ```
* Start Command:

  ```
  uvicorn app.main:app --host 0.0.0.0 --port 10000
  ```

6. Add Environment Variable:

```
GOOGLE_API_KEY=your_key_here
```

After deployment, you’ll get a URL like:

```
https://your-backend.onrender.com
```

---

## 🌐 Frontend → Streamlit Cloud

1. Update `BACKEND_URL` in `frontend/app.py`
2. Push changes to GitHub
3. Go to [https://share.streamlit.io](https://share.streamlit.io)
4. Deploy using:

   * Main file: `frontend/app.py`
   * Requirements: `frontend/requirements.txt`

---

# 🛠 Technologies Used

* Python 3.10+
* FastAPI
* Uvicorn
* Pandas
* Matplotlib (Agg backend)
* LangChain v1+
* Gemini (Google Generative AI)
* Streamlit
* Requests

---

# 🧩 Key Engineering Decisions

* Used **LangChain v1 tool-calling API** instead of legacy ReAct agents
* Avoided deprecated memory patterns
* Implemented custom safe Python execution tool
* Captured plots using non-GUI backend
* Handled empty tool outputs safely
* Separated frontend and backend for scalable deployment


---

# 🙌 Acknowledgment

Built as part of an AI engineering assignment to demonstrate:

* LLM agent design
* Tool-calling orchestration
* Data reasoning
* Visualization generation
* Production-ready architecture

---

⭐ If you found this useful, feel free to star the repository!
