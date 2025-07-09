from fastapi import FastAPI
from app.tasks import scan_site
from app.models import ScanRequest

app = FastAPI()

@app.post("/scan")
async def scan(request: ScanRequest):
    task = scan_site.delay(request.url)
    return {"task_id": task.id}
