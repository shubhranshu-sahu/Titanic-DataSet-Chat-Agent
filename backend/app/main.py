from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from typing import Optional

from langchain_core.messages import HumanMessage, AIMessage

from .agent import run_agent

app = FastAPI(title="Titanic Data Chat Agent API")

chat_sessions = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.get("/health")
def health_check():
    return {"status": "Backend running 🚀"}


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        if not request.session_id:
            request.session_id = str(uuid4())

        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []

        history = chat_sessions[request.session_id]

        # Build conversation context
        context_text = ""
        for msg in history:
            context_text += f"User: {msg['user']}\n"
            context_text += f"Assistant: {msg['assistant']}\n"

        full_input = context_text + f"User: {request.message}"

        result = run_agent(full_input)

        history.append({
            "user": request.message,
            "assistant": result["text"]
        })

        return {
            "session_id": request.session_id,
            "response": result["text"],
            "image": result["image"]
        }

    except Exception as e:
        return {"error": str(e)}