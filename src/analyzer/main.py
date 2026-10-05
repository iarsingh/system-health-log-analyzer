from analyzer.ops import router as ops_router
from fastapi import FastAPI, HTTPException
from analyzer.detect import InputError, alerts, ingest
app = FastAPI(title="System Health & Log Analyzer")
app.include_router(ops_router, prefix="/v1")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/ingest")
def post_ingest(body: dict):
    try:
        return ingest(body.get("snapshot") or {}, body.get("logs") or [])
    except InputError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@app.get("/alerts")
def get_alerts():
    return alerts()
