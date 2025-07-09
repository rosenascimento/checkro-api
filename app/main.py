from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from tasks import scan_site
from schemas import ScanRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API Checkro online"}

@app.post("/scan")
def scan(scan_request: ScanRequest):
    task = scan_site.delay(scan_request.url)
    return {"task_id": task.id}

@app.get("/health")
def health_check():
    return {"status": "ok"}
