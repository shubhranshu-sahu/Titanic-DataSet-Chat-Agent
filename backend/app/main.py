from fastapi import FastAPI
import pandas as pd
from pathlib import Path

from pydantic import BaseModel
from uuid import uuid4
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


from .agent import run_agent

app = FastAPI(title="Titanic Data Chat Agent API")

# Loading dataset 
DATA_PATH = Path(__file__).parent / "data" / "titanic.csv"

try:
    df = pd.read_csv(DATA_PATH)
    print("Titanic dataset loaded successfully")
    print(f"Dataset shape: {df.shape}")
except Exception as e:
    print("Failed to load dataset:", e)
    df = None


@app.get("/health")
def health_check():
    return {"status": "Backend is running "}


@app.get("/dataset-info")
def dataset_info():
    if df is None:
        return {"error": "Dataset not loaded"}
    
    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": list(df.columns)
    }




##--------------------------------------------

chat_sessions = {}


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None





@app.post("/chat")
def chat(request: ChatRequest):
    try:
        if not request.session_id:
            request.session_id = str(uuid4())

        # Initialize history if not exists
        if request.session_id not in chat_sessions:
            chat_sessions[request.session_id] = []

        history = chat_sessions[request.session_id]

        # Define system behavior
        system_message = SystemMessage(
            content="""
        You are a professional data analyst working strictly on the Titanic dataset.

        Guidelines:
        - Only answer using dataset information.
        - Do not hallucinate.
        - If unsure, say the dataset does not contain that information.
        - Format answers clearly.
        - Round numbers to 2 decimal places.
        - Keep explanations concise (max 4 lines).
        """
        )

        # Build full conversation list
        messages = [system_message] + history + [
            HumanMessage(content=request.message)
        ]

        # Convert structured messages into formatted text as expected by the agent
        formatted_prompt = ""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted_prompt += f"System: {msg.content}\n\n"
            elif isinstance(msg, HumanMessage):
                formatted_prompt += f"User: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                formatted_prompt += f"Assistant: {msg.content}\n"

        formatted_prompt += "Assistant:"

        # Run agent
        answer = run_agent(formatted_prompt)

        # Store conversation properly
        history.append(HumanMessage(content=request.message))
        history.append(AIMessage(content=answer))

        return {
            "session_id": request.session_id,
            "response": answer
        }

    except Exception as e:
        return {"error": str(e)}
    
    