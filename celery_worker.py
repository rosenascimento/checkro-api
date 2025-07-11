from celery import Celery
import os
from dotenv import load_dotenv
from database import SessionLocal
from models import Scan, Issue
from scan import analyze_site  # a lógica de análise deve estar em scan.py

load_dotenv()

celery = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
)

@celery.task
def scan_site(scan_id):
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return

    scan.status = "scanning"
    db.commit()

    issues = analyze_site(scan.url)

    for issue in issues:
        db_issue = Issue(
            scan_id=scan.id,
            code=issue["code"],
            description=issue["description"]
        )
        db.add(db_issue)

    scan.status = "completed"
    db.commit()
