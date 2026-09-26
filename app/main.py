from fastapi import FastAPI
from pydantic import BaseModel
from app.chat import ask, ask_structured
from uuid import UUID
from fastapi.responses import StreamingResponse
import logging
import time
from fastapi import HTTPException

# App-wide log format/level (used by logger.info / logger.exception below)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    question: str
    session_id: UUID

app = FastAPI()

@app.get("/")
def root():
    return { "message": "RAG API is running" }

# Streaming: log start only; sources live at end of the stream (__SOURCES__)
@app.post("/chat")
def chat(request: ChatRequest):
    logger.info(
        "chat request session_id=%s and question=%s",
        request.session_id,
              request.question
    )
    try:
        result = ask(
            question=request.question,
            session_id=request.session_id
        )
        logger.info(
            "chat ok session_id=%s",
            request.session_id
        )
        return StreamingResponse(
            result,
            media_type="text/plain"
        )
    except Exception:
        logger.exception(
            "chat failed session_id=%s",
            request.session_id
        )
        raise HTTPException(status_code=500, detail="chat failed")

# Non-streaming: log total duration + sources after ask_structured returns
@app.post("/chat/structured")
def chat_structured(request: ChatRequest):
    logger.info(
        "structured_chat request session_id=%s question=%s",
        request.session_id,
        request.question,
    )
    start = time.perf_counter()
    try:
        response = ask_structured(
            question=request.question,
            session_id=str(request.session_id),
        )
        elapsed = time.perf_counter() - start
        logger.info(
            "structured_chat ok session_id=%s duration_s=%.3f sources=%s",
            request.session_id,
            elapsed,
            response.sources,
        )
        return response
    except Exception:
        logger.exception(
            "structured_chat failed session_id=%s",
            request.session_id,
        )
        raise HTTPException(status_code=500, detail="Chat failed")