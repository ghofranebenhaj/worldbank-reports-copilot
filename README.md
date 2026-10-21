# World Bank Reports Copilot

Ask questions about World Bank reports and get answers with citations (document and page), or an honest "I don't know".

## Architecture

![Architecture](docs/architecture.png)

PDFs -> ingestion pipeline (clean, chunk, hash, embed) -> PostgreSQL + pgvector -> hybrid search (vectors + full-text, RRF) -> LLM -> FastAPI

## Key design choices

- **Idempotent ingestion**: each chunk has a content hash; re-running creates no duplicates
- **Hybrid search**: vector similarity and PostgreSQL full-text search, merged with Reciprocal Rank Fusion
- **Grounded answers**: the model answers only from retrieved passages and cites its sources
- **Evaluation**: hit@5 and MRR on 40 hand-written questions
- **Observability**: every query is logged (latency, answered or not), exposed at `/stats`

## Evaluation results

| Chunk size / overlap | hit@5 | MRR |
|---|---|---|
| 500 / 50 | [ ] | [ ] |
| 800 / 100 | [ ] | [ ] |
| 1200 / 150 | [ ] | [ ] |

Average latency: [ ] ms. Off-topic questions answered "I don't know": [ ] out of [ ].

## Run it

```bash
cp .env.example .env
docker compose up --build
```

Put PDFs in `data/`, then open http://localhost:8000/docs and call POST `/ingest`, then POST `/ask`.

### Local development (without Docker API)

```powershell
docker compose up -d db
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m src.ingest
uvicorn src.api:app --reload
```

## Limitations

- Scanned PDFs and complex tables are not handled well
- Small evaluation set (40 questions), written by me
- Answer quality depends on the LLM you choose
- Not an official World Bank product

## Tech stack

Python, FastAPI, PostgreSQL, pgvector, sentence-transformers, Docker, pytest, GitHub Actions
