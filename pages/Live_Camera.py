# frontend/pages/Live_Camera.py
import streamlit as st
from PIL import Image, ImageOps
import io
from pages.assets.utils import predict_pil_image

def app():
    st.markdown('<div id="live"></div>', unsafe_allow_html=True)
    st.title("Live Camera — Capture & Predict")
    st.write("Use your webcam to capture a frame. Flip/rotate to simulate back camera or rotation.")

    cap = st.camera_input("Take a photo")
    mode = st.selectbox("Adjust orientation", ["Default", "Flip horizontally (back)", "Rotate 180°"])

    if cap:
        img = Image.open(cap).convert("RGB")
        if mode == "Flip horizontally (back)":
            img = ImageOps.mirror(img)
        elif mode == "Rotate 180°":
            img = img.rotate(180, expand=True)
        st.image(img, caption="Captured", use_column_width=True)
        col1, col2 = st.columns([1,1])
        with col1:
            if st.button("Predict from capture"):
                with st.spinner("Predicting..."):
                    try:
                        out = predict_pil_image(img)
                        st.success("Prediction complete")
                        if out.get("top_k"):
                            for p in out["top_k"]:
                                st.write(f"• {p['label']} — {p['confidence']*100:.1f}%")
                        if out.get("recommendation"):
                            st.markdown("**Recommendation:**")
                            st.write(out["recommendation"])
                    except Exception as e:
                        st.error(f"Prediction failed: {e}")
        with col2:
            if st.button("Retake"):
                st.experimental_rerun()
    else:
        st.info("Take a photo using your device camera.")
