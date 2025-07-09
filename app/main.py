from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from banco_de_dados import motor
from modelos import Base
from tarefas import local_de_digitalizacao
from esquemas import SolicitacaoDeDigitalizacao

aplicativo = FastAPI()

aplicativo.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=motor)

@aplicativo.get("/")
def raiz():
    return {"mensagem": "API Checkro online"}

@aplicativo.post("/scan")
def escanear(solicitacao: SolicitacaoDeDigitalizacao):
    tarefa = local_de_digitalizacao.atraso(solicitacao.URL)
    return {"id_da_tarefa": tarefa.id}

@aplicativo.get("/health")
def health():
    return {"message": "Checkro online"}
