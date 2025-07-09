from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import scan_routes  # se você tiver um router para /scan, por exemplo
from database import setup_database  # se você tiver função de inicialização

app = FastAPI()

# Rota de verificação de integridade para o Azure
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Middleware CORS (opcional, mas recomendado)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar o banco de dados (opcional)
setup_database()

# Incluir outras rotas
app.include_router(scan_routes)

# Execução local (ignorado no Azure, mas útil para testes locais)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
