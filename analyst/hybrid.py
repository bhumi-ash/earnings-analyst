
from rank_bm25 import BM25Okapi

from analyst.retrieval import retrieve
from analyst.store import get_collection
import re


def _tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def _get_filtered_documents(company=None, fy=None, doc_type=None):
    conditions = []

    if company:
        conditions.append({"company": company.upper()})

    if fy:
        conditions.append({"fy": fy.upper()})

    if doc_type:
        conditions.append({"doc_type": doc_type.lower()})

    where = None

    if conditions:
        where = (
            conditions[0]
            if len(conditions) == 1
            else {"$and": conditions}
        )

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


def retrieve_bm25(
    question,
    k=10,
    company=None,
    fy=None,
    doc_type=None
):
    documents = _get_filtered_documents(
        company=company,
        fy=fy,
        doc_type=doc_type
    )

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


def _retrieve_rrf(
    question,
    k=10,
    candidate_k=50,
    company=None,
    fy=None,
    doc_type=None,
    rrf_constant=60,
    bm25_weight=1,
    vector_weight=1
):
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

    # Add BM25 rankings
    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit["id"]

        if doc_id not in fused:
            fused[doc_id] = {
                **hit,
                "rrf_score": 0.0
            }

        fused[doc_id]["rrf_score"] += (
            bm25_weight / (rrf_constant + rank)
        )

    # Add vector rankings
    for rank, hit in enumerate(vector_hits, start=1):
        doc_id = hit["id"]

        if doc_id not in fused:
            fused[doc_id] = {
                **hit,
                "rrf_score": 0.0
            }

        fused[doc_id]["rrf_score"] += (
            vector_weight / (rrf_constant + rank)
        )

    ranked_hits = sorted(
        fused.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )

    return ranked_hits[:k]


def retrieve_hybrid(
    question,
    k=10,
    candidate_k=50,
    company=None,
    fy=None,
    doc_type=None,
    rrf_constant=60
):
    """Equal-weight BM25 + vector RRF."""

    return _retrieve_rrf(
        question=question,
        k=k,
        candidate_k=candidate_k,
        company=company,
        fy=fy,
        doc_type=doc_type,
        rrf_constant=rrf_constant,
        bm25_weight=1,
        vector_weight=1
    )


def retrieve_weighted_hybrid(
    question,
    k=10,
    candidate_k=50,
    company=None,
    fy=None,
    doc_type=None,
    rrf_constant=60
):
    """BM25-weighted RRF: BM25 weight 2, vector weight 1."""

    return _retrieve_rrf(
        question=question,
        k=k,
        candidate_k=candidate_k,
        company=company,
        fy=fy,
        doc_type=doc_type,
        rrf_constant=rrf_constant,
        bm25_weight=2,
        vector_weight=1
    )
