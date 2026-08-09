# Architecture

## High-Level Architecture

```text
User
 │
 ▼
Streamlit UI
 │
 ▼
FastAPI
 │
 ▼
chat.py
 │
 ├── Conversation History
 ├── Retriever
 ├── prompts.py
 └── Gemini
 │
 ▼
Streaming Response
 │
 ▼
Streamlit
```

---

# Retrieval Pipeline

```text
User Question
        │
        ▼
Embed Question
        │
        ▼
Chroma Retriever (MMR)
        │
        ▼
Top K Chunks
        │
        ▼
Prompt
        │
        ▼
Gemini
```

---

# Conversation History

Each Streamlit session creates one UUID.

```text
session_id
        │
        ▼
histories
```

```python
histories = {
    session_id: [
        HumanMessage(...),
        AIMessage(...),
        ...
    ]
}
```

Conversation history is inserted into the prompt using:

```
MessagesPlaceholder("history")
```

---

# Prompt Composition

The prompt is composed from four independent pieces.

```text
System Instructions

↓

Conversation History

↓

Retrieved Context

↓

Current User Question
```

LangChain combines these into the final prompt before sending it to Gemini.

---

# Streaming Responses

Instead of waiting for the entire answer:

```text
invoke()
```

the application streams chunks using

```text
stream()
```

Pipeline:

```text
Gemini

↓

AIMessageChunk

↓

yield

↓

FastAPI StreamingResponse

↓

HTTP Stream

↓

requests(stream=True)

↓

Streamlit placeholder
```

---

# Source Citations

Retrieved documents contain metadata:

```python
doc.metadata["source"]
```

Duplicate URLs are removed before streaming.

After the answer finishes streaming, a simple protocol is used:

```text
Answer

↓

__SOURCES__

↓

URL 1
URL 2
URL 3
```

The frontend detects the marker and renders clickable documentation links.

---

# Project Components

### loader.py

Loads Markdown documentation.

### splitter.py

Splits documents into chunks.

### vectorstore.py

Creates and loads the Chroma vector database.

### retriever.py

Creates the MMR retriever.

### prompts.py

Contains the LangChain `ChatPromptTemplate` used by the application.

The prompt is composed of:
- System instructions
- Conversation history (`MessagesPlaceholder`)
- Retrieved documentation context
- Current user question

Keeping the prompt separate from the chat logic makes it easier to modify prompt engineering without changing the RAG pipeline.

### chat.py

Coordinates retrieval, prompt construction, conversation history, streaming, and source citations.

### main.py

FastAPI API.

### streamlit.py

Frontend UI.