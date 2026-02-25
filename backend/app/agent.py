import os
import pandas as pd
import io
import base64
import traceback
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent

from .config import GOOGLE_API_KEY

# =============================
# Load Dataset
# =============================
DATA_PATH = Path(__file__).parent / "data" / "titanic.csv"
df = pd.read_csv(DATA_PATH)



# =============================
# Python Execution Tool
# =============================
@tool
def python_executor(code: str):
    """
    Execute Python code to analyze the Titanic dataset.
    A pandas DataFrame named 'df' is available.
    Use matplotlib for plotting if needed.
    """
    global LAST_IMAGE

    try:
        local_env = {"df": df, "plt": plt}

        plt.close("all")
        stdout_buffer = io.StringIO()

        exec(
            f"""
import sys
sys.stdout = stdout_buffer
{code}
""",
            {"stdout_buffer": stdout_buffer},
            local_env
        )

        output_text = stdout_buffer.getvalue()

        LAST_IMAGE = None

        fig = plt.gcf()
        if fig and fig.get_axes():
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            LAST_IMAGE = base64.b64encode(buf.read()).decode("utf-8")
            buf.close()
            plt.close("all")

        return output_text.strip() if output_text else "Execution successful."

    except Exception:
        return f"ERROR:\n{traceback.format_exc()}"

# =============================
# LLM Setup
# =============================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0
)

# =============================
# Create Modern Agent
# =============================
agent = create_agent(
    model=llm,
    tools=[python_executor],
    system_prompt="""
You are a professional data analyst working strictly on the Titanic dataset.

Rules:
- Always use the python_executor tool for calculations.
- Never hallucinate.
- Use matplotlib for plots.
- If code fails, fix it and try again.
- Round numbers to 2 decimal places.
- Keep responses concise and clear.
"""
)


# =============================
# Run Agent Wrapper
# =============================
def run_agent(user_input: str):
    global LAST_IMAGE

    LAST_IMAGE = None  # reset

    result = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
    )

    final_text = ""

    for msg in result["messages"]:
        if msg.type == "ai":
            final_text = msg.content

    return {
        "text": final_text,
        "image": LAST_IMAGE
    }