from celery import Celery
import os

celery_app = Celery(
    "tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)

@celery_app.task
def scan_site(url: str):
    # Aqui entra sua lógica real de análise
    print(f"Escaneando {url} com regras do Google AdSense")
    return {"url": url, "status": "ok"}
