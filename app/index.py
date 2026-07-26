from app.loader import load_documents
from app.splitter import split_documents
from app.vectorstore import create_vectorstore

urls = ["https://docs.freeclimb.com/reference/using-the-api"]

documents = load_documents(urls)

chunks = split_documents(documents)

vector_store = create_vectorstore(chunks)

print(f"Loaded {len(documents)} documents")
print(f"Created {len(chunks)} chunks")
print("Vector store created")


