
from functools import lru_cache

from fastembed import TextEmbedding

from analyst.config import EMBED_MODEL


@lru_cache(maxsize=1)
def _model():
    """Load the embedding model once and reuse it."""
    return TextEmbedding(model_name=EMBED_MODEL)


def embed_passages(texts):
    """Embed document chunks. Returns a list of lists of floats."""
    return [vec.tolist() for vec in _model().passage_embed(list(texts))]


def embed_query(question):
    """Embed a question. Some models treat queries differently from passages."""
    return next(iter(_model().query_embed(question))).tolist()
