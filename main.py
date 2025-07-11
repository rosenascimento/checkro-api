from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# CORS CONFIG
origins = [
    "https://checkro.com",  # Permite frontend oficial
    "http://localhost:3000",  # Permite desenvolvimento local (opcional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}
from fastapi import Request
from pydantic import BaseModel
import uuid
import time
from scan_site import scan_site, SessionLocal, Scan

class ScanRequest(BaseModel):
    url: str

@app.post("/scan")
def create_scan(scan_request: ScanRequest):
    scan_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db_scan = Scan(
            id=scan_id,
            url=scan_request.url,
            status="pending",
            created_at=int(time.time())
        )
        db.add(db_scan)
        db.commit()
    finally:
        db.close()

    scan_site.delay(scan_id, scan_request.url)

    return {"scan_id": scan_id, "status": "queued"}
