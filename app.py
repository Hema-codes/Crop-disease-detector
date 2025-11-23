# frontend/app.py
import streamlit as st
import os
from importlib import import_module

st.set_page_config(page_title="AI-Driven Crop Disease Detection", layout="wide", page_icon="🌿")

BASE_DIR = os.path.dirname(__file__)
ASSETS = os.path.join(BASE_DIR, "pages", "assets")
CSS_PATH = os.path.join(ASSETS, "styles.css")

# Load CSS
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top navbar (styled via CSS)
st.markdown("""
<nav class="top-nav">
  <div class="nav-left">
    <div class="logo">🌿 CropAI</div>
  </div>
  <div class="nav-right">
    <a href="#home">Home</a>
    <a href="#detect">Detect</a>
    <a href="#live">Live Camera</a>
    <a href="#history">History</a>
    <a href="#chat">Chatbot</a>
    <a href="#admin">Admin</a>
  </div>
</nav>
""", unsafe_allow_html=True)

# Sidebar replaced with a compact page selector for app routing
st.sidebar.title("Navigate")
pages = {
    "Home": "app_page",
    "Detect": "detect",
    "Live Camera": "Live_Camera",
    "History": "history",
    "Chatbot": "live",
    "Admin": "admin"
}
choice = st.sidebar.radio("Go to", list(pages.keys()), index=0)

# dynamic import and run
module_name = f"pages.{pages[choice]}"
try:
    page = import_module(module_name)
    if hasattr(page, "app"):
        page.app()
    elif hasattr(page, "render"):
        page.render()
    else:
        st.error(f"Page {module_name} missing app()/render().")
except ModuleNotFoundError:
    st.error(f"Page module {module_name} not found. Check files in pages/")
except Exception as e:
    st.exception(e)
    st.error("Error loading page.")
