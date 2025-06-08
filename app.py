import os
import requests
import streamlit as st
from dotenv import load_dotenv
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "mistralai/mistral-7b-instruct"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://yourdomain.com",
    "X-Title": "AI Interview Prep"
}

st.set_page_config(page_title="AI Interview Assistant", page_icon="💬", layout="centered")

# ---------- LLM Functions ---------- #
def ask_openrouter(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"❌ Error: {response.status_code}\n{response.text}"

def generate_questions_by_round(job_desc, round_type):
    prompt = f"""
You are a senior interviewer. Based on this job description, generate 4 {round_type} interview questions.

Job Description:
{job_desc}

Format:
- Q1
- Q2
- Q3
- Q4
"""
    return ask_openrouter(prompt)

def generate_all_questions(job_desc):
    prompt = f"""
You are a senior interviewer. Based on the job description, generate interview questions in three sections:

1. Behavioral Questions (4)
2. Technical Questions (4)
3. HR Round Questions (4)

Job Description:
{job_desc}

Format:
### Behavioral
- Q1
- Q2
- Q3
- Q4

### Technical
- Q1
- Q2
- Q3
- Q4

### HR Round
- Q1
- Q2
- Q3
- Q4
"""
    return ask_openrouter(prompt)

def generate_question_by_round(round_name):
    prompt = f"Generate 1 random {round_name} interview question only. No explanation, just the question."
    return ask_openrouter(prompt).strip()

def give_detailed_feedback(question, answer):
    prompt = f"""
You are an interview coach. Give concise feedback (max 4 lines) and a suggested improved answer.

Question: {question}
Candidate's Answer: {answer}

Format:
- Good Points
- Areas to Improve
- Suggested Improved Answer
"""
    return ask_openrouter(prompt)

# ---------- Streamlit Tabs ---------- #
tab1, tab2 = st.tabs(["📄 Generate Questions", "🧠 Practice & Feedback"])

# --- Tab 1: Question Generator --- #
with tab1:
    st.title("📄 Interview Question Generator")
    job_desc = st.text_area("Paste Job Description:", height=250)

    col1, col2 = st.columns(2)
    with col1:
        round_selection = st.selectbox("Select Round to Generate:", ["Behavioral", "Technical", "HR Round"])
        if st.button("🎯 Generate Selected Round Questions"):
            if not job_desc.strip():
                st.warning("Please enter a job description.")
            else:
                with st.spinner(f"Generating {round_selection} questions..."):
                    result = generate_questions_by_round(job_desc, round_selection)
                    st.markdown(f"### {round_selection} Questions")
                    st.markdown(result)

    with col2:
        if st.button("📋 Generate All Rounds"):
            if not job_desc.strip():
                st.warning("Please enter a job description.")
            else:
                with st.spinner("Generating all types of questions..."):
                    result = generate_all_questions(job_desc)
                    st.markdown("### All Interview Rounds")
                    st.markdown(result)

# --- Tab 2: Answer Feedback --- #
with tab2:
    st.title("🧠 Practice by Round & Get Feedback")
    feedback_round = st.selectbox("Choose Interview Round:", ["Behavioral", "Technical", "HR Round"], key="feedback_round")

    if st.button("🎲 Get a Random Question"):
        st.session_state.question = generate_question_by_round(feedback_round)

    question = st.session_state.get("question", "")
    if question:
        st.markdown(f"**🎯 {feedback_round} Question:** {question}")
    else:
        st.info("Click above to get a question.")

    answer_method = st.radio("Answer using:", ["Text", "Voice"])

    if answer_method == "Text":
        answer = st.text_area("Write your answer here:")
    else:
        st.warning("🎙️ Voice input enabled (for local use only)")
        st.markdown("Due to Streamlit limitations, please **write what you said** below after recording.")

        # Streamlit WebRTC component (non-functional for actual speech recognition)
        webrtc_streamer(key="audio", mode=WebRtcMode.SENDONLY)

        answer = st.text_area("Write what you spoke (for feedback):")

    if st.button("✅ Get Feedback"):
        if not question or not answer:
            st.warning("Provide both question and answer.")
        else:
            with st.spinner("Generating feedback..."):
                feedback = give_detailed_feedback(question, answer)
                st.markdown("### ✍️ Feedback & Suggested Answer")
                st.success(feedback)














