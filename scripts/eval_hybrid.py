
import json

from analyst.config import ROOT
from analyst.retrieval import retrieve
from analyst.hybrid import retrieve_bm25, retrieve_hybrid

K = 10

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

total = 0
vector_success = 0
bm25_success = 0
hybrid_success = 0

vector_misses = []
bm25_misses = []
hybrid_misses = []

for q in questions:
    expected_pages = q.get("expected_pages", [])

    if not expected_pages:
        continue

    total += 1

    question = q["question"]
    company = q.get("company")
    fy = q.get("fy")

    # 1. Vector retrieval
    vector_hits = retrieve(
        question,
        k=K,
        company=company,
        fy=fy,
    )

    # 2. BM25 retrieval
    bm25_hits = retrieve_bm25(
        question,
        k=K,
        company=company,
        fy=fy,
    )

    # 3. Hybrid retrieval using RRF
    hybrid_hits = retrieve_hybrid(
        question,
        k=K,
        candidate_k=50,
        company=company,
        fy=fy,
    )

    vector_pages = [
        hit["meta"]["page"] for hit in vector_hits
    ]

    bm25_pages = [
        hit["meta"]["page"] for hit in bm25_hits
    ]

    hybrid_pages = [
        hit["meta"]["page"] for hit in hybrid_hits
    ]

    vector_found = any(
        page in vector_pages for page in expected_pages
    )

    bm25_found = any(
        page in bm25_pages for page in expected_pages
    )

    hybrid_found = any(
        page in hybrid_pages for page in expected_pages
    )

    if vector_found:
        vector_success += 1
    else:
        vector_misses.append(q["id"])

    if bm25_found:
        bm25_success += 1
    else:
        bm25_misses.append(q["id"])

    if hybrid_found:
        hybrid_success += 1
    else:
        hybrid_misses.append(q["id"])

    print(f"\nQuestion {q['id']}")
    print("Expected pages:", expected_pages)
    print("Vector:", "HIT" if vector_found else "MISS")
    print("BM25:", "HIT" if bm25_found else "MISS")
    print("Hybrid:", "HIT" if hybrid_found else "MISS")


print("\n" + "=" * 55)
print("HYBRID RETRIEVAL EVALUATION")
print("=" * 55)

print(f"Total answerable questions: {total}")

print(
    f"Vector: {vector_success}/{total} "
    f"({vector_success / total * 100:.1f}%)"
)

print(
    f"BM25: {bm25_success}/{total} "
    f"({bm25_success / total * 100:.1f}%)"
)

print(
    f"Hybrid: {hybrid_success}/{total} "
    f"({hybrid_success / total * 100:.1f}%)"
)

print("\nVector misses:", vector_misses)
print("BM25 misses:", bm25_misses)
print("Hybrid misses:", hybrid_misses)
