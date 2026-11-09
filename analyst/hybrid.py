
from rank_bm25 import BM25Okapi

from analyst.retrieval import retrieve
from analyst.store import get_collection


def _tokenize(text):
    """Convert text into lowercase tokens."""
    return text.lower().split()


def _get_filtered_documents(company=None, fy=None, doc_type=None):
    """Fetch documents from ChromaDB using optional metadata filters."""

    conditions = []

    if company:
        conditions.append({"company": company.upper()})

    if fy:
        conditions.append({"fy": fy.upper()})

    if doc_type:
        conditions.append({"doc_type": doc_type.lower()})

    where = None

    if conditions:
        where = conditions[0] if len(conditions) == 1 else {"$and": conditions}

    collection = get_collection()

    result = collection.get(
        where=where,
        include=["documents", "metadatas"]
    )

    documents = []

    for i, text in enumerate(result["documents"]):
        documents.append({
            "id": result["ids"][i],
            "text": text,
            "meta": result["metadatas"][i]
        })

    return documents


def retrieve_bm25(question, k=10, company=None, fy=None, doc_type=None):
    """Retrieve the top k documents using BM25 keyword search."""

    documents = _get_filtered_documents(company, fy, doc_type)

    if not documents:
        return []

    tokenized_corpus = [
        _tokenize(doc["text"]) for doc in documents
    ]

    bm25 = BM25Okapi(tokenized_corpus)

    query_tokens = _tokenize(question)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    hits = []

    for i in ranked_indices[:k]:
        hit = documents[i].copy()
        hit["bm25_score"] = float(scores[i])
        hits.append(hit)

    return hits

def retrieve_hybrid(
    question,
    k=10,
    candidate_k=50,
    company=None,
    fy=None,
    doc_type=None,
    rrf_constant=60
):
    """Combine vector and BM25 rankings using Reciprocal Rank Fusion."""

    vector_hits = retrieve(
        question,
        k=candidate_k,
        company=company,
        fy=fy,
        doc_type=doc_type
    )

    bm25_hits = retrieve_bm25(
        question,
        k=candidate_k,
        company=company,
        fy=fy,
        doc_type=doc_type
    )

    fused = {}

    # Add vector search rankings
    for rank, hit in enumerate(vector_hits, start=1):
        doc_id = hit["id"]

        if doc_id not in fused:
            fused[doc_id] = {
                **hit,
                "rrf_score": 0.0
            }

        fused[doc_id]["rrf_score"] += (
            1 / (rrf_constant + rank)
        )

    # Add BM25 rankings
    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit["id"]

        if doc_id not in fused:
            fused[doc_id] = {
                **hit,
                "rrf_score": 0.0
            }

        fused[doc_id]["rrf_score"] += (
            1 / (rrf_constant + rank)
        )

    ranked_hits = sorted(
        fused.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )

    return ranked_hits[:k]
