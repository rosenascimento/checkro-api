from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from tasks import scan_site
from schemas import ScanRequest

app = FastAPI()

# CORS (permite chamadas de outros domínios, como do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Altere para domínios específicos em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Checkro API online"}

@app.post("/scan")
def scan(scan_request: ScanRequest):
    task = scan_site.delay(scan_request.url)
    return {"task_id": task.id}

# ✅ Rota de verificação para Azure Health Check
@app.get("/health")
def health_check():
    return {"status": "ok"}
