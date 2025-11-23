# frontend/pages/admin.py
import streamlit as st
from pages.assets.utils import get_admin_stats

def app():
    st.markdown('<div id="admin"></div>', unsafe_allow_html=True)
    st.title("Admin")
    token = st.text_input("Admin token", type="password")
    if st.button("Get stats"):
        if not token:
            st.error("Admin token required")
            return
        try:
            data = get_admin_stats(token)
            st.json(data)
        except Exception as e:
            st.error(f"Failed: {e}")
