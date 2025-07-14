from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import time

from models import Base, Scan, Issue
from database import engine, SessionLocal
from scanner import scan_url

app = FastAPI()

Base.metadata.create_all(bind=engine)

class ScanRequest(BaseModel):
    url: str

class ScanResponse(BaseModel):
    scan_id: str

@app.post("/scan", response_model=ScanResponse)
def start_scan(scan_request: ScanRequest):
    db = SessionLocal()
    try:
        scan_id = str(uuid4())
        new_scan = Scan(id=scan_id, url=scan_request.url, status="pending", created_at=int(time.time()))
        db.add(new_scan)
        db.commit()
        scan_url(scan_id, scan_request.url)
        return {"scan_id": scan_id}
    finally:
        db.close()

@app.get("/scan/{scan_id}")
def get_scan_results(scan_id: str):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        issues = db.query(Issue).filter(Issue.scan_id == scan_id).all()
        return {
            "scan_id": scan_id,
            "status": scan.status,
            "url": scan.url,
            "issues": [i.__dict__ for i in issues]
        }
    finally:
        db.close()
