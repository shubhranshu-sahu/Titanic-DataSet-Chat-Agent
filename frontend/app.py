import streamlit as st
import requests
import base64
import time

# Config
BACKEND_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Titanic Data Chat Agent", layout="centered")

st.title("🚢 Titanic Data Chat Agent")
st.markdown("Ask questions about the Titanic dataset and get insights + visualizations.")

# Session State
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar 
with st.sidebar:
    st.header("Sample Questions")
    st.markdown("""
    - What is the average age of passengers?
    - Show histogram of Age
    - Survival rate by gender
    - Average fare by passenger class
    - Bar chart of Embarked distribution
    """)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()

# 
# Display Chat History

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image"):
            image_bytes = base64.b64decode(msg["image"])
            st.image(image_bytes, use_container_width=True)

# User Input
user_input = st.chat_input("Ask about Titanic dataset...")

if user_input:
    # Store user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    payload = {
        "message": user_input,
        "session_id": st.session_state.session_id
    }

    try:
        with st.spinner("Thinking... 🤔"):
            response = requests.post(BACKEND_URL, json=payload)
            data = response.json()

        # Save session ID
        if not st.session_state.session_id:
            st.session_state.session_id = data.get("session_id")

        bot_text = data.get("response", "")
        bot_image = data.get("image")

        # Show assistant message with streaming effect
        with st.chat_message("assistant"):
            placeholder = st.empty()
            streamed_text = ""

            for char in bot_text:
                streamed_text += char
                placeholder.markdown(streamed_text)
                time.sleep(0.01)

            if bot_image:
                image_bytes = base64.b64decode(bot_image)
                st.image(image_bytes, use_container_width=True)

        # Store assistant message
        st.session_state.messages.append({
            "role": "assistant",
            "content": bot_text,
            "image": bot_image
        })

    except Exception as e:
        st.error(f"Error connecting to backend: {e}") 