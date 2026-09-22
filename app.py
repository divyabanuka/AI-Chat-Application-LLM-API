import streamlit as st
import requests
import time

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Chat Application",
    page_icon="🤖",
    layout="centered"
)

# ---------------- API KEY ----------------

API_KEY = st.secrets["GEMINI_API_KEY"]

# Try reliable models automatically
MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash"
]

# ---------------- UI ----------------

st.title("🤖 AI Chat Application")
st.caption("LLM API powered conversational AI")


# ---------------- GEMINI FUNCTION ----------------

def ask_gemini(question):

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

    last_error = ""

    # Try each model
    for model in MODELS:

        url = (
            "https://generativelanguage.googleapis.com/"
            f"v1beta/models/{model}:generateContent"
        )

        # Retry temporary failures
        for attempt in range(3):

            try:

                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=45
                )

                # Success
                if response.status_code == 200:

                    result = response.json()

                    candidates = result.get("candidates", [])

                    if not candidates:
                        last_error = "No candidates returned."
                        break

                    parts = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [])
                    )

                    if not parts:
                        last_error = "Empty response returned."
                        break

                    answer = parts[0].get("text", "")

                    if answer:
                        return answer

                    last_error = "Empty text returned."
                    break

                # Temporary server error
                if response.status_code in [408, 429, 500, 502, 503, 504]:

                    try:
                        error_data = response.json()
                        last_error = (
                            error_data
                            .get("error", {})
                            .get("message", response.text)
                        )
                    except Exception:
                        last_error = response.text

                    # Wait before retry
                    time.sleep(2 ** attempt)
                    continue

                # Permanent error
                try:
                    error_data = response.json()
                    message = (
                        error_data
                        .get("error", {})
                        .get("message", response.text)
                    )
                except Exception:
                    message = response.text

                return (
                    f"❌ Gemini API Error {response.status_code}: "
                    f"{message}"
                )

            except requests.exceptions.Timeout:

                last_error = "Request timed out."
                time.sleep(2 ** attempt)

            except requests.exceptions.ConnectionError:

                last_error = "Connection error."
                time.sleep(2 ** attempt)

            except Exception as e:

                last_error = str(e)
                break

    return (
        "⚠️ Gemini is temporarily unavailable.\n\n"
        f"Last error: {last_error}\n\n"
        "Please try again in a few minutes."
    )


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