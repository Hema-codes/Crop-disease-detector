# backend/main.py
import os
import time
import io
import base64
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware

# relative imports (work when backend is a package or when you run from backend dir)
from .db import SessionLocal  # ensure backend/db.py exists
from .predict import single_predict  # must return dict or raise controlled exceptions
from .crud import create_scan_record, get_recent_scans, get_scan, delete_scan
from .report_generator import generate_pdf_report

from gtts import gTTS
import requests
from dotenv import load_dotenv

load_dotenv()

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "change_me")
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

app = FastAPI(title="Crop Disease Detection API (Full)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Crop Disease Detection API is running!"}

@app.post("/predict")
async def predict_endpoint(
    file: UploadFile = File(...),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    notes: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """
    Single image prediction. Returns top_k predictions, crop, and scan_id.
    """
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        # single_predict must return dict { "top_k": [ {"label":..., "confidence":...}, ... ], "crop": "..."}
        result = single_predict(image_bytes, top_k=3)
    except HTTPException:
        raise
    except Exception as e:
        # bubble up a helpful message
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    # store minimal info (use create_scan_record from crud)
    try:
        geo = f"{lat},{lon}" if lat is not None and lon is not None else None
        top = result.get("top_k", [])
        top_label = top[0]["label"] if top else None
        confidence = float(top[0]["confidence"]) if top else None
        scan = create_scan_record(db, image_bytes=image_bytes, crop=result.get("crop"), top_result=top_label, geo=geo, notes=notes, confidence=confidence)
        scan_id = getattr(scan, "id", None)
    except Exception:
        # if DB fails, still return prediction so frontend can show results
        scan_id = None

    return {"top_k": result.get("top_k", []), "crop": result.get("crop"), "scan_id": scan_id}

@app.post("/predict_live")
async def predict_live_endpoint(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file")
        result = single_predict(image_bytes, top_k=3)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Live prediction failed: {e}")

@app.get("/history")
def history(limit: int = 200, db = Depends(get_db)):
    rows = get_recent_scans(db, limit=limit)
    out = []
    for s in rows:
        out.append({
            "id": s.id,
            "timestamp": s.timestamp.isoformat(),
            "crop": s.crop,
            "label": s.top_label,
            "confidence": s.confidence,
            "image_path": s.image_path,
            "notes": s.notes,
            "treatment": s.treatment
        })
    return out

@app.get("/scan/{scan_id}")
def get_scan_endpoint(scan_id: int, db = Depends(get_db)):
    s = get_scan(db, scan_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {
        "id": s.id,
        "timestamp": s.timestamp.isoformat(),
        "crop": s.crop,
        "label": s.top_label,
        "confidence": s.confidence,
        "image_path": s.image_path,
        "notes": s.notes,
        "treatment": s.treatment
    }

@app.delete("/scan/{scan_id}")
def delete_scan_endpoint(scan_id: int, token: str = Query(...), db = Depends(get_db)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    ok = delete_scan(db, scan_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": True}

@app.get("/report/{scan_id}")
def report_endpoint(scan_id: int, db = Depends(get_db)):
    s = get_scan(db, scan_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    out_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"report_{scan_id}.pdf")
    generate_pdf_report(s, out)
    return {"report_path": out}

@app.post("/tts")
def tts_endpoint(body: dict = Body(...)):
    text = body.get("text", "")
    lang = body.get("lang", "en")
    if not text:
        raise HTTPException(status_code=400, detail="Missing text")
    fn = f"tts_{int(time.time())}.mp3"
    path = os.path.join(os.path.dirname(__file__), "tts_files")
    os.makedirs(path, exist_ok=True)
    full = os.path.join(path, fn)
    gTTS(text=text, lang=lang).save(full)
    return {"path": full}

@app.get("/stores")
def stores(lat: float, lon: float, radius: int = 5000, query: str = "agro shop"):
    if not GOOGLE_MAPS_API_KEY:
        return {"error": "Set GOOGLE_MAPS_API_KEY environment variable"}
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&keyword={query}&key={GOOGLE_MAPS_API_KEY}"
    resp = requests.get(url).json()
    places = [{"name": p.get("name"), "vicinity": p.get("vicinity")} for p in resp.get("results", [])]
    return {"places": places}

@app.post("/yield_estimate")
def yield_estimate(body: dict = Body(...)):
    disease = body.get("disease")
    severity = float(body.get("confidence", 0))
    base_loss = {"TomatoEarlyBlight":0.2, "TomatoYellowCurlVirus":0.5, "PotatoEarlyBlight":0.25}
    loss = base_loss.get(disease, 0.15) * severity
    return {"estimated_yield_loss_pct": round(loss*100,2)}

@app.get("/admin/stats")
def admin_stats(token: str = Query(...), db = Depends(get_db)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    rows = get_recent_scans(db, limit=1000)
    counts = {}
    for s in rows:
        counts[s.top_label] = counts.get(s.top_label, 0) + 1
    return {"counts": counts, "total_scans": len(rows)}
