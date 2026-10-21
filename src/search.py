import re
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.db import get_conn
from src.embeddings import embed
from src.fusion import rrf


def hybrid_search(question, top_k=5, config=None, pool=20):
    config = config or f"{CHUNK_SIZE}-{CHUNK_OVERLAP}"
    qvec = embed([question])[0]
    words = re.findall(r"\w+", question)
    text_query = " or ".join(words)
    with get_conn() as conn:
        vec_ids = [
            r[0]
            for r in conn.execute(
                "SELECT id FROM chunks WHERE chunk_config = %s ORDER BY embedding <=> %s LIMIT %s",
                (config, qvec, pool),
            ).fetchall()
        ]
        txt_ids = []
        if words:
            txt_ids = [
                r[0]
                for r in conn.execute(
                    """SELECT id FROM chunks
                   WHERE chunk_config = %s AND tsv @@ websearch_to_tsquery('english', %s)
                   ORDER BY ts_rank_cd(tsv, websearch_to_tsquery('english', %s)) DESC
                   LIMIT %s""",
                    (config, text_query, text_query, pool),
                ).fetchall()
            ]
        best = rrf([vec_ids, txt_ids])[:top_k]
        if not best:
            return []
        rows = conn.execute(
            """SELECT c.id, d.title, c.page, c.content
               FROM chunks c JOIN documents d ON d.id = c.document_id
               WHERE c.id = ANY(%s)""",
            (best,),
        ).fetchall()
    by_id = {
        r[0]: {"id": r[0], "document": r[1], "page": r[2], "content": r[3]} for r in rows
    }
    return [by_id[i] for i in best]
