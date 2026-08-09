from app.vectorstore import load_vector_store
from app.retriever import create_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

vector_store = load_vector_store()

retriever = create_retriever(vector_store)

llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful AI assistant.

            Answer using the provided context.

            If the context contains an endpoint definition but no
            language-specific code sample, you may generate a concise
            example from the documented HTTP method, URL, parameters,
            and authentication.

            Clearly label generated examples.

            If the answer cannot be determined from the context
            or conversation history, say you don't know.
            """
        ),

        MessagesPlaceholder("history"),

        (
            "human",
            """
            Context:
            {context}

            Question:
            {question}
            """
        )
    ]
)

histories = {}

def ask(question, session_id):
    if session_id not in histories:
        histories[session_id] = []

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

    response = llm.invoke(message)

    history.append(
        HumanMessage(content=question)
    )

    history.append(
        AIMessage(content=response.content)
    )

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

        answer = ask(question, session_id="test-session")
        print("\nAnswer:")
        print(answer)


