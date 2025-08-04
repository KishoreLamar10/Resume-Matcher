import os
from dotenv import load_dotenv
import streamlit as st
from resume_parser import extract_text_from_resume
from job_parser import extract_text_from_job
from match_engine import get_match_score, get_improvement_suggestions

load_dotenv()
st.set_page_config(page_title="Job-Resume Matcher", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f9fafc;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        border-radius: 5px;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Job-Resume Matcher")
st.markdown("Match your resume to any job description and receive personalized AI-powered suggestions.")

# Sidebar for inputs
with st.sidebar:
    st.header("📄 Upload & Paste")
    resume = st.file_uploader("Upload your resume", type=["pdf", "txt"])
    job_desc = st.text_area("Paste the job description here")
    analyze = st.button("🔍 Analyze Match")

# Analysis logic
if analyze:
    if not resume or not job_desc:
        st.warning("Please upload a resume and paste a job description to continue.")
    else:
        resume_text = extract_text_from_resume(resume)
        job_text = extract_text_from_job(job_desc)

        score = get_match_score(resume_text, job_text)
        suggestions = get_improvement_suggestions(resume_text, job_text)

        st.success("Analysis complete!")
        st.markdown(f"### 🔎 Match Score: **{score}%**")

        st.markdown("### 🧠 Suggested Improvements:")
        for line in suggestions.split("\n"):
            if line.strip():
                st.markdown(f"- {line.strip()}")
