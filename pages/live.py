# frontend/pages/live.py
import streamlit as st
from pages.assets.utils import chat_reply

def app():
    st.markdown('<div id="chat"></div>', unsafe_allow_html=True)
    st.title("Chatbot — Ask about crops & treatments")
    st.write("Ask natural language questions. For ChatGPT-quality answers, set OPENAI_API_KEY in env and enable cloud mode in utils.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    def send_message(text):
        st.session_state["chat_history"].append({"role":"user","text":text})
        reply = chat_reply(text)
        st.session_state["chat_history"].append({"role":"bot","text":reply})

    col_input = st.container()
    with col_input:
        msg = st.text_input("Type your question", key="chat_input")
        if st.button("Send"):
            if msg:
                send_message(msg)
                st.experimental_rerun()

    # render chat history
    for entry in st.session_state["chat_history"]:
        if entry["role"] == "user":
            st.markdown(f"**You:** {entry['text']}")
        else:
            st.markdown(f"**Assistant:** {entry['text']}")
