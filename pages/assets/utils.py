# frontend/pages/assets/utils.py
import os
import requests
import json
from io import BytesIO
from PIL import Image
import base64

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")  # optional

def predict_image_bytes(image_bytes, timeout=30):
    url = f"{BACKEND_URL}/predict"
    files = {"file": ("img.jpg", image_bytes, "image/jpeg")}
    r = requests.post(url, files=files, timeout=timeout)
    r.raise_for_status()
    return r.json()

def predict_pil_image(pil_img):
    buf = BytesIO()
    pil_img.save(buf, format="JPEG")
    buf.seek(0)
    return predict_image_bytes(buf.getvalue())

def get_history(limit=200):
    url = f"{BACKEND_URL}/history"
    r = requests.get(url, params={"limit": limit}, timeout=10)
    r.raise_for_status()
    return r.json()

def get_scan(scan_id):
    url = f"{BACKEND_URL}/scan/{scan_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def get_admin_stats(token):
    url = f"{BACKEND_URL}/admin/stats"
    r = requests.get(url, params={"token": token}, timeout=10)
    r.raise_for_status()
    return r.json()

# ---- Chatbot logic: rule-based -> optional OpenAI fallback ----
_RECS = {
    "tomatoearlyblight": "Apply copper-based fungicide and remove infected leaves. Improve air circulation.",
    "tomatoyellowcurlvirus": "Remove infected plants and control whiteflies. Use resistant varieties.",
    "potatoearlyblight": "Use recommended fungicides and rotate crops.",
    "healthy": "Plant appears healthy; continue monitoring."
}

def chat_reply(question: str):
    q = question.lower()
    # exact disease name match
    for d,k in _RECS.items():
        if d in q.replace(" ", ""):
            return f"**{d}**: {_RECS[d]}"
    # substring disease keyword
    for d in _RECS:
        if any(part in q for part in d.split()):
            return f"**{d}**: {_RECS[d]}"
    # If OPENAI_KEY present, call OpenAI GPT (optional)
    if OPENAI_KEY:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system","content":"You are an expert agronomist. Give short, actionable advice."},
                    {"role":"user","content":question}
                ],
                max_tokens=300
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            # fallback text
            return "OpenAI call failed: " + str(e)
    return "I couldn't match the disease. Try typing a disease name (e.g. TomatoEarlyBlight) or upload an image on Detect."

# image helper
def pil_from_bytes(b):
    return Image.open(BytesIO(b)).convert("RGB")
