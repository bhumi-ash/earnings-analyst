
from sentence_transformers import CrossEncoder

# Load the reranking model only once
_model = None

def get_reranker():
    global _model

    if _model is None:
        _model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    return _model


def rerank(question, hits, top_n=10):
    """
    Reorder retrieved chunks using a cross-encoder.

    Args:
        question: User's question.
        hits: List of retrieved chunks.
        top_n: Number of highest-ranked chunks to return.

    Returns:
        Reranked list of chunks.
    """
    if not hits:
        return []

    model = get_reranker()

    pairs = [
        (question, hit["text"])
        for hit in hits
    ]

    scores = model.predict(pairs)

    ranked_hits = []

    for hit, score in zip(hits, scores):
        updated_hit = hit.copy()
        updated_hit["rerank_score"] = float(score)
        ranked_hits.append(updated_hit)

    ranked_hits.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return ranked_hits[:top_n]
