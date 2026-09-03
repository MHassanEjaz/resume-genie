import streamlit as st
import os
import tempfile
import requests
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

st.set_page_config(
    page_title="Resume Genie",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

from PIL import Image

logo = Image.open("logo.png")
st.sidebar.image(logo, width=80)

st.sidebar.markdown("**Resume Genie**")

# API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_API_KEY:
    st.error("❌ **OPENROUTER_API_KEY missing**. Add it to your `.env` file or `.streamlit/secrets.toml`.")
    st.stop()


def get_live_free_model() -> str:
    """
    Query OpenRouter's live model catalog and return the ID of a currently
    free model. Free-tier models rotate frequently, so we check live rather
    than hardcoding a model name.
    """
    resp = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])

    free_models = []
    for m in data:
        pricing = m.get("pricing", {})
        try:
            prompt_price = float(pricing.get("prompt", "1"))
            completion_price = float(pricing.get("completion", "1"))
        except (TypeError, ValueError):
            continue
        if prompt_price == 0 and completion_price == 0:
            free_models.append(m["id"])

    if not free_models:
        raise RuntimeError("No free models currently available on OpenRouter.")

    return free_models[0]


@st.cache_resource(show_spinner="🔄 Initializing model...")
def get_llm():
    model_id = get_live_free_model()
    return ChatOpenAI(
        model=model_id,
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
        max_tokens=4000,
    )


llm = get_llm()

