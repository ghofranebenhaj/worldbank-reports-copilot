from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _model():
    return SentenceTransformer(EMBEDDING_MODEL)


def embed(texts):
    return _model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
