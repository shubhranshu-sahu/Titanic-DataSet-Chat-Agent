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
    return {"status": "Backend running - GET request"}

@app.head("/health")
def health_check_head():
    return {"status": "Backend running - HEAD request"}



@app.post("/chat")
def chat(request: ChatRequest):
    try:
        # Create session if needed
        if not request.session_id:
            request.session_id = str(uuid4())

        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []

        history = chat_sessions[request.session_id]

        # Append new user message
        history.append(HumanMessage(content=request.message))

        # Run agent with full structured history
        result = run_agent(history)

        # Append assistant response to history
        history.append(AIMessage(content=result["text"]))

        return {
            "session_id": request.session_id,
            "response": result["text"],
            "images": result["images"]
        }

    except Exception as e:
        return {"error": str(e)}