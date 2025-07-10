from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import time

from app.database import SessionLocal
from app.models import Scan
from app.scan import scan_site

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/scan")
async def create_scan(request: Request):
    body = await request.json()
    url = body.get("url")

    if not url:
        return {"error": "URL não fornecida"}

    scan_id = str(uuid.uuid4())
    db = SessionLocal()
    scan = Scan(
        id=scan_id,
        url=url,
        status="pending",
        created_at=int(time.time())
    )
    db.add(scan)
    db.commit()
    db.close()

    scan_site.delay(scan_id, url)

    return {
        "scan_id": scan_id,
        "status": "pending"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
