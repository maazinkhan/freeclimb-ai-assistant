import streamlit as st
import requests
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="FreeClimb AI Assistant",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

with st.sidebar:
    theme = st.radio(
        "Theme",
        options=["dark", "light"],
        format_func=lambda t: "☾" if t == "dark" else "☀︎",
        horizontal=True,
        key="theme",
        label_visibility="collapsed",
        help="Dark / light mode",
    )

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;500;600&display=swap');

html, body, [class*="css"] {
  font-family: "Source Sans 3", system-ui, sans-serif;
}

.stApp {
  background:
    radial-gradient(900px 480px at 12% -15%, #1a3a4a 0%, transparent 55%),
    linear-gradient(165deg, #121a20 0%, #1a262e 45%, #152028 100%);
  color: #e8eef2;
}

h1, .brand-title {
  font-family: "Fraunces", Georgia, serif !important;
  letter-spacing: -0.02em;
}

.brand-block { margin: 0.25rem 0 1.25rem 0; }

.brand-title {
  font-size: 2.35rem;
  font-weight: 700;
  color: #e8eef2;
  margin: 0 0 0.35rem 0;
  line-height: 1.15;
}

.brand-sub {
  font-size: 1.05rem;
  color: #a8bbc6;
  margin: 0;
  max-width: 36rem;
  line-height: 1.45;
}

.coverage-card {
  background: #24343e;
  border: 1px solid #3a5160;
  border-radius: 12px;
  padding: 1rem 1.15rem 1.1rem;
  margin: 0.75rem 0 1.25rem 0;
}

.coverage-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #8aa3b0;
  margin: 0 0 0.55rem 0;
}

.coverage-body {
  color: #d0dde5;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 0.85rem 0;
}

.topic-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem 1rem;
  margin: 0 0 0.9rem 0;
  font-size: 0.9rem;
  color: #c5d4dc;
}

.topic-grid span::before {
  content: "·";
  color: #5eb3c9;
  font-weight: 700;
  margin-right: 0.4rem;
}

