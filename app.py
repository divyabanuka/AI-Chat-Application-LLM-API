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

# ---------------- GEMINI FUNCTION ----------------

def ask_gemini(question):

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{MODEL}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    data = {
        "contents": [
            {
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
            timeout=120
        )

        # ---------------- API ERROR ----------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                error_message = (
                    error_data
                    .get("error", {})
                    .get("message", "Unknown Gemini API error")
                )

            except Exception:
                error_message = response.text

            return f"❌ Gemini API Error {response.status_code}: {error_message}"

        # ---------------- RESPONSE ----------------

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            return "❌ Gemini returned no answer."

        content = candidates[0].get("content", {})

        parts = content.get("parts", [])

        if not parts:
            return "❌ Gemini returned an empty response."

        answer = parts[0].get("text", "")

        if not answer:
            return "❌ No text was returned by Gemini."

        return answer

    # ---------------- ERRORS ----------------

    except requests.exceptions.Timeout:
        return "⏳ Request timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "🌐 Connection error. Check your internet connection."

    except Exception as e:
        return f"❌ Error: {str(e)}"


# ---------------- CHAT INPUT ----------------

question = st.chat_input("Ask me anything...")

if question:

    # User message
    with st.chat_message("user"):
        st.write(question)

    # AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):
            answer = ask_gemini(question)

        st.write(answer)