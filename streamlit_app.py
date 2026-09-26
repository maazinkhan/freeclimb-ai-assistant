import streamlit as st
import requests
import uuid
from pydantic_settings import sources
import os
from dotenv import load_dotenv
load_dotenv()

st.title("🤖 FreeClimb AI Assistant")
st.write("Ask anything about the FreeClimb documentation.")

question = st.text_input("Ask a question")

if st.button("Ask"):
    # Persist one ID across Streamlit reruns for this conversation.
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    session_id = st.session_state["session_id"]

    with st.spinner("Thinking..."):
        # Same API_KEY as FastAPI (.env); sent as header, not in JSON body
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={
                "question": question,
                "session_id": session_id
            },
            headers={"X-API-Key": os.getenv("API_KEY")},
            stream=True
        )

    if response.status_code == 401:
        st.error("Unauthorized — check API_KEY")
        st.stop()

    placeholder = st.empty()

    full_stream = ""

    for chunk in response.iter_content(
            chunk_size=None,
            decode_unicode=True
    ):
        if chunk:
            full_stream += chunk

            if "__SOURCES__" not in full_stream:
                placeholder.markdown(full_stream)

    answer_text, sources_text = full_stream.split(
        "__SOURCES__",
        1
    )

    placeholder.markdown(answer_text.strip())

    sources = [
        source.strip()
        for source in sources_text.split("\n")
        if source.strip()
    ]



    st.subheader("Sources")

    for source in sources:
        st.markdown(f"- [{source}]({source})")