.doc-links { font-size: 0.92rem; line-height: 1.7; color: #a8bbc6; }

.doc-links a {
  color: #7ecee6 !important;
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid rgba(126, 206, 230, 0.4);
}

.doc-links a:hover { border-bottom-color: #7ecee6; }

section[data-testid="stSidebar"] {
  background: #0c161c;
}

section[data-testid="stSidebar"] * { color: #e8eef2 !important; }
section[data-testid="stSidebar"] a { color: #7ecee6 !important; }

/* Main text / inputs on dark */
.stApp p, .stApp label, .stApp span, .stMarkdown, .stCaption {
  color: #d0dde5;
}

div[data-baseweb="input"] input,
div[data-baseweb="textarea"] textarea {
  background-color: #1c2a33 !important;
  color: #e8eef2 !important;
}

hr { border-color: #3a5160 !important; }
</style>
"""

LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Source+Sans+3:wght@400;500;600&display=swap');

html, body, [class*="css"] {
  font-family: "Source Sans 3", system-ui, sans-serif;
}

.stApp {
  background:
    radial-gradient(1000px 520px at 10% -10%, #c5d9e4 0%, transparent 50%),
    linear-gradient(180deg, #e6eef2 0%, #dce6ec 100%);
  color: #1a2c36;
}

h1, .brand-title {
  font-family: "Fraunces", Georgia, serif !important;
  letter-spacing: -0.02em;
}

.brand-block { margin: 0.25rem 0 1.25rem 0; }

.brand-title {
  font-size: 2.35rem;
  font-weight: 700;
  color: #0f2a3a;
  margin: 0 0 0.35rem 0;
  line-height: 1.15;
}

.brand-sub {
  font-size: 1.05rem;
  color: #3d5563;
  margin: 0;
  max-width: 36rem;
  line-height: 1.45;
}

.coverage-card {
  background: #f7fafb;
  border: 1px solid #b8c9d4;
  border-radius: 12px;
  padding: 1rem 1.15rem 1.1rem;
  margin: 0.75rem 0 1.25rem 0;
}

.coverage-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #5a7a8a;
  margin: 0 0 0.55rem 0;
}

.coverage-body {
  color: #243944;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 0.85rem 0;
}

.topic-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem 1rem;
  margin: 0 0 0.9rem 0;
  font-size: 0.9rem;
  color: #2c4552;
}

.topic-grid span::before {
  content: "·";
  color: #1a6b8a;
  font-weight: 700;
  margin-right: 0.4rem;
}

.doc-links { font-size: 0.92rem; line-height: 1.7; }

.doc-links a {
  color: #0b5f7a !important;
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px solid rgba(11, 95, 122, 0.35);
}

.doc-links a:hover { border-bottom-color: #0b5f7a; }

section[data-testid="stSidebar"] {
  background: #0f2a3a;
}

section[data-testid="stSidebar"] * { color: #e8eef2 !important; }
section[data-testid="stSidebar"] a { color: #7ecee6 !important; }
</style>
"""

st.markdown(DARK_CSS if theme == "dark" else LIGHT_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### About")
    st.markdown(
        "Answers come from the FreeClimb **API Reference** "
        "(accounts, numbers, SMS, voice, PerCL, webhooks, and more)."
    )
    st.markdown(
        "[API Reference](https://docs.freeclimb.com/reference/api-reference-overview)  \n"
        "[llms.txt](https://docs.freeclimb.com/llms.txt)"
    )

st.markdown(
    """
    <div class="brand-block">
      <p class="brand-title">FreeClimb AI Assistant</p>
      <p class="brand-sub">Ask the FreeClimb API docs. Answers include source links.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("ask_form", clear_on_submit=False):
    question = st.text_input(
        "Your question",
        placeholder="e.g. How do I send an SMS?",
        label_visibility="collapsed",
    )
    ask = st.form_submit_button("Ask", type="primary")

if ask:
    if not question.strip():
        st.warning("Enter a question first.")
        st.stop()

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    session_id = st.session_state["session_id"]

    # Visible feedback (form submit only flashes the top-right running icon otherwise)
    progress = st.status("Working on your question…", expanded=True)
    progress.markdown(f"**You asked:** {question}")
    progress.markdown("Retrieving FreeClimb docs and generating an answer…")

    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "question": question,
                "session_id": session_id,
            },
            headers={"X-API-Key": os.getenv("API_KEY")},
            stream=True,
        )
    except requests.RequestException as e:
        progress.update(label="Request failed", state="error")
        st.error(f"Could not reach the API: {e}")
        st.stop()

    if response.status_code == 401:
        progress.update(label="Unauthorized", state="error")
        st.error("Unauthorized — check API_KEY in your .env")
        st.stop()

    if response.status_code != 200:
        progress.update(label="API error", state="error")
        st.error(f"API error ({response.status_code}). Is the FastAPI server running?")
        st.stop()

    placeholder = st.empty()
    full_stream = ""
    started = False

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            if not started:
                progress.update(label="Streaming answer…", state="running")
                started = True
            full_stream += chunk
            if "__SOURCES__" not in full_stream:
                placeholder.markdown(full_stream)

    if "__SOURCES__" not in full_stream:
        progress.update(label="Done", state="complete")
        placeholder.markdown(full_stream)
        st.stop()

    answer_text, sources_text = full_stream.split("__SOURCES__", 1)
    placeholder.markdown(answer_text.strip())
    progress.update(label="Done", state="complete")

    sources = [
        source.strip()
        for source in sources_text.split("\n")
        if source.strip()
    ]

    st.markdown("---")
    st.markdown("#### Sources")
    if not sources:
        st.caption("No source URLs returned for this answer.")
    else:
        for source in sources:
            st.markdown(f"- [{source}]({source})")
