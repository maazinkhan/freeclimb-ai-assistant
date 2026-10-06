# FreeClimb AI Assistant

RAG chatbot over FreeClimb documentation: retrieve relevant `.md` docs from ChromaDB, then answer with Gemini via FastAPI (streaming + structured JSON). Streamlit UI for demos.

## Live demo

**UI:** [FreeClimb AI Assistant on Streamlit](https://freeclimb-ai-assistant.streamlit.app)

**API:** [https://freeclimb-ai-assistant-production.up.railway.app](https://freeclimb-ai-assistant-production.up.railway.app)  
(`GET /` health check; chat routes require `X-API-Key`)

Architecture: public Streamlit → server-side `API_KEY` → Railway FastAPI (Chroma baked into the image).

---

## What this solves

FreeClimb’s product surface is a large REST API and docs set — voice, SMS, accounts, applications, PerCL, and more. Developers normally hunt through the [API Reference](https://docs.freeclimb.com/reference/api-reference-overview) (and related guides) by hand.

This project turns that documentation into a **question-answering assistant**: you ask in natural language, the app retrieves the most relevant FreeClimb doc chunks, and Gemini answers with citations back to the docs.

Docs are ingested from FreeClimb’s AI-friendly `.md` pages (see their [`llms.txt`](https://docs.freeclimb.com/llms.txt) index), not only the HTML site. Coverage today is the **API Reference** corpus in `data/doc_urls.txt`.

---

## Features

- RAG over FreeClimb API docs (MMR retrieval, source citations)
- Session-based conversation history
- Streaming `POST /chat` and structured JSON `POST /chat/structured`
- API key auth (`X-API-Key`)
- Request logging + retrieval/LLM timing
- Docker image with **baked Chroma** (Railway-ready)
- Streamlit UI (local or Streamlit Community Cloud)

---

## Tech stack

Python · LangChain (LCEL) · ChromaDB · Google Gemini · FastAPI · Streamlit · Docker · Railway

---

## Prerequisites

- Python 3.12+ recommended
- A [Google AI](https://ai.google.dev/) API key (Gemini)
- For Docker path: [Docker Desktop](https://www.docker.com/products/docker-desktop/) or [Rancher Desktop](https://rancherdesktop.io/) running

---

## Quick start (local)

### 1. Clone and enter the project

```bash
git clone https://github.com/maazinkhan/freeclimb-ai-assistant.git
cd freeclimb-ai-assistant
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
- Optional: `API_URL` — FastAPI base URL for Streamlit (defaults to `http://127.0.0.1:8000`)

### 4. Vector index

`data/chroma/` is **committed** (prebuilt index for deploy). For local API you can use it as-is.

To rebuild or resume after a rate-limit stop:

```bash
python -m app.index
```

Default **resumes** (keeps existing chunks). Full wipe + rebuild:

```bash
FORCE_REINDEX=1 python -m app.index
```

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

Leave `API_URL` unset to talk to local FastAPI. Streamlit reads `API_KEY` from `.env` (or Streamlit secrets in Cloud).

---

## Run the API with Docker

Chroma is **copied into the image** at build time (same path the app loads: `data/chroma/`).

```bash
docker compose up --build
```

API: http://127.0.0.1:8000/docs  

Stop: `Ctrl+C`, then optionally `docker compose down`.

Equivalent:

```bash
docker build -t fcchat-api .
docker run --rm -p 8000:8000 --env-file .env fcchat-api
```

---

## Deployed stack

| Piece | Where | Notes |
|-------|--------|--------|
| FastAPI + Chroma | [Railway](https://railway.app) | Dockerfile bake; env: `GOOGLE_API_KEY`, `API_KEY` |
| Streamlit UI | [Streamlit Community Cloud](https://share.streamlit.io) | Secrets: `API_URL` (Railway base URL), `API_KEY` |

Recruiters use the Streamlit URL; they never see the API key.

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
│   └── index.py          # Build / resume Chroma index
├── data/
│   ├── chroma/           # Vector DB (committed; baked into Docker)
│   └── doc_urls.txt      # API Reference .md URLs
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
| `401 Unauthorized` | `.env` / Cloud secrets have matching `API_KEY`; send `X-API-Key` header (not in JSON body) |
| Streamlit Cloud hits `127.0.0.1` | Set secrets `API_URL` + `API_KEY`; reboot the app |
| Empty / weak answers | Confirm `data/chroma` present; re-run `python -m app.index` if needed |
| Docker can’t connect | Start Docker Desktop or Rancher Desktop; retry `docker info` |
| Port 8000 in use | Stop other uvicorn/Compose; or change the host port mapping |
| Gemini `503` / stream cut off | Temporary model capacity; retry later |

---

## Roadmap / next

- Eval harness + CI (Milestone 4) — **next**
- Optional: MLflow tracing; hybrid search / reranking
- Optional: architecture diagram + eval numbers in README after harness
