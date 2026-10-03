# FreeClimb AI Assistant

RAG chatbot over FreeClimb documentation: retrieve relevant `.md` docs from ChromaDB, then answer with Gemini via FastAPI (streaming + structured JSON). Streamlit UI optional.

## What this solves

FreeClimb’s product surface is a large REST API and docs set — voice, SMS, accounts, applications, PerCL, and more. Developers normally hunt through the [API Reference](https://docs.freeclimb.com/reference/api-reference-overview) (and related guides) by hand.

This project turns that documentation into a **question-answering assistant**: you ask in natural language, the app retrieves the most relevant FreeClimb doc chunks, and Gemini answers with citations back to the docs.

Docs are ingested from FreeClimb’s AI-friendly `.md` pages (see their [`llms.txt`](https://docs.freeclimb.com/llms.txt) index), not only the HTML site.

---

## Features

- RAG over FreeClimb docs (MMR retrieval, source citations)
- Session-based conversation history
- Streaming `POST /chat` and structured JSON `POST /chat/structured`
- API key auth (`X-API-Key`)
- Request logging + retrieval/LLM timing
- Docker / Compose for the API

---

## Tech stack

Python · LangChain (LCEL) · ChromaDB · Google Gemini · FastAPI · Streamlit · Docker

---

## Prerequisites

- Python 3.12+ recommended
- A [Google AI](https://ai.google.dev/) API key (Gemini)
- For Docker path: [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Rancher Desktop](https://rancherdesktop.io/) running

---

## Quick start (local)

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd FCchat
```

### 2. Create a virtualenv and install deps

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure secrets

Create a `.env` file in the project root (do **not** commit it):

```env
GOOGLE_API_KEY=your-google-api-key
API_KEY=your-own-random-secret
USER_AGENT=FCChat/1.0
```

- `GOOGLE_API_KEY` — embeddings + Gemini  
- `API_KEY` — shared secret for FastAPI / Streamlit (`X-API-Key` header)

### 4. Build the vector index

`data/chroma/` is **not** in git. You must index once (needs network + `GOOGLE_API_KEY`):

```bash
python -m app.index
```

You should see document/chunk counts and “Vector store created”.

### 5. Start the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Health: http://127.0.0.1:8000/  
- Swagger: http://127.0.0.1:8000/docs  

Protected routes need header: `X-API-Key: <same as API_KEY in .env>`.

### 6. (Optional) Start the Streamlit UI

In a **second** terminal (venv activated, same `.env`):

```bash
streamlit run streamlit_app.py
```

Streamlit calls `http://127.0.0.1:8000/chat` and sends `X-API-Key` automatically.

---

## Run the API with Docker Compose

Index **once on the host** first (step 4 above) so `./data/chroma` exists. Compose mounts that folder into the container.

```bash
# from project root; Docker/Rancher must be running
docker compose up --build
```

API: http://127.0.0.1:8000/docs  

Stop: `Ctrl+C`, then optionally `docker compose down`.

Equivalent manual run:

```bash
docker build -t fcchat-api .
docker run --rm -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/data/chroma:/app/data/chroma" \
  fcchat-api
```

---

## API overview

| Method | Path | Auth | Notes |
|--------|------|------|--------|
| `GET` | `/` | No | Health check |
| `POST` | `/chat` | `X-API-Key` | Streaming text; sources after `__SOURCES__` |
| `POST` | `/chat/structured` | `X-API-Key` | JSON `{ "answer", "sources" }` |

Example:

```bash
curl -X POST http://127.0.0.1:8000/chat/structured \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-own-random-secret" \
  -d '{"question":"What is the base URL?","session_id":"3fa85f64-5717-4562-b3fc-2c963f66afa6"}'
```

`session_id` must be a UUID string.

---

## Project structure

```text
.
├── app/
│   ├── main.py           # FastAPI + auth + logging
│   ├── chat.py           # RAG pipeline (streaming + structured)
│   ├── prompts.py
│   ├── retriever.py
│   ├── vectorstore.py
│   ├── loader.py
│   ├── splitter.py
│   └── index.py          # Build Chroma index
├── data/chroma/          # Local vector DB (gitignored — create via index.py)
├── streamlit_app.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── .env                  # You create this (gitignored)
```

---

## How it works

1. Load FreeClimb `.md` docs → chunk → embed → Chroma  
2. On each question: MMR retrieve → format context → prompt (+ history) → Gemini  
3. Streaming path yields tokens then source URLs; structured path returns Pydantic JSON  

---

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `401 Unauthorized` | `.env` has `API_KEY`; send `X-API-Key` header (not in JSON body) |
| Empty / weak answers | Run `python -m app.index`; confirm `data/chroma` exists |
| Docker can’t connect | Start Docker Desktop or Rancher Desktop; retry `docker info` |
| Port 8000 in use | Stop other uvicorn/Compose; or change the host port mapping |

---

## Roadmap / next

- Public deploy (Railway / Render / similar)
- Broader doc index before eval harness
- Optional: Streamlit in Compose; MLflow later
