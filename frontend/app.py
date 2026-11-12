"""Streamlit client for IntelliDesk."""

import os

import requests
import streamlit as st

API_URL = os.getenv("INTELLIDESK_API_URL", "http://localhost:8000")

st.set_page_config(page_title="IntelliDesk", page_icon="💬", layout="wide")
st.title("IntelliDesk")
st.caption("Explainable customer support with source-grounded answers")

with st.sidebar:
    st.header("Knowledge base")
    uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"], accept_multiple_files=True)
    if st.button("Index documents", disabled=not uploaded_files):
        for uploaded_file in uploaded_files or []:
            with st.spinner(f"Indexing {uploaded_file.name}..."):
                response = requests.post(
                    f"{API_URL}/documents",
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")},
                    timeout=120,
                )
            if response.ok:
                st.success(f"{uploaded_file.name}: indexed {response.json()['chunks_indexed']} chunks")
            else:
                st.error(f"{uploaded_file.name}: {response.json().get('detail', response.text)}")

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("citations"):
            with st.expander("Sources"):
                for citation in message["citations"]:
                    st.markdown(
                        f"**{citation['document_name']} — page {citation['page_number']}** "
                        f"(confidence: {citation['confidence']:.2f})\n\n"
                        f"> {citation['snippet']}"
                    )

if prompt := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            response = requests.post(f"{API_URL}/query", json={"query": prompt}, timeout=120)
        if response.ok:
            result = response.json()
            st.markdown(result["answer"])
            with st.expander("Sources", expanded=True):
                for citation in result["citations"]:
                    st.markdown(
                        f"**{citation['document_name']} — page {citation['page_number']}** "
                        f"(confidence: {citation['confidence']:.2f})\n\n"
                        f"> {citation['snippet']}"
                    )
            st.session_state.messages.append(
                {"role": "assistant", "content": result["answer"], "citations": result["citations"]}
            )
        else:
            detail = response.json().get("detail", response.text)
            st.error(detail)
