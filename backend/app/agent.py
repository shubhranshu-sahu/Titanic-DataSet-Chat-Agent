import pandas as pd
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import os

from .config import GOOGLE_API_KEY

# Load dataset once
DATA_PATH = Path(__file__).parent / "data" / "titanic.csv"
df = pd.read_csv(DATA_PATH)


# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0,
)

# Create Pandas Agent
agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=True,
    allow_dangerous_code=True,
    handle_parsing_errors=True
)

def run_agent(prompt: str):
    """
    Wrapper function to run the agent.
    """
    response = agent.invoke(prompt)
    print(response)
    

    if isinstance(response, dict) and "output" in response:
        return response["output"]
    
    return str(response)