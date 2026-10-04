from app.loader import load_documents
from app.splitter import split_documents
from app.vectorstore import create_vectorstore
from pathlib import Path
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

chroma_dir = BASE_DIR / "data" / "chroma"
if chroma_dir.exists():
    shutil.rmtree(chroma_dir)

vector_store = create_vectorstore(chunks)

print(f"Loaded {len(documents)} documents")
print(f"Created {len(chunks)} chunks")
print("Vector store created")


