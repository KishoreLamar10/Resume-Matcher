import os
from dotenv import load_dotenv
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

def get_api_key():
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
        
    raise ValueError("Missing OPENAI_API_KEY in environment or secrets. Please check your .env file.")

def get_match_score(resume_text: str, job_text: str) -> float:
    api_key = get_api_key()
    embedding_model = OpenAIEmbeddings(openai_api_key=api_key)
    
    resume_vector = embedding_model.embed_query(resume_text)
    job_vector = embedding_model.embed_query(job_text)

    dot_product = sum(r * j for r, j in zip(resume_vector, job_vector))
    resume_norm = sum(r**2 for r in resume_vector) ** 0.5
    job_norm = sum(j**2 for j in job_vector) ** 0.5

    similarity = dot_product / (resume_norm * job_norm + 1e-8)
    return round(similarity * 100, 2)

def get_improvement_suggestions(resume_text: str, job_text: str) -> str:
    api_key = get_api_key()
    llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo", openai_api_key=api_key)
    
    prompt = PromptTemplate(
        input_variables=["resume", "job"],
        template="""
You are a resume optimization assistant. Based on the resume and job description below,
suggest concrete, actionable improvements to align the resume with the job role.
Format the output as a clear bulleted list using markdown.

Resume:
{resume}

Job Description:
{job}

Suggestions:
"""
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": resume_text, "job": job_text})

def get_missing_keywords(resume_text: str, job_text: str) -> str:
    api_key = get_api_key()
    llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo", openai_api_key=api_key)
    
    prompt = PromptTemplate(
        input_variables=["resume", "job"],
        template="""
You are an expert ATS (Applicant Tracking System) parser. Analyze the job description and the resume.
Extract up to 10 critical technical skills, tools, or domain keywords that are present in the job description but are MISSING from the resume.

Return ONLY a comma-separated list of keywords. If nothing is missing, return "None".

Job Description:
{job}

Resume:
{resume}

Missing Keywords:"""
    )
    
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": resume_text, "job": job_text})
