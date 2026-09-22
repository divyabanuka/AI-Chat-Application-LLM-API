
import streamlit as st
import requests

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖",
    layout="centered"
)

# ---------------- TITLE ----------------

st.title("🤖 AI Chat Application")
st.caption("LLM API powered conversational AI")

# ---------------- API CONFIG ----------------

API_KEY = st.secrets["GEMINI_API_KEY"]

MODEL = "gemini-3.5-flash"

API_URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)

SYSTEM_INSTRUCTION = """
You are a helpful AI assistant.

Give clear, simple, and accurate answers.

For technical questions, explain step by step.

Keep responses concise and easy to understand.
"""

# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- DISPLAY HISTORY ----------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- USER INPUT ----------------

user_input = st.chat_input("Ask me anything...")

if user_input:

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # ---------------- BUILD CONVERSATION ----------------

    contents = []

    for message in st.session_state.messages:

        role = (
            "user"
            if message["role"] == "user"
            else "model"
        )

        contents.append({
            "role": role,
            "parts": [
                {
                    "text": message["content"]
                }
            ]
        })

    # ---------------- API REQUEST ----------------

    data = {
        "system_instruction": {
            "parts": [
                {
                    "text": SYSTEM_INSTRUCTION
                }
            ]
        },
        "contents": contents
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    try:

        response = requests.post(
            API_URL,
            headers=headers,
            json=data,
            timeout=60
        )

        # ---------------- SUCCESS ----------------

        if response.ok:

            result = response.json()

            ai_reply = (
                result["candidates"][0]
                ["content"]["parts"][0]["text"]
            )

            # Save AI response
            st.session_state.messages.append({
                "role": "assistant",
                "content": ai_reply
            })

            # Display AI response
            with st.chat_message("assistant"):
                st.markdown(ai_reply)

        # ---------------- QUOTA ERROR ----------------

        elif response.status_code == 429:

            st.warning(
                "⚠️ Gemini API quota is temporarily exhausted."
            )

            st.info(
                "Please try again later when the API quota resets."
            )

        # ---------------- AUTHENTICATION ERROR ----------------

        elif response.status_code == 401 or response.status_code == 403:

            st.error(
                "🔑 Gemini API key error. "
                "Please check your API key in Streamlit Secrets."
            )

        # ---------------- OTHER API ERRORS ----------------

        else:

            st.error(
                f"Gemini API temporarily unavailable "
                f"(Error {response.status_code})."
            )

    # ---------------- TIMEOUT ----------------

    except requests.exceptions.Timeout:

        st.warning(
            "⏳ The request took too long. Please try again."
        )

    # ---------------- CONNECTION ERROR ----------------

    except requests.exceptions.RequestException:

        st.error(
            "🌐 Could not connect to the Gemini API. "
            "Please check your internet connection and try again."
        )

    # ---------------- OTHER ERROR ----------------

    except Exception:

        st.error(
            "❌ Something went wrong. Please try again later."
        )