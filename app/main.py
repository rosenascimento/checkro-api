from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery
from dotenv import load_dotenv
from models import Base, Scan, Issue
from tasks import scan_site
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.post("/scan/")
def start_scan(url: str, background_tasks: BackgroundTasks):
    db = SessionLocal()
    scan = Scan(url=url, status="pending")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    db.close()
    background_tasks.add_task(scan_site, scan.id)
    return {"message": "Scan iniciado", "scan_id": scan.id}

@app.get("/scan/{scan_id}")
def get_scan(scan_id: int):
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        db.close()
        return JSONResponse(status_code=404, content={"message": "Scan não encontrado"})
    issues = db.query(Issue).filter(Issue.scan_id == scan_id).all()
    db.close()
    return {
        "scan": scan.url,
        "status": scan.status,
        "issues": [issue.description for issue in issues]
    }
