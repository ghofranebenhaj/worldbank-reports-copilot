import csv
import sys
from src.search import hybrid_search


def evaluate(path="evaluation/questions.csv", config=None, k=5):
    hits, reciprocal, total = 0, 0.0, 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            results = hybrid_search(row["question"], top_k=k, config=config)
            rank = next(
                (
                    i
                    for i, r in enumerate(results, start=1)
                    if r["document"] == row["document"] and r["page"] == int(row["page"])
                ),
                None,
            )
            total += 1
            if rank:
                hits += 1
                reciprocal += 1 / rank
    return {
        "config": config,
        "questions": total,
        f"hit@{k}": round(hits / total, 3) if total else 0,
        "MRR": round(reciprocal / total, 3) if total else 0,
    }


if __name__ == "__main__":
    for cfg in sys.argv[1:] or [None]:
        print(evaluate(config=cfg))
