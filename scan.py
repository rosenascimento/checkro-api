from celery import Celery
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import validators
import time
import re
from urllib.parse import urljoin, urlparse

load_dotenv()

# Database setup with PostgreSQL from Render
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models (mantidas da sua API original)
class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True)
    url = Column(String)
    status = Column(String)
    created_at = Column(Integer)

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    page_url = Column(String)
    rule_code = Column(String)
    description = Column(Text)
    term_detected = Column(Text, nullable=True)
    suggestion = Column(Text)

Base.metadata.create_all(bind=engine)

# Rule definitions (mantidas da sua API original, com ajuste em Pδ-34)
PROHIBITED_RULES = {
    "P-01": {"desc": "Conteúdo adulto ou pornográfico", "terms": ["adulto", "pornô", "xxx"]},
    "P-02": {"desc": "Conteúdo violento ou chocante", "terms": ["violência", "sangue", "gore"]},
    "P-03": {"desc": "Discurso de ódio, discriminação ou assédio", "terms": ["ódio", "racismo", "discriminação"]},
    "P-04": {"desc": "Atividades ilegais", "terms": ["ilegal", "criminoso"]},
    "P-05": {"desc": "Drogas e substâncias proibidas", "terms": ["droga", "maconha", "cocaína"]},
    "P-06": {"desc": "Bebidas alcoólicas e tabaco", "terms": ["álcool", "cerveja", "tabaco"]},
    "P-07": {"desc": "Armas, munições e explosivos", "terms": ["arma", "pistola", "explosivo"]},
    "P-08": {"desc": "Conteúdo enganoso ou sensacionalista", "terms": ["milagre", "cura instantânea"]},
    "P-09": {"desc": "Fraudes e esquemas de dinheiro fácil", "terms": ["dinheiro fácil", "enriquecer rápido"]},
    "P-10": {"desc": "Clickbait excessivo", "terms": ["você não vai acreditar", "choquei"]},
    "P-11": {"desc": "Downloads ilegais", "terms": ["torrent", "download grátis"]},
    "P-12": {"desc": "Conteúdo com direitos autorais", "terms": ["copyright", "protegido por direitos"]},
    "P-13": {"desc": "Manipulação de tráfego e cliques", "terms": ["cliques automáticos", "bot de tráfego"]},
    "P-14": {"desc": "Conteúdo insuficiente ou de baixa qualidade", "terms": []},
    "P-15": {"desc": "Excesso de anúncios e pop-ups", "terms": ["popup", "anúncio intrusivo"]},
    "P-16": {"desc": "Erros graves de navegação", "terms": []},
    "P-17": {"desc": "Hacking, cracking ou invasão de sistemas", "terms": ["hack", "crack", "invasão"]},
    "P-18": {"desc": "Fake news e desinformação", "terms": ["notícia falsa", "desinformação"]},
    "P-19": {"desc": "Programas de afiliados sem valor agregado", "terms": ["afiliado", "sem valor"]},
    "P-20": {"desc": "Conteúdo automatizado de baixa qualidade", "terms": ["gerado automaticamente", "ia não revisada"]},
    "P-21": {"desc": "Conteúdo médico duvidoso", "terms": ["cura milagrosa", "tratamento não comprovado"]},
    "P-22": {"desc": "Sites copiados ou sem identidade própria", "terms": ["cópia", "plágio"]},
    "P-23": {"desc": "Conteúdo político ou eleitoral enganoso", "terms": ["propaganda enganosa", "fake eleitoral"]},
    "P-24": {"desc": "Idioma não suportado pelo AdSense", "terms": []},
    "P-25": {"desc": "Redirecionamentos enganosos", "terms": ["redirecionamento suspeito"]},
    "P-26": {"desc": "Propagação de malware, vírus ou phishing", "terms": ["malware", "phishing"]},
    "P-27": {"desc": "Venda de dados pessoais", "terms": ["vender dados", "dados pessoais"]},
    "P-28": {"desc": "Conteúdo relacionado a apostas e cassinos online", "terms": ["cassino", "aposta online"]},
    "P-29": {"desc": "Sites que promovem ódio contra indivíduos ou grupos", "terms": ["ataque pessoal", "preconceito"]},
    "P-30": {"desc": "Uso de técnicas de SEO Black Hat", "terms": ["black hat", "spam seo"]},
    "P-31": {"desc": "Conteúdo com incentivo a comportamentos prejudiciais", "terms": ["comportamento perigoso", "autolesão"]},
    "P-32": {"desc": "Falsificação de identidade ou informações", "terms": ["falsificação", "identidade falsa"]},
    "P-33": {"desc": "Venda ou distribuição de contas do Google AdSense", "terms": ["venda adsense", "conta adsense"]},
    "P-34": {"desc": "Criptomoedas ou investimentos de alto risco sem informações confiáveis", "terms": ["criptomoeda", "investimento arriscado"]},
    "P-35": {"desc": "Sites apenas para redirecionamento", "terms": ["redirecionamento puro"]},
}

ALLOWED_RULES = {
    "A-01": {"desc": "Conteúdo original e educativo", "terms": ["guia", "tutorial", "educação"]},
    "A-02": {"desc": "Revisão e análises honestas", "terms": ["análise", "revisão", "opinião"]},
    "A-03": {"desc": "Notícias relevantes e atualizadas", "terms": ["notícia", "atualidade"]},
    "A-04": {"desc": "Artigos com boa estrutura e profundidade", "terms": ["artigo detalhado", "profundidade"]},
    "A-05": {"desc": "Uso correto de títulos H1, H2, meta descrição", "terms": []},
    "A-06": {"desc": "Imagens com texto alternativo (ALT)", "terms": []},
    "A-07": {"desc": "Páginas institucionais (Sobre, Contato, Privacidade)", "terms": []},
    "A-08": {"desc": "Escrita clara e sem erros", "terms": []},
    "A-09": {"desc": "Design responsivo e boa experiência móvel", "terms": []},
    "A-10": {"desc": "Conteúdo atualizado regularmente", "terms": []},
}

# Configuração do Celery
celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL")
)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
