def rrf(rank_lists, k=60):
    scores = {}
    for ranks in rank_lists:
        for position, chunk_id in enumerate(ranks, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (k + position)
    return sorted(scores, key=scores.get, reverse=True)
