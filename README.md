# 📄 Resume Genie — AI-Powered Resume Toolkit

An all-in-one AI toolkit that helps job seekers optimize their resumes, match them against job descriptions, generate tailored cover letters, and get personalized career coaching — all powered by an LLM through a live-discovering, resilient API integration.

---

## 🎯 Overview

Resume Genie bundles four AI-powered tools into a single Streamlit application:

| Tool | What it does |
|---|---|
| ✉️ **Cover Letter Generator** | Generates a tailored, professional cover letter from a resume + job description |
| 📊 **Resume-JD Matcher** | Scores how well a resume matches a specific job description, with keyword and ATS analysis |
| 🔍 **Resume Checker** | Standalone resume evaluation — strengths, weaknesses, ATS compatibility, and skill recommendations |
| 💬 **Career Coach Chat** | An interactive chatbot that answers career, resume, and interview-prep questions using the uploaded resume as context |

---

## 🧠 Key Highlights

- **Resilient LLM integration** — dynamically queries OpenRouter's live model catalog to select a currently-available free model, rather than relying on a hardcoded model name that can break when free-tier availability rotates.
- **Structured prompt engineering** — each tool uses a purpose-built `PromptTemplate` enforcing a strict output structure (score, keyword analysis, ATS compatibility, etc.), rather than open-ended prompting.
- **Streaming responses** — all tools stream model output token-by-token for a responsive user experience.
- **Session-persisted chat** — the Career Coach uses Streamlit's session state to maintain conversation history and injected resume context across multiple turns.
- **Real-world validation testing** — tested with mismatched job descriptions to confirm the matcher performs genuine semantic scoring rather than superficial keyword stuffing (a fully unrelated JD correctly scored 12/100 vs. 92/100 for a well-matched one), and tested the chatbot's resistance to hallucination by asking it to modify a skill that didn't exist in the resume.

---

## ⚙️ Tech Stack

**Language:** Python
**LLM Orchestration:** LangChain (`langchain-openai`, `langchain-community`)
**LLM Provider:** OpenRouter (free-tier models, dynamically discovered)
**PDF Parsing:** PyPDFLoader (pypdf)
**Frontend:** Streamlit
**Environment Management:** python-dotenv, uv

---

## 🗂️ Project Structure

```
resume-genie/
├── main.py              # Full Streamlit application (all 4 tools)
├── requirements.txt
├── .env                 # API key (not committed)
├── .gitignore
└── README.md
```

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/resume-genie.git
   cd resume-genie
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```
   or with pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**

   Create a `.env` file in the project root:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```
   Get a free key at [openrouter.ai](https://openrouter.ai).

4. **Run the app**
   ```bash
   streamlit run main.py
   ```

---

## 🔍 A Real Bug Caught by the Tool Itself

While testing, the Resume Checker flagged missing hyperlinks in the resume's contact section — even though the resume visually showed "LinkedIn | GitHub | Portfolio" as clickable links. Investigating this revealed that `PyPDFLoader` extracts only the visible text layer of a PDF, not the underlying hyperlink annotations — meaning any ATS or LLM-based tool relying on plain-text extraction would see the same gap. This mirrors how many real-world ATS systems parse resumes, making the finding directly actionable: contact links should include the visible URL text, not just a clickable label.

---

## 📌 Future Improvements

- Add support for `.docx` resumes in addition to PDF
- Persist chat history across sessions (currently resets on app restart)
- Add a "compare against multiple JDs" batch mode for the matcher
- Swap in a paid/dedicated model (e.g., Grok-4) once available, replacing the free-tier fallback

---

## 👤 Author

**Muhammad Hassan**
[LinkedIn](https://www.linkedin.com/in/muhammad-hassanofficial) · [GitHub](https://github.com/MHassanEjaz) · [Portfolio](https://hassan-portfolio-rtse.vercel.app/)