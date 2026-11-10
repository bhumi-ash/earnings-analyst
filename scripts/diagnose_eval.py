
import json

from analyst.config import ROOT
from analyst.hybrid import retrieve_bm25
from analyst.query_rewriting import rewrite_query

K = 10

questions = json.loads(
    (ROOT / "eval" / "heldout_questions.json").read_text(
        encoding="utf-8"
    )
)

miss_count = 0
answerable_count = 0

for q in questions:
    if not q["answerable"]:
        continue

    answerable_count += 1

    original_query = q["question"]
    rewritten_query = rewrite_query(original_query)

    hits = retrieve_bm25(
        rewritten_query,
        k=K,
        company=q.get("company"),
        fy=q.get("fy")
    )

    retrieved_pages = [h["meta"]["page"] for h in hits]
    expected_pages = q["expected_pages"]

    if set(expected_pages) & set(retrieved_pages):
        continue

    miss_count += 1

    print("\n" + "=" * 80)
    print(f"QUESTION ID: {q['id']}")
    print(f"Question: {original_query}")
    print(f"Rewritten query: {rewritten_query}")
    print(f"Expected pages: {expected_pages}")
    print(f"Retrieved pages: {retrieved_pages}")

    for rank, hit in enumerate(hits[:3], start=1):
        print(f"\n--- Rank {rank} | Page {hit['meta']['page']} ---")
        print(hit["text"][:600].replace("\n", " "))

print("\n" + "=" * 80)
print("DIAGNOSTIC SUMMARY")
print(f"Answerable questions: {answerable_count}")
print(f"Retrieval misses: {miss_count}")
print(
    f"Retrieval hits: {answerable_count - miss_count}"
)
