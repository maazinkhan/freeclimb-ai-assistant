from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langchain_chroma import Chroma
from pathlib import Path


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

PERSIST_DIRECTORY = str(BASE_DIR / "data" / "chroma")
EMBEDDING_MODEL = "gemini-embedding-2-preview"

def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def create_vectorstore(chunks):

    vector_store = Chroma.from_documents(
        embedding = get_embedding_model(),
        documents=chunks,
        persist_directory= PERSIST_DIRECTORY
    )

    return vector_store


def load_vector_store():

    vector_store = Chroma(
        embedding_= get_embedding_model(),
        persist_directory= PERSIST_DIRECTORY
    )

    return vector_store