# PDF Loader
def extract_resume_text(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    try:
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        text = "\n\n".join(doc.page_content for doc in docs)
        return text
    finally:
        os.unlink(tmp_path)

# Prompts
COVER_LETTER_PROMPT = PromptTemplate.from_template("""
Write a professional cover letter (300-450 words) for this job. Match resume to JD exactly. Standard format.
Job Description: {job_description}
Resume: {resume_text}
Do not invent facts.
""")

RESUME_SCORER_PROMPT = PromptTemplate.from_template("""You are an expert resume scorer. Analyze match to JD. EXACT structure:
**Score**: X/100
**Overall Match**: X%
Keywords matched: bullet points
Missing keywords: bullet points
Readability Score: X/100
ATS Compatibility Score: X/100
2-liner summary: ...
Skill gap analysis: bullet points
Overall improvement suggestions: bullet points
Industry specific feedback: bullet points
Be honest, use rubrics.

Job: {job_description}
Resume: {context}
""")

RESUME_CHECKER_PROMPT = PromptTemplate.from_template("""
Score resume standalone (clarity, format, ATS, skills): EXACT structure:
1. **Score**: X/100
2. **Strengths**: bullet points
3. **Weaknesses**: bullet points
4. **Skills Mentioned**: bullet points
5. **Recommended Skills**: bullet points
6. **Next Career Steps**: bullet points
Resume: {context}
""")

# Main Ui
st.title("🚀 Resume Genie")
st.markdown("""
**Powered by OpenRouter (free tier)** • Your all-in-one solution for job applications
**AI Tools** to craft winning resumes, cover letters & career strategies 💼✨
""")

# left side
st.sidebar.title("🛠️ Select Tool")
tool = st.sidebar.radio("Choose a service:", [
    "✉️ Cover Letter Generator",
    "📊 Resume-JD Matcher",
    "🔍 Resume Checker",
    "💬 Career Coach Chat"
], index=0, horizontal=False, key="tool_selector")

job_desc = ""
if tool in ["✉️ Cover Letter Generator", "📊 Resume-JD Matcher"]:
    st.sidebar.subheader("📤 Inputs")
    job_desc = st.sidebar.text_area("Job Description", height=200, key="jd_shared")

#4: Cover Letter
if tool == "✉️ Cover Letter Generator":
    st.header("✉️ AI Cover Letter Generator")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Job Description")
        job_description = st.text_area("Paste JD", value=job_desc or "", height=350, key="jd_cl")

    with col2:
        st.subheader("📄 Your Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="cl_resume")
        if uploaded_file:
            if st.button("🔥 Generate Cover Letter", type="primary"):
                with st.spinner("Extracting → Generating..."):
                    resume_text = extract_resume_text(uploaded_file)
                    chain = COVER_LETTER_PROMPT | llm
                    full_response = ""
                    resp_container = st.empty()
                    for chunk in chain.stream({"job_description": job_description, "resume_text": resume_text}):
                        content = chunk.content if hasattr(chunk, "content") else str(chunk)
                        full_response += content
                        resp_container.markdown(full_response + "▌")
                    resp_container.markdown(full_response)
                    st.download_button("💾 Download .md", full_response, "cover_letter.md")

#4: Resume Scorer/Matcher
elif tool == "📊 Resume-JD Matcher":
    st.header("📊 Resume vs Job Description Matcher")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Job Description")
        job_description = st.text_area("Paste full JD", value=job_desc or "", height=350, key="jd_scorer")

    with col2:
        st.subheader("📄 Resume")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf", key="scorer_resume")
        if uploaded_file:
            st.success("✅ Resume loaded")
            if st.button("📈 Score Match", type="primary"):
                with st.spinner("Analyzing match... (30-60s)"):
                    context = extract_resume_text(uploaded_file)
                    chain = RESUME_SCORER_PROMPT | llm
                    response = chain.invoke({"job_description": job_description, "context": context})
                    st.markdown("### 📊 **Analysis Result**")
                    st.markdown(response.content)

#3: Resume Checker
elif tool == "🔍 Resume Checker":
    st.header("🔍 Standalone Resume Evaluator")
    uploaded_file = st.file_uploader("Upload resume PDF", type="pdf", key="checker_resume")

    if uploaded_file and st.button("Evaluate Resume", type="primary"):
        with st.spinner("Evaluating..."):
            context = extract_resume_text(uploaded_file)
            chain = RESUME_CHECKER_PROMPT | llm
            response = chain.invoke({"context": context})
            st.markdown("### 📋 **Detailed Evaluation**")
            st.markdown(response.content)

#4: Career Coach Chat
elif tool == "💬 Career Coach Chat":
    st.header("💬 Career Coach Chatbot")

    if "resume_context" not in st.session_state:
        st.session_state.resume_context = None
        st.session_state.chat_history = []

    uploaded_file = st.file_uploader("Upload resume first", type="pdf", key="chat_resume")
    if uploaded_file and st.session_state.resume_context is None:
        context = extract_resume_text(uploaded_file)
        st.session_state.resume_context = context
        st.rerun()

    if not st.session_state.resume_context:
        st.warning("👆 Upload your resume to start chatting!")
        st.stop()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("📄 Your Resume")
        with st.expander("View full text", expanded=True):
            st.text_area("", st.session_state.resume_context, height=500, disabled=True)

    with right_col:
        st.subheader("🤖 Career Coach")
        system_msg = SystemMessage(content=f"""You are a career coach. Use this resume: {st.session_state.resume_context}""")

        for msg in st.session_state.chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            with st.chat_message(role):
                st.markdown(msg.content)

        if prompt := st.chat_input("Ask about career, resume, interviews..."):
            st.session_state.chat_history.append(HumanMessage(content=prompt))
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                messages = [system_msg] + st.session_state.chat_history
                resp_container = st.empty()
                full_resp = ""
                for chunk in llm.stream(messages):
                    full_resp += chunk.content
                    resp_container.markdown(full_resp + "▌")
                resp_container.markdown(full_resp)
            st.session_state.chat_history.append(AIMessage(content=full_resp))

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("✅ **Ready**: All 4 tools live")
with col2:
    st.caption("🔑 **API**: OpenRouter (free tier)")
with col3:
    st.caption("📅 **Built**: Jan 2026 • Muhammad Hassan")

st.sidebar.markdown("---")
st.sidebar.caption("**Pro Tips**: Use sidebar to switch tools instantly ⚡")