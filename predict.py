# backend/predict.py
import numpy as np
from backend.model_loader import model, labels
from backend.preprocess import preprocess_image
import json
import os

# load medicine recommendations
RECOMMEND_FILE = os.path.join(os.path.dirname(__file__), "recommendations.json")
with open(RECOMMEND_FILE, "r") as f:
    MEDICINES = json.load(f)


def single_predict(image_bytes, top_k=3):
    img = preprocess_image(image_bytes)

    preds = model.predict(img)[0]
    sorted_idx = np.argsort(preds)[::-1][:top_k]

    results = []
    for idx in sorted_idx:
        label = labels[idx]
        results.append({
            "label": label,
            "confidence": float(preds[idx]),
            "treatment": MEDICINES.get(label, "No treatment available")
        })

    crop = labels[sorted_idx[0]].split("_")[0]

    return {
        "crop": crop,
        "top_k": results
    }
