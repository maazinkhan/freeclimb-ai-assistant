from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def load_documents(urls: list[str], batch_size: int = 15) -> list[Document]:
    docs = []
    for i in range(0, len(urls), batch_size):
        batch = urls[i : i + batch_size]
        print(f"Loading URLs {i + 1}–{i + len(batch)} / {len(urls)}")
        docs.extend(WebBaseLoader(batch).load())
    return docs

