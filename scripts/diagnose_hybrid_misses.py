
import json

from analyst.config import ROOT
from analyst.retrieval import retrieve
from analyst.hybrid import retrieve_bm25, retrieve_hybrid

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

missed_ids = {8, 9, 16, 17, 28}

for q in questions:
    if q["id"] not in missed_ids:
        continue

    question = q["question"]
    expected_pages = q["expected_pages"]
    company = q.get("company")
    fy = q.get("fy")

    vector_hits = retrieve(
        question,
        k=50,
        company=company,
        fy=fy,
    )

    bm25_hits = retrieve_bm25(
        question,
        k=50,
        company=company,
        fy=fy,
    )

    hybrid_hits = retrieve_hybrid(
        question,
        k=50,
        candidate_k=50,
        company=company,
        fy=fy,
    )

    print("\n" + "=" * 55)
    print("QUESTION:", q["id"])
    print("Expected pages:", expected_pages)

    for name, hits in [
        ("VECTOR", vector_hits),
        ("BM25", bm25_hits),
        ("HYBRID TOP 50", hybrid_hits),
    ]:
        print(f"\n{name}:")

        found = False

        for rank, hit in enumerate(hits, start=1):
            page = hit["meta"]["page"]

            if page in expected_pages:
                print(f"Expected page {page} found at rank {rank}")
                found = True

        if not found:
            print("Expected page NOT FOUND")
