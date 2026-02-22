import os
from dotenv import load_dotenv
import streamlit as st
from resume_parser import extract_text_from_resume
from job_parser import extract_text_from_job
from match_engine import get_match_score, get_improvement_suggestions, get_missing_keywords

load_dotenv()
st.set_page_config(page_title="Job-Resume Matcher", layout="wide")

st.markdown("""
    <style>
    /* Global Background and Text overridden by config.toml, but we can target specific elements here */
    .stButton>button {
        background-color: #4F46E5;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .block-container {
        padding-top: 3rem;
        max-width: 1000px;
    }
    /* Sleek card look for the tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1F2937;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #374151 !important;
        border-bottom-color: #4F46E5 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
col_hero1, col_hero2 = st.columns([1, 5])
with col_hero1:
    st.image("https://cdn-icons-png.flaticon.com/512/942/942799.png", width=100) # Optional placeholder icon
with col_hero2:
    st.title("AI Resume Matcher 🚀")
    st.markdown("##### *Optimize your resume for the exact job you want.*")
st.markdown("---")

# Input Section: Side-by-side columns
st.markdown("### 1. Provide Your Details")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### 📄 Upload Resume")
    resume = st.file_uploader("Must be a PDF or TXT file", type=["pdf", "txt"], label_visibility="collapsed")

with col2:
    st.markdown("#### 💼 Job Description")
    job_desc = st.text_area("Paste the target job description here...", height=200, label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    analyze = st.button("🔍 Analyze Match", use_container_width=True)

# Analysis logic
if analyze:
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    if not has_api_key:
        try:
            has_api_key = "OPENAI_API_KEY" in st.secrets
        except Exception:
            pass
            
    if not has_api_key:
        st.error("⚠️ **OpenAI API Key is missing!** Please add it to your `.env` file or Streamlit secrets.")
    elif not resume or not job_desc:
        st.warning("Please upload a resume and paste a job description to continue.")
    else:
        with st.spinner("Analyzing Match..."):
            resume_text = extract_text_from_resume(resume)
            job_text = extract_text_from_job(job_desc)

            score = get_match_score(resume_text, job_text)
            missing_keywords = get_missing_keywords(resume_text, job_text)
            suggestions = get_improvement_suggestions(resume_text, job_text)

        st.success("Analysis complete!")
        
        tab1, tab2, tab3 = st.tabs(["🔎 Match Score", "🎯 Missing Keywords", "🧠 Actionable Suggestions"])
        
        with tab1:
            st.metric(label="Compatibility Score", value=f"{score}%")
            st.progress(score / 100.0)
            
        with tab2:
            st.markdown("### Missing Technical Skills / Keywords")
            if missing_keywords.lower().strip() == "none" or not missing_keywords:
                st.success("Great job! Your resume contains all the critical keywords mentioned in the job description.")
            else:
                st.warning("Consider adding these missing keywords to your resume to pass ATS filters:")
                keywords = [kw.strip() for kw in missing_keywords.split(",") if kw.strip()]
                # Display keywords as pills/badges using markdown HTML
                html_keywords = " ".join([f"<span style='background-color: #ffcccc; padding: 5px 10px; border-radius: 15px; margin: 5px; display: inline-block; color: #900;'>{kw}</span>" for kw in keywords])
                st.markdown(html_keywords, unsafe_allow_html=True)
            
        with tab3:
            st.markdown("### Suggested Improvements")
            for line in suggestions.split("\n"):
                if line.strip():
                    if line.strip().startswith("-") or line.strip().startswith("*") or line.strip()[0].isdigit():
                        st.markdown(f"{line.strip()}")
                    else:
                        st.markdown(f"- {line.strip()}")
                        
        st.markdown("---")
        st.header("💾 Export Result")
        report_content = f"""# Job-Resume Matcher Report

## Compatibility Score
{score}%

## Missing Keywords (ATS Gap Analysis)
{missing_keywords}

## Actionable Suggestions
{suggestions}
"""
        st.download_button(
            label="📄 Download Analysis (.txt)",
            data=report_content,
            file_name="resume_analysis_report.txt",
            mime="text/plain"
        )
