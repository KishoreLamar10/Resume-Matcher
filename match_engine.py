import os
from dotenv import load_dotenv

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in environment. Please check your .env file.")

embedding_model = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = OpenAI(temperature=0.3, openai_api_key=OPENAI_API_KEY)

def get_match_score(resume_text: str, job_text: str) -> float:
    resume_vector = embedding_model.embed_query(resume_text)
    job_vector = embedding_model.embed_query(job_text)

    dot_product = sum(r * j for r, j in zip(resume_vector, job_vector))
    resume_norm = sum(r**2 for r in resume_vector) ** 0.5
    job_norm = sum(j**2 for j in job_vector) ** 0.5

    similarity = dot_product / (resume_norm * job_norm + 1e-8)
    return round(similarity * 100, 2)

def get_improvement_suggestions(resume_text: str, job_text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["resume", "job"],
        template="""
You are a resume optimization assistant. Based on the resume and job description below,
suggest improvements to align the resume with the job role.

Resume:
{resume}

Job Description:
{job}

List your suggestions:
"""
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"resume": resume_text, "job": job_text})
