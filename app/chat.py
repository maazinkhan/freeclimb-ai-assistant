from app.vectorstore import load_vector_store
from app.retriever import create_retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


vector_store = load_vector_store()

retriever = create_retriever(vector_store)

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)

prompt = ChatPromptTemplate.from_template(
        """
    Answer using the provided context.

    If the context contains an endpoint definition but no language-specific
    code sample, you may generate a concise example from the documented
    HTTP method, URL, parameters, and authentication.
    
    Clearly label it as a generated example.
    
    Do not invent undocumented endpoint details.

    Context:
    {context}

    Question:
    {question}
    """
    )

def ask(question):

    docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    sources = []
    seen = set()

    for doc in docs:
        url = doc.metadata["source"].replace(".md", "")

        if url not in seen:
            sources.append(url)
            seen.add(url)


    message = prompt.invoke(
        {
            "context": context,
            "question": question
        }
    )


    response = llm.invoke(message)

    answer = {
        "answer":response.content,
        "sources":sources
    }

    return answer



if __name__ == "__main__":
    while True:
        question = input("\nAsk a question (or 'quit'): ")

        if question.lower() == "quit":
            break

        answer = ask(question)
        print("\nAnswer:")
        print(answer)


