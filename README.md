# 🤖 FreeClimb AI Assistant

An AI-powered assistant that answers questions about the FreeClimb documentation using Retrieval-Augmented Generation (RAG).

The application indexes the official FreeClimb documentation into a vector database and retrieves the most relevant documentation before generating answers with Gemini.

---

## Features

- 📄 RAG over FreeClimb documentation
- 🔍 ChromaDB vector search
- 🎯 MMR (Maximal Marginal Relevance) retrieval
- 💬 Session-based conversation history
- ⚡ Real-time streaming responses
- 🔗 Source citations with clickable documentation links
- 🧠 LangChain prompt composition
- 🚀 FastAPI backend
- 🎨 Streamlit frontend

---

## Tech Stack

- Python
- LangChain
- ChromaDB
- Google Gemini 2.5 Flash
- Google Gemini Embeddings
- FastAPI
- Streamlit

---

## Project Structure

```text
.
├── app/
│   ├── loader.py
│   ├── splitter.py
│   ├── vectorstore.py
│   ├── retriever.py
│   ├── prompts.py      # Prompt composition
│   ├── chat.py         # RAG pipeline & conversation history
│   ├── index.py
│   └── main.py
│
├── data/
│   ├── docs/
│   └── chroma/
│
├── streamlit.py
├── requirements.txt
└── README.md
```

---

## How It Works

1. Load FreeClimb documentation
2. Split documents into chunks
3. Generate embeddings
4. Store embeddings in ChromaDB
5. Retrieve relevant chunks using MMR
6. Build a prompt using:
   - Conversation history
   - Retrieved context
   - Current question
7. Generate a streamed response using Gemini
8. Display clickable source citations

---

## Running the Project

### Install dependencies

```bash
pip install -r requirements.txt
```

### Index the documentation

```bash
python app/index.py
```

### Start FastAPI

```bash
uvicorn app.main:app --reload
```

### Start Streamlit

```bash
streamlit run streamlit.py
```

---

## Future Improvements

- Hybrid Search
- Reranking
- Authentication
- Docker
- Deployment
- Conversation summarization