
import json

from analyst.config import ROOT
from analyst.hybrid import retrieve_bm25

K = 10

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

total_answerable = 0
successful = 0
misses = []

for q in questions:

    expected_pages = q.get("expected_pages", [])

    # Skip unanswerable questions
    if not expected_pages:
        continue

    total_answerable += 1

    hits = retrieve_bm25(
        q["question"],
        k=K,
        company=q.get("company"),
        fy=q.get("fy")
    )

    retrieved_pages = [
        hit["meta"]["page"] for hit in hits
    ]

    found = any(
        page in retrieved_pages for page in expected_pages
    )

    if found:
        successful += 1
    else:
        misses.append({
            "id": q["id"],
            "question": q["question"],
            "expected_pages": expected_pages,
            "retrieved_pages": retrieved_pages
        })

    print(
        f"Q{q['id']} | "
        f"{'HIT' if found else 'MISS'} | "
        f"Expected: {expected_pages} | "
        f"Retrieved: {retrieved_pages}"
    )

print("\n" + "=" * 60)
print("BM25 EVALUATION RESULTS")
print("=" * 60)

print(f"Total answerable questions: {total_answerable}")
print(f"Successful retrievals: {successful}")
print(f"Missed questions: {len(misses)}")

if total_answerable:
    hit_rate = successful / total_answerable * 100
    print(f"Retrieval hit rate: {hit_rate:.1f}%")

print("\nMISSED QUESTIONS:")

for miss in misses:
    print(f"\nQ{miss['id']}: {miss['question']}")
    print("Expected:", miss["expected_pages"])
    print("Retrieved:", miss["retrieved_pages"])
