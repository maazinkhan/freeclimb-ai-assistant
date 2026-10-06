from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import time
from langchain_chroma import Chroma
from pathlib import Path


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PERSIST_DIRECTORY = str(BASE_DIR / "data" / "chroma")
EMBEDDING_MODEL = "gemini-embedding-2"

# Free tier (~100 RPM): 25 chunks + 20s sleep ≈ 75 texts/min
EMBED_BATCH_SIZE = 25
EMBED_SLEEP_SECONDS = 20


def get_embedding_model():
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )


def create_vectorstore(chunks, resume: bool = True):
    """
    Embed chunks into Chroma in small batches with sleeps.

    Avoids from_documents(all) which bursts Gemini free-tier limits.
    With resume=True, skip chunks already in the store (same load/split order).
    """
    embedding = get_embedding_model()
    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=PERSIST_DIRECTORY,
    )

    total = len(chunks)
    start = 0
    if resume:
        existing = vector_store._collection.count()
        if existing:
            if existing >= total:
                print(
                    f"Nothing to do: store already has {existing} "
                    f"chunks (pipeline produced {total})."
                )
                return vector_store
            print(
                f"Resuming: {existing} chunks already embedded, "
                f"skipping those ({total - existing} left)"
            )
            start = existing

    for i in range(start, total, EMBED_BATCH_SIZE):
        batch = chunks[i : i + EMBED_BATCH_SIZE]
        print(f"Embedding chunks {i + 1}–{i + len(batch)} / {total}")
        vector_store.add_documents(batch)

        if i + EMBED_BATCH_SIZE < total:
            print(
                f"Sleeping {EMBED_SLEEP_SECONDS}s "
                "(Gemini free-tier embed rate limit)..."
            )
            time.sleep(EMBED_SLEEP_SECONDS)

    return vector_store


def load_vector_store():
    return Chroma(
        embedding_function=get_embedding_model(),
        persist_directory=PERSIST_DIRECTORY,
    )
