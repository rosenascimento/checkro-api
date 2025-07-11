from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from app.database import SessionLocal
from app.models import Scan
from scan import scan_site  # importa a task Celery

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# Modelo da requisição
class ScanRequest(BaseModel):
    url: str

# Endpoint /scan que seu frontend precisa
@app.post("/scan")
async def create_scan(request: ScanRequest):
    db = SessionLocal()
    try:
        # Cria um novo scan no banco
        scan = Scan(url=request.url, status="queued")
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Dispara a task Celery
        scan_site.delay(scan.id, scan.url)

        return {
            "scan_id": scan.id,
            "status": scan.status
        }
    finally:
        db.close()

# Rodar com uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
