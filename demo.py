import os
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# Sidebar / Header
# --------------------------------------------------
logo = Image.open("logo.png")
st.sidebar.image(logo, width=60)
st.sidebar.markdown("Resume Genie")

st.title("Hey Folk's")
st.title("Welcome to the Resume Genie")

# --------------------------------------------------
# LLM Setup
# --------------------------------------------------
XAI_API_KEY = os.environ.get("XAI_API_KEY")

from langchain_xai import ChatXAI

chat = ChatXAI(
    model="grok-4",
    api_key=XAI_API_KEY,
)

# --------------------------------------------------
# PDF-Based Resume Loading
# --------------------------------------------------
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("path/to/your/resume.pdf")   # replace with actual path
documents = loader.load()

# Keep this as the single source of truth for the resume text —
# do NOT reassign this variable later with a placeholder.
resume_text = "\n\n".join(doc.page_content for doc in documents)

# --------------------------------------------------
# Resume Evaluation Prompt
# --------------------------------------------------
from langchain_core.prompts import PromptTemplate

resume_eval_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an intelligent assistant that understands resume documents.
Given the resume content below, provide:
1. A score out of 100 based on overall quality.
2. Strengths found in the resume.
3. Weaknesses found in the resume.
4. Skills currently mentioned in the resume.
5. Additional skills that could be added to strengthen it.

Resume content:
{context}

Question: {question}
"""
)

formatted_eval_prompt = resume_eval_prompt.format(
    context=resume_text,
    question="Please evaluate this resume."
)

st.subheader("📊 Resume Evaluation")
eval_output = st.empty()
full_eval_response = ""
for chunk in chat.stream(formatted_eval_prompt):
    full_eval_response += chunk.content
    eval_output.markdown(full_eval_response)

# --------------------------------------------------
# Cover Letter Generation
# --------------------------------------------------
job_description = st.text_area("Paste the job description here:")

if st.button("Generate Cover Letter") and job_description:
    cover_letter_prompt = f"""
Based on the resume of the candidate, write a tailored cover letter.

Job Description:
{job_description}

Candidate's Resume:
{resume_text}
"""

    st.subheader("✉️ Generated Cover Letter")
    cover_letter_output = st.empty()
    full_cover_letter = ""
    for chunk in chat.stream(cover_letter_prompt):
        full_cover_letter += chunk.content
        cover_letter_output.markdown(full_cover_letter)
        
        



# --------------------------------------------------
# Resume Scorer
# --------------------------------------------------
job_description = st.text_area("Paste the job description here:")

if st.button("Generate Cover Letter") and job_description:
    """You are an expert resume scorer. Analyze match to JD. EXACT structure:
**Score**: X/100
**Overall Match**: X%
Keywords matched: • ...
Missing keywords: • ...
Readability Score: X/100
ATS Compatibility Score: X/100
2-liner summary: ...
Skill gap analysis: • ...
Overall improvement suggestions: • ...
Industry specific feedback: • ...
Job: {job_description}
Resume: {context}
Be honest, use rubrics.

Job Description:
{job_description}

Candidate's Resume:
{resume_text}
"""

    st.subheader("✉️ Generated Cover Letter")
    cover_letter_output = st.empty()
    full_cover_letter = ""
    for chunk in chat.stream(cover_letter_prompt):
        full_cover_letter += chunk.content
        cover_letter_output.markdown(full_cover_letter)
        
        
        
        
        
# AI Career Coach
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
chat_history = []
system_message = SystemMessage(
    content=f"""
    you are a professional career coach and resume mentor.
    you help with:
    carrer guidance
    resume improvements
    interview preparation
    job search strategy
    skill gap analysus
    
    
    candidate resume:
    {context}
    """
)


while True:
    user_input = input("You: ")
    
    if user_input.lower() in ['exit', 'quit']:
        print("\n Goodbye!!")
        
        
        chat_history.append(HumanMessage(context=user_input))
        message = [system_message] + chat_history
        print("\nCoach: ", end="", flush=True)
        
        
        response_text = ""
        for chunk in chat.stream(message):
            print(chunk.content, end="", flush=True)
            response_text = response_text + chunk.content
            print("\n")
            