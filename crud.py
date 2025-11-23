# backend/crud.py
import base64
from sqlalchemy.orm import Session
from datetime import datetime
from backend.db import Base, engine
from sqlalchemy import Column, Integer, String, Float, DateTime

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    crop = Column(String)
    top_label = Column(String)
    confidence = Column(Float)
    image_base64 = Column(String)   # store image as base64
    image_path = Column(String, nullable=True)
    geo = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    treatment = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)


def create_scan_record(db: Session, image_bytes, crop, top_result, geo, notes):
    encoded = base64.b64encode(image_bytes).decode()

    scan = Scan(
        crop=crop,
        top_label=top_result["label"],
        confidence=top_result["confidence"],
        image_base64=encoded,
        geo=geo,
        notes=notes,
        treatment=top_result.get("treatment", "")
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def get_recent_scans(db: Session, limit=50):
    return db.query(Scan).order_by(Scan.timestamp.desc()).limit(limit).all()


def get_scan(db: Session, scan_id: int):
    return db.query(Scan).filter(Scan.id == scan_id).first()


def delete_scan(db: Session, scan_id: int):
    scan = get_scan(db, scan_id)
    if not scan:
        return False
    db.delete(scan)
    db.commit()
    return True
