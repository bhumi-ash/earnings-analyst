
import json

from analyst.config import ROOT
from analyst.hybrid import retrieve_hybrid

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

for q in questions:
    if q["id"] not in [8, 27]:
        continue

    
    query = q["question"]

    if q["id"] == 8:
        query = "Infosys FY2025 consolidated balance sheet total assets"

    hits = retrieve_hybrid(
      query,    
          k=10,
          candidate_k=50,
        company=q.get("company"),
          fy=q.get("fy")
    )

    print("\n" + "=" * 80)
    print(f"Q{q['id']}: {q['question']}")
    print("Expected pages:", q["expected_pages"])
    print("\n--- HYBRID SEARCH (RRF) ---")

    for rank, hit in enumerate(hits, start=1):
        print(
            f"Rank {rank} | Page {hit['meta']['page']} | "
            f"RRF score: {hit['rrf_score']:.5f}"
        )
        print(hit["text"][:350].replace("\n", " "))
        print("-" * 40)
