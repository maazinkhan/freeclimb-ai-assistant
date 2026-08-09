from app.vectorstore import load_vector_store
from app.retriever import create_retriever
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from app.prompts import prompt

vector_store = load_vector_store()

retriever = create_retriever(vector_store)

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)



# Store conversation history per session so different users
# do not share the same chat context.
histories = {}

def ask(question, session_id):
    if session_id not in histories:
        histories[session_id] = []

    # Keep the current question separate from history.
    # It is appended only after the LLM responds to avoid sending it twice.
    history = histories[session_id]

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
            "history": history,
            "context": context,
            "question": question
        }
    )

    # Keep the full streamed answer so it can be saved
    # as one AIMessage in conversation history.
    full_response = ""

    for chunk in llm.stream(message):
        full_response += chunk.content
        yield chunk.content

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


