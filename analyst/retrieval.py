
from analyst.embeddings import embed_query
from analyst.store import get_collection


def _where(company=None, fy=None, doc_type=None):
    """Build a Chroma metadata filter. Several conditions need $and."""
    conditions = []

    if company:
        conditions.append({"company": company.upper()})

    if fy:
        conditions.append({"fy": fy.upper()})

    if doc_type:
        conditions.append({"doc_type": doc_type.lower()})

    if not conditions:
        return None

    return conditions[0] if len(conditions) == 1 else {"$and": conditions}


def retrieve(question, k=6, company=None, fy=None, doc_type=None):
    """Return the k most similar chunks as a list of dicts (best first)."""
    result = get_collection().query(
        query_embeddings=[embed_query(question)],
        n_results=k,
        where=_where(company, fy, doc_type),
    )

    hits = []

    for i in range(len(result["ids"][0])):
        hits.append(
            {
                "id": result["ids"][0][i],
                "text": result["documents"][0][i],
                "meta": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
            }
        )

    return hits
def retrieve_multi(question, company, fy, doc_types, k_each=4):
    """Retrieve separately per document type so each type is represented."""
    hits = []

    for doc_type in doc_types:
        hits += retrieve(
            question,
            k=k_each,
            company=company,
            fy=fy,
            doc_type=doc_type
        )

    return hits
