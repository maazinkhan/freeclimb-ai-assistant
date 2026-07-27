import streamlit as st
import requests

st.title("🤖 FreeClimb AI Assistant")
st.write("Ask anything about the FreeClimb documentation.")

question = st.text_input("Ask a question")

if st.button("Ask"):
    with st.spinner("Thinking..."):
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"question": question}
        )

        answer = response.json()["answer"]

    st.write(answer)