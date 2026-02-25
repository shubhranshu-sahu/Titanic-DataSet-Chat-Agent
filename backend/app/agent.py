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
from langchain_core.messages import HumanMessage


from .config import GOOGLE_API_KEY

# =============================
# Load Dataset
# =============================
DATA_PATH = Path(__file__).parent / "data" / "titanic.csv"
df = pd.read_csv(DATA_PATH)

LAST_IMAGES = []

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
    global LAST_IMAGES

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


       # Capture all open figures
        figures = [plt.figure(n) for n in plt.get_fignums()]

        for fig in figures:
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            image_base64 = base64.b64encode(buf.read()).decode("utf-8")
            LAST_IMAGES.append(image_base64)
            buf.close()

        plt.close("all")

        figures = plt.get_fignums()

        if not output_text and not figures:
            return "ERROR: No result was printed."
        

        return output_text

    
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

Guidelines:

1. Always use the python_executor tool for any calculations or visualizations.
2. After every tool execution, you MUST generate a clear explanation.
3. When generating visualizations:
   - Explain what is being shown.
   - Highlight key trends or insights.
   - Mention important numerical values.
4. For analytical questions:
   - Provide precise numerical results.
   - Add brief interpretation of what the result means.
5. Never respond with generic phrases like:
   - "Analysis completed."
   - "Execution successful."
6. If a request is ambiguous, ask for clarification.
7. Use structured, readable paragraphs when explanation requires detail.
8. Round numerical results to 2 decimal places.

Be concise when possible, but detailed when explanation is required.
"""
)


# =============================
# Run Agent Wrapper
# =============================
def run_agent(message_history):
    global LAST_IMAGES

    LAST_IMAGES = []
    result = agent.invoke(
        {
        "messages": message_history
    }
    )

    final_text = None
    tool_text = None

    for msg in result["messages"]:

        # AI message
        if msg.type == "ai":
            if isinstance(msg.content, list):
                texts = []
                for block in msg.content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        texts.append(block.get("text", ""))
                combined = "\n".join(texts).strip()
                if combined:
                    final_text = combined
            elif isinstance(msg.content, str) and msg.content.strip():
                final_text = msg.content.strip()

        # Tool message
        if msg.type == "tool":
            if isinstance(msg.content, str) and msg.content.strip():
                tool_text = msg.content.strip()

        #  Enforcement Layer
    if not final_text or len(final_text) < 30:
        # Ask model to summarize tool result properly
        summary_prompt = message_history + [
            HumanMessage(
                content="Provide a clear explanation of the result above. "
                        "Explain what was computed, key insights, and interpret the outcome."
            )
        ]

        summary_result = agent.invoke({"messages": summary_prompt})

        for msg in summary_result["messages"]:
            if msg.type == "ai" and msg.content:
                if isinstance(msg.content, list):
                    texts = [
                        block.get("text", "")
                        for block in msg.content
                        if isinstance(block, dict) and block.get("type") == "text"
                    ]
                    final_text = "\n".join(texts).strip()
                else:
                    final_text = msg.content.strip()

    # Absolute fallback (only if truly broken)
    if not final_text:
        final_text = "I encountered an issue while generating the explanation. Please try rephrasing your question."


    return {
        "text": final_text,
        "images": LAST_IMAGES
    }