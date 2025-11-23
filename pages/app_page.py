# frontend/pages/app_page.py
import streamlit as st
from pathlib import Path

def app():
    st.markdown('<div id="home"></div>', unsafe_allow_html=True)

    # Hero image path uses your uploaded file path (tool will transform sandbox: path to URL)
    HERO_IMAGE = "sandbox:/mnt/data/test.zip"

    st.markdown(f"""
    <section class="hero">
      <div class="hero-inner">
        <div class="hero-text">
          <h1>AI-Driven Crop Disease Detection</h1>
          <p class="lead">Reducing losses and boosting agricultural profits — instant disease detection on-device or in the cloud.</p>
          <div class="hero-cta">
            <a class="btn primary" href="#" onclick="document.querySelector('[aria-label=Go to Detect]').click();">Try Detect</a>
            <a class="btn outline" href="#" onclick="document.querySelector('[aria-label=Go to Live Camera]').click();">Open Live Camera</a>
          </div>
        </div>
        <div class="hero-media">
          <img src="{HERO_IMAGE}" alt="Hero" class="hero-img">
        </div>
      </div>
    </section>
    """, unsafe_allow_html=True)

    st.markdown("""
    <section class="features">
      <div class="feature-cards">
        <div class="card"><h3>Accurate Detection</h3><p>State-of-the-art CNN models for multi-crop disease detection.</p></div>
        <div class="card"><h3>Actionable Advice</h3><p>Crop-specific treatment recommendations and store locators.</p></div>
        <div class="card"><h3>History & Reports</h3><p>Track scans, download PDF reports and analyze trends.</p></div>
      </div>
    </section>
    """, unsafe_allow_html=True)
