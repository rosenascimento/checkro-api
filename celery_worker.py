from celery import Celery
import os
from dotenv import load_dotenv
from database import SessionLocal, Scan, Issue
from scan import scan_site, crawl_site, analyze_page, IssueResponse

load_dotenv()

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

@celery_app.task
def scan_site(scan_id: str, url: str):
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan and scan.status == "pending":
            pages = crawl_site(url)
            issues = []
            for page in pages:
                page_issues = analyze_page(page)
                for issue in page_issues:
                    db_issue = Issue(
                        scan_id=scan_id,
                        page_url=page,
                        rule_code=issue["rule_code"],
                        description=issue["desc"],
                        term_detected=issue["term"],
                        suggestion=issue["suggestion"]
                    )
                    db.add(db_issue)
                    issues.append(IssueResponse(
                        id=db_issue.id,
                        page_url=page,
                        rule_code=issue["rule_code"],
                        description=issue["desc"],
                        term_detected=issue["term"],
                        suggestion=issue["suggestion"]
                    ))
            db.commit()
            scan.status = "completed"
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    celery_app.start()
