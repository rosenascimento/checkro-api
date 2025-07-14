import os
import httpx
from bs4 import BeautifulSoup
from models import Scan, Issue
from rules import PROHIBITED_RULES, ALLOWED_RULES
from database import SessionLocal
from dotenv import load_dotenv

load_dotenv()

def scan_site(scan_id: int):
    db = SessionLocal()
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        return

    try:
        response = httpx.get(scan.url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text().lower()

        def check_rules(rules_dict, rule_type):
            for code, rule in rules_dict.items():
                if any(term.lower() in text for term in rule["terms"]):
                    issue = Issue(
                        scan_id=scan.id,
                        rule_code=code,
                        rule_desc=rule["desc"],
                        rule_type=rule_type
                    )
                    db.add(issue)

        check_rules(PROHIBITED_RULES, "prohibited")
        check_rules(ALLOWED_RULES, "allowed")

        scan.status = "completed"
        db.commit()
    except Exception as e:
        scan.status = "error"
        db.commit()
    finally:
        db.close()
