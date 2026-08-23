from fastapi import FastAPI
from pydantic import BaseModel
from app.chat import ask, ask_structured
from uuid import UUID
from fastapi.responses import StreamingResponse

class ChatRequest(BaseModel):
    question: str
    session_id: UUID

app = FastAPI()

@app.get("/")
def root():
    return { "message": "RAG API is running" }

@app.post("/chat")
def chat(request: ChatRequest):
    result = ask(
        question=request.question,
        session_id=request.session_id
    )
    # return result
    return StreamingResponse(
        result,
        media_type="text/plain"
    )

@app.post("/chat/structured")
def chat_structured(request: ChatRequest):
    return ask_structured(
        question=request.question,
        session_id=str(request.session_id)
    )