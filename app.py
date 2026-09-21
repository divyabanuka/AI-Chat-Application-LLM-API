
import streamlit as st
import requests

st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 AI Chat Application")
st.caption("LLM API powered conversational AI")

# API key from Streamlit Secrets
API_KEY = st.secrets["GEMINI_API_KEY"]

MODEL = "gemini-3.5-flash"

SYSTEM_INSTRUCTION = """
You are a helpful AI assistant.
Give clear, simple, and accurate answers.
For technical questions, explain step by step.
Keep responses concise and easy to understand.
"""

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask me anything...")

if user_input:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare conversation
    contents = []

    for message in st.session_state.messages:
        contents.append({
            "role": "user" if message["role"] == "user" else "model",
            "parts": [
                {"text": message["content"]}
            ]
        })

    data = {
        "system_instruction": {
            "parts": [
                {"text": SYSTEM_INSTRUCTION}
            ]
        },
        "contents": contents
    }

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    try:
        response = requests.post(
            url,
            params={"key": API_KEY},
            json=data,
            timeout=60
        )

        if response.ok:
            result = response.json()

            ai_reply = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_reply
            })

            with st.chat_message("assistant"):
                st.markdown(ai_reply)

        else:
            st.error("API Error. Please try again.")

    except requests.exceptions.Timeout:
        st.error("Request timed out. Please try again.")

    except Exception as e:
        st.error(f"Error: {e}")
