from fastapi import FastAPI
from pydantic import BaseModel
from app.chat import ask
from uuid import UUID

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
    return result