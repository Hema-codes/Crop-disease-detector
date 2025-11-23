# frontend/pages/history.py
import streamlit as st
from pages.assets.utils import get_history

def app():
    st.markdown('<div id="history"></div>', unsafe_allow_html=True)
    st.title("History — Past Scans")
    st.write("List of recent scans saved on the backend (if DB enabled).")

    try:
        rows = get_history(limit=200)
        if not rows:
            st.info("No scans yet.")
            return
        for s in rows:
            with st.expander(f"Scan {s['id']} — {s.get('label')}"):
                st.json(s)
    except Exception as e:
        st.error(f"Could not retrieve history: {e}")
