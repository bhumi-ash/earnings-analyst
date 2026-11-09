
import json

from analyst.config import ROOT
from analyst.hybrid import retrieve_bm25
from analyst.query_rewriting import rewrite_query

K = 10

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

total = 0
original_success = 0
rewritten_success = 0
improved = []
still_missed = []

for q in questions:
    expected_pages = q.get("expected_pages", [])

    if not expected_pages:
        continue

    total += 1
    original_question = q["question"]

    # Original BM25 retrieval
    original_hits = retrieve_bm25(
        original_question,
        k=K,
        company=q.get("company"),
        fy=q.get("fy"),
    )

    original_pages = [
        hit["meta"]["page"] for hit in original_hits
    ]

    original_found = any(
        page in original_pages for page in expected_pages
    )

    if original_found:
        original_success += 1

    # Automated query rewriting
    rewritten_question = rewrite_query(original_question)

    # BM25 retrieval using rewritten query
    rewritten_hits = retrieve_bm25(
        rewritten_question,
        k=K,
        company=q.get("company"),
        fy=q.get("fy"),
    )

    rewritten_pages = [
        hit["meta"]["page"] for hit in rewritten_hits
    ]

    rewritten_found = any(
        page in rewritten_pages for page in expected_pages
    )

    if rewritten_found:
        rewritten_success += 1

    if rewritten_found and not original_found:
        improved.append(q["id"])

    if not rewritten_found:
        still_missed.append(q["id"])

    print(f"\n{q['id']}")
    print("Original:", original_question)
    print("Rewritten:", rewritten_question)
    print("Original BM25:", "HIT" if original_found else "MISS")
    print("Rewritten BM25:", "HIT" if rewritten_found else "MISS")
    print("Expected pages:", expected_pages)
    print("Retrieved pages:", rewritten_pages)

print("\n" + "=" * 55)
print("AUTOMATED QUERY REWRITING EVALUATION")
print("=" * 55)

print(f"Total answerable questions: {total}")
print(
    f"Original BM25: {original_success}/{total} "
    f"({original_success / total * 100:.1f}%)"
)
print(
    f"Rewritten BM25: {rewritten_success}/{total} "
    f"({rewritten_success / total * 100:.1f}%)"
)
print(f"Questions improved: {improved}")
print(f"Questions still missed: {still_missed}")

# Q16 targeted query test
query = (
 
    "Infosys FY2025 Financial Services Manufacturing "
    "Retail Energy Utilities Communication revenue "
    "business segments"
)

hits = retrieve_bm25(
    query,
    k=10,
    company="INFOSYS",
    fy="FY2025",
)

print("\nQ16 TARGETED QUERY RESULTS")
for hit in hits:
    print(
        "Page:", hit["meta"]["page"],
        "| Score:", round(hit["bm25_score"], 4)
    )