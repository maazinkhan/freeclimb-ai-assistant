from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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