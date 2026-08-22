from app.vectorstore import load_vector_store
from app.retriever import create_retriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from app.prompts import prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough,RunnableParallel

vector_store = load_vector_store()

retriever = create_retriever(vector_store)

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)



# Store conversation history per session so different users
# do not share the same chat context.
histories = {}

chain = prompt | llm |  StrOutputParser()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


# RunnableLambda is used to format the documents as a string.

format_docs_runnable = RunnableLambda(format_docs) 

retrieval_chain = retriever | format_docs_runnable


rag_inputs = RunnableParallel(
    context=retrieval_chain,
    question=RunnablePassthrough(),
)

def ask(question, session_id):
    if session_id not in histories:
        histories[session_id] = []

    # Keep the current question separate from history.
    # It is appended only after the LLM responds to avoid sending it twice.
    history = histories[session_id]

    docs = retriever.invoke(question) 

    result = rag_inputs.invoke(question)
    result["history"] = history 

    sources = []
    seen = set()

    for doc in docs:
        url = doc.metadata["source"].replace(".md", "")

        if url not in seen:
            sources.append(url)
            seen.add(url)


    # Keep the full streamed answer so it can be saved
    # as one AIMessage in conversation history.
    full_response = ""

    for chunk in chain.stream(result):
        full_response += chunk
        yield chunk


    history.append(
        HumanMessage(content=question)
    )

    history.append(
        AIMessage(content=full_response)
    )

    # Marker separates streamed answer text from source metadata.
    # Later this can be replaced with structured SSE/JSON events.
    yield "\n__SOURCES__\n"
    yield "\n".join(sources)




if __name__ == "__main__":
    while True:
        question = input("\nAsk a question (or 'quit'): ")

        if question.lower() == "quit":
            break

        answer = ask(question, session_id="test-session")
        print("\nAnswer:")
        print(answer)
