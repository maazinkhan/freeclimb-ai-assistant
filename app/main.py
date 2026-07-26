from fastapi import FastAPI
from pydantic import BaseModel
from app.chat import ask

class ChatRequest(BaseModel):
    question: str

app = FastAPI()

@app.get("/")
def root():
    return { "message": "RAG API is running" }

@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask(question=request.question)
    return { "answer": answer }