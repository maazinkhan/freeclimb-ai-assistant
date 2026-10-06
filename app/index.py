from app.loader import load_documents
from app.splitter import split_documents
from app.vectorstore import create_vectorstore
from pathlib import Path
import os
import shutil


BASE_DIR = Path(__file__).resolve().parent.parent

def load_urls(path: Path) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


urls = load_urls(BASE_DIR / "data" / "doc_urls.txt")
print(f"Indexing {len(urls)} URLs")

documents = load_documents(urls)

chunks = split_documents(documents)

# Default: keep existing Chroma and resume mid-run.
# Set FORCE_REINDEX=1 only when you intentionally want a full rebuild.
chroma_dir = BASE_DIR / "data" / "chroma"
force = os.getenv("FORCE_REINDEX", "").strip() in ("1", "true", "True")
if force and chroma_dir.exists():
    print("FORCE_REINDEX=1 — wiping chroma and starting fresh")
    shutil.rmtree(chroma_dir)

vector_store = create_vectorstore(chunks, resume=not force)

print(f"Loaded {len(documents)} documents")
print(f"Created {len(chunks)} chunks")
print(f"Vector store now has {vector_store._collection.count()} chunks")
print("Vector store created")


