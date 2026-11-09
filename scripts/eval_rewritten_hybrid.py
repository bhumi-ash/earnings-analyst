
import json

from analyst.config import ROOT
from analyst.hybrid import (
    retrieve_bm25,
    retrieve_hybrid,
    retrieve_weighted_hybrid,
)
from analyst.query_rewriting import rewrite_query

K = 10
CANDIDATE_K = 50

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

total = 0

bm25_success = 0
hybrid_success = 0
weighted_success = 0

bm25_misses = []
hybrid_misses = []
weighted_misses = []

for q in questions:
    expected_pages = q.get("expected_pages", [])

    if not expected_pages:
        continue

    total += 1

    original_question = q["question"]

    # Rewrite each question only once.
    rewritten_question = rewrite_query(original_question)

    common_filters = {
        "company": q.get("company"),
        "fy": q.get("fy"),
    }

    # 1. Rewritten BM25
    bm25_hits = retrieve_bm25(
        rewritten_question,
        k=K,
        **common_filters
    )

    bm25_pages = [
        hit["meta"]["page"] for hit in bm25_hits
    ]

    bm25_found = any(
        page in bm25_pages for page in expected_pages
    )

    if bm25_found:
        bm25_success += 1
    else:
        bm25_misses.append(q["id"])

    # 2. Rewritten equal-weight hybrid
    hybrid_hits = retrieve_hybrid(
        rewritten_question,
        k=K,
        candidate_k=CANDIDATE_K,
        **common_filters
    )

    hybrid_pages = [
        hit["meta"]["page"] for hit in hybrid_hits
    ]

    hybrid_found = any(
        page in hybrid_pages for page in expected_pages
    )

    if hybrid_found:
        hybrid_success += 1
    else:
        hybrid_misses.append(q["id"])

    # 3. Rewritten BM25-weighted hybrid
    weighted_hits = retrieve_weighted_hybrid(
        rewritten_question,
        k=K,
        candidate_k=CANDIDATE_K,
        **common_filters
    )

    weighted_pages = [
        hit["meta"]["page"] for hit in weighted_hits
    ]

    weighted_found = any(
        page in weighted_pages for page in expected_pages
    )

    if weighted_found:
        weighted_success += 1
    else:
        weighted_misses.append(q["id"])

    # Display individual results
    print(f"\nQuestion {q['id']}")
    print("Original:", original_question)
    print("Rewritten:", rewritten_question)
    print("Expected pages:", expected_pages)

    print(
        f"BM25: {'HIT' if bm25_found else 'MISS'}",
        "| Pages:", bm25_pages
    )

    print(
        f"Equal Hybrid: {'HIT' if hybrid_found else 'MISS'}",
        "| Pages:", hybrid_pages
    )

    print(
        f"Weighted Hybrid: {'HIT' if weighted_found else 'MISS'}",
        "| Pages:", weighted_pages
    )


# Final comparison
print("\n" + "=" * 60)
print("REWRITTEN RETRIEVAL COMPARISON")
print("=" * 60)

print(f"Total answerable questions: {total}")

print(
    f"Rewritten BM25: {bm25_success}/{total} "
    f"({bm25_success / total * 100:.1f}%)"
)

print(
    f"Equal-weight Hybrid: {hybrid_success}/{total} "
    f"({hybrid_success / total * 100:.1f}%)"
)

print(
    f"BM25-weighted Hybrid: {weighted_success}/{total} "
    f"({weighted_success / total * 100:.1f}%)"
)

print("\nBM25 misses:", bm25_misses)
print("Equal-weight Hybrid misses:", hybrid_misses)
print("Weighted Hybrid misses:", weighted_misses)

print("\n" + "=" * 60)
print("EXPERIMENT COMPLETED")
print("=" * 60)
