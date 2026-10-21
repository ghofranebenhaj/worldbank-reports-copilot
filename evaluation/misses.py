import csv
import sys
from src.search import hybrid_search

config = sys.argv[1] if len(sys.argv) > 1 else "800-100"

with open("evaluation/questions.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        valid = {int(p) for p in row["page"].split("|")}
        results = hybrid_search(row["question"], top_k=5, config=config)
        pages = [(r["document"], r["page"]) for r in results]
        if not any(d == row["document"] and p in valid for d, p in pages):
            print("MISS:", row["question"])
            print("  expected:", row["document"], sorted(valid))
            print("  got:", pages)