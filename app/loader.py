from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

urls = ["https://docs.freeclimb.com/reference/using-the-api"]

def load_documents(urls: list[str]) -> list[Document]:


    loader = WebBaseLoader(urls)
    return loader.load()

