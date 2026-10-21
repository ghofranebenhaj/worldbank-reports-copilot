from fastapi import FastAPI
from pydantic import BaseModel
from src.db import get_conn
from src.ingest import ingest_folder
from src.rag import ask

app = FastAPI(title="World Bank Reports Copilot")


class Question(BaseModel):
    question: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest():
    return ingest_folder("data")


@app.post("/ask")
def ask_endpoint(body: Question):
    return ask(body.question, body.top_k)


@app.get("/stats")
def stats():
    with get_conn() as conn:
        row = conn.execute(
            """SELECT count(*), round(avg(latency_ms)),
                      round(100.0 * avg(answered::int), 1)
               FROM query_log"""
        ).fetchone()
    return {"queries": row[0], "avg_latency_ms": row[1], "answered_pct": row[2]}
