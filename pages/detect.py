# frontend/pages/detect.py
import streamlit as st
from PIL import Image
import io
from pages.assets.utils import predict_pil_image

def app():
    st.markdown('<div id="detect"></div>', unsafe_allow_html=True)
    st.title("Detect — Upload Image")
    st.write("Upload a leaf/crop image. The backend model will return top predictions and recommendations.")

    uploaded = st.file_uploader("Upload image (jpg, png)", type=["jpg","jpeg","png"])
    if not uploaded:
        st.info("Upload a photo or use Live Camera.")
        return

    try:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, use_column_width=True, caption="Uploaded image")
    except Exception as e:
        st.error("Could not read image.")
        return

    if st.button("Predict"):
        with st.spinner("Contacting backend..."):
            try:
                # predict_pil_image wraps sending to backend and returns JSON
                out = predict_pil_image(img)
                st.success("Prediction completed")
                # Top-K card
                if out.get("top_k"):
                    st.markdown("### 🔍 Top predictions")
                    for p in out["top_k"]:
                        label = p.get("label")
                        conf = p.get("confidence", p.get("prob", 0))
                        st.markdown(f"- **{label}** — {conf*100:.1f}%")
                # Recommendation
                rec = out.get("recommendation") or out.get("treatment")
                if rec:
                    st.markdown("### 💊 Recommendation")
                    st.write(rec)
                # Save last JSON to session for download
                st.session_state["last_predict"] = out
                st.download_button("Download prediction (JSON)", data=str(out), file_name="prediction.json")
            except Exception as e:
                st.error(f"Prediction error: {e}")
