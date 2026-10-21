import sys
from pathlib import Path
from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.chunking import read_pdf, make_chunks, content_hash
from src.embeddings import embed
from src.db import get_conn


def ingest_pdf(path, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    path = Path(path)
    config = f"{size}-{overlap}"
    chunks = make_chunks(read_pdf(path), size, overlap)
    with get_conn() as conn:
        doc_id = conn.execute(
            """INSERT INTO documents (title, source_file) VALUES (%s, %s)
               ON CONFLICT (source_file) DO UPDATE SET title = EXCLUDED.title
               RETURNING id""",
            (path.stem, path.name),
        ).fetchone()[0]
        existing = {
            r[0]
            for r in conn.execute(
                "SELECT content_hash FROM chunks WHERE document_id = %s AND chunk_config = %s",
                (doc_id, config),
            ).fetchall()
        }
        new = []
        for c in chunks:
            h = content_hash(c["content"], config)
            if h not in existing:
                new.append((c, h))
        if new:
            vectors = embed([c["content"] for c, _ in new])
            for (c, h), vec in zip(new, vectors):
                conn.execute(
                    """INSERT INTO chunks (document_id, page, content, content_hash, chunk_config, embedding)
                       VALUES (%s, %s, %s, %s, %s, %s)
                       ON CONFLICT (content_hash) DO NOTHING""",
                    (doc_id, c["page"], c["content"], h, config, vec),
                )
    return {"file": path.name, "chunks_new": len(new), "chunks_total": len(chunks)}


def ingest_folder(folder="data", **kwargs):
    return [ingest_pdf(p, **kwargs) for p in sorted(Path(folder).glob("*.pdf"))]


if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else CHUNK_SIZE
    overlap = int(sys.argv[2]) if len(sys.argv) > 2 else CHUNK_OVERLAP
    for result in ingest_folder(size=size, overlap=overlap):
        print(result)
