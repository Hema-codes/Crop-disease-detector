# backend/model_loader.py
import os
import tensorflow as tf

MODEL_PATH = os.path.join(os.path.dirname(__file__), "saved_model", "best_model.h5")

model = None
labels = []

def load_model():
    global model, labels
    if model is not None:
        return model
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file not found at {MODEL_PATH}")
    model = tf.keras.models.load_model(MODEL_PATH)
    # load labels from labels.txt if available
    labels_file = os.path.join(os.path.dirname(__file__), "labels.txt")
    if os.path.exists(labels_file):
        with open(labels_file, "r") as f:
            labels = [l.strip() for l in f.readlines() if l.strip()]
    return model

# call at import time
try:
    load_model()
except Exception as e:
    # print to server logs so you see the issue on startup
    print("Model loading warning:", e)
