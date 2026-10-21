import time
from src import config
from src.db import get_conn
from src.llm import generate
from src.search import hybrid_search

NO_ANSWER = "I don't know based on the provided documents."


def ask(question, top_k=5):
    start = time.time()
    passages = hybrid_search(question, top_k=top_k)
    answer = generate(question, passages) if passages else NO_ANSWER
    answered = not answer.lower().startswith("i don't know")
    latency = int((time.time() - start) * 1000)
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO query_log (question, provider, retrieved, latency_ms, answered)
               VALUES (%s, %s, %s, %s, %s)""",
            (question, config.LLM_PROVIDER, len(passages), latency, answered),
        )
    sources = []
    if answered:
        sources = [{"document": p["document"], "page": p["page"]} for p in passages]
    return {"answer": answer, "sources": sources, "latency_ms": latency}