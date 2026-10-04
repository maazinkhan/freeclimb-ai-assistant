from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import time
from langchain_chroma import Chroma
from pathlib import Path


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

PERSIST_DIRECTORY = str(BASE_DIR / "data" / "chroma")
EMBEDDING_MODEL = "gemini-embedding-2"

# Free tier: ~100 embed requests/minute — pause between batches to avoid 429
EMBED_BATCH_SIZE = 25
EMBED_SLEEP_SECONDS = 20


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def create_vectorstore(chunks):
    """
    Build Chroma by embedding chunks in small batches with sleeps.

    from_documents(all_chunks) fires many Gemini embed calls at once and
    hits free-tier rate limits. We add 25 chunks, wait 20s, repeat.
    """
    embedding = get_embedding_model()
    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=PERSIST_DIRECTORY,
    )

    total = len(chunks)
    for i in range(0, total, EMBED_BATCH_SIZE):
        batch = chunks[i : i + EMBED_BATCH_SIZE]
        print(f"Embedding chunks {i + 1}–{i + len(batch)} / {total}")
        vector_store.add_documents(batch)

        # Don't sleep after the last batch
        if i + EMBED_BATCH_SIZE < total:
            print(
                f"Sleeping {EMBED_SLEEP_SECONDS}s "
                "(Gemini free-tier embed rate limit)..."
            )
            time.sleep(EMBED_SLEEP_SECONDS)

    return vector_store


def load_vector_store():

    vector_store = Chroma(
        embedding_function=get_embedding_model(),
        persist_directory=PERSIST_DIRECTORY
    )

    return vector_store
