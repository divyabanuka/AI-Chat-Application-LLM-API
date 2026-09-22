import streamlit as st
import requests

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖",
    layout="centered"
)

# ---------------- API KEY ----------------

API_KEY = st.secrets["GEMINI_API_KEY"]

MODEL = "gemini-3.8-flash"

# ---------------- UI ----------------

st.title("🤖 AI Chat Application")
st.caption("LLM API powered conversational AI")

# ---------------- CHAT FUNCTION ----------------

def ask_gemini(question):

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    data = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": question
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        # API error
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get(
                    "message",
                    response.text
                )
            except Exception:
                error_message = response.text

            return f"API Error ({response.status_code}): {error_message}"

        result = response.json()

        # Check response
        candidates = result.get("candidates", [])

        if not candidates:
            return "No response was returned by Gemini."

        parts = candidates[0].get("content", {}).get("parts", [])

        if not parts:
            return "Gemini returned an empty response."

        answer = parts[0].get("text", "")

        if not answer:
            return "Gemini returned no text."

        return answer

    except requests.exceptions.Timeout:
        return "⏳ Gemini took too long to respond. Please try again."

    except requests.exceptions.ConnectionError:
        return "🌐 Connection error. Please check your internet connection."

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- CHAT INPUT ----------------

question = st.chat_input("Ask me anything...")

if question:

    # Show user question
    with st.chat_message("user"):
        st.write(question)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = ask_gemini(question)

        st.write(answer)