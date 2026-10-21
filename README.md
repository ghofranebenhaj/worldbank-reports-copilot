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

40 hand-written questions over two World Bank reports (*Fiscal Challenges in Small States*, 2024, and *The State of Economic Inclusion Report 2024*). A hit means a correct page is in the top 5 results. Some facts appear on several pages, so a question can accept more than one page.

| Chunk size / overlap | hit@5 | MRR |
|---|---|---|
| 500 / 50 | 0.825 | 0.669 |
| 800 / 100 | 0.875 | 0.651 |
| 1200 / 150 | 0.825 | 0.602 |

800 / 100 found the right page most often, so it is the default. With 40 questions, one question is worth 2.5 points, so the gaps between configurations are small.

**What went wrong:** most misses came from chart pages. Their captions and notes repeat generic words (small states, EMDEs, percent of GDP) and compete with the text pages that contain the answer.

**Speed:** about 12 to 20 seconds per answer with a local llama3.2 model through Ollama, and about 87 seconds on the first call while the model loads.

**Off-topic test:** "What is the best recipe for couscous?" returns "I don't know based on the provided documents." with no sources.

## Run it

```bash
cp .env.example .env
docker compose up --build
```

Put PDFs in `data/`, then open http://localhost:8000/docs and call POST `/ingest`, then POST `/ask`. The Docker image is large because it includes PyTorch.

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

### Reproduce the evaluation

```powershell
python -m src.ingest 500 50
python -m src.ingest 800 100
python -m src.ingest 1200 150
python -m evaluation.evaluate 500-50 800-100 1200-150
python -m evaluation.misses
```

In `evaluation/questions.csv`, the page column holds the page number shown by a PDF reader (first physical page = 1). Use `|` to list several valid pages, for example `19|63`.

## Limitations

- Scanned PDFs and complex tables are not handled well
- Small evaluation set (40 questions over two reports), written by me
- Chart pages hurt retrieval: figure captions and notes can outrank the text that answers the question
- Cited pages are physical PDF pages, which can differ from the printed page numbers (by 2 in the first report)
- Answer quality and speed depend on the LLM you choose
- Not an official World Bank product

## Tech stack

Python, FastAPI, PostgreSQL, pgvector, sentence-transformers, Docker, pytest, GitHub Actions
- Scanned PDFs and complex tables are not handled well
- Small evaluation set (40 questions), written by me
- Answer quality depends on the LLM you choose
- Not an official World Bank product

## Tech stack

Python, FastAPI, PostgreSQL, pgvector, sentence-transformers, Docker, pytest, GitHub Actions
