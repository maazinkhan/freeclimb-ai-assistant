import streamlit as st
import requests
import uuid
from pydantic_settings import sources

st.title("🤖 FreeClimb AI Assistant")
st.write("Ask anything about the FreeClimb documentation.")

question = st.text_input("Ask a question")

if st.button("Ask"):

    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())

    session_id = st.session_state["session_id"]

    with st.spinner("Thinking..."):
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={
                "question": question,
                "session_id": session_id
            }
        )

        answer = response.json()["answer"]
        sources =response.json()["sources"]

    st.write(answer)

    st.subheader("Sources")

    for source in sources:
        st.markdown(f"- [{source}]({source})")