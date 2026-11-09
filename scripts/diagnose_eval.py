'''
 import json

from analyst.config import ROOT
from analyst.retrieval import retrieve

K = 10

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

for q in questions:
    if not q["answerable"]:
        continue

    hits = retrieve(
        q["question"],
        k=K,
        company=q.get("company"),
        fy=q.get("fy")
    )

    pages = [h["meta"]["page"] for h in hits]

    if set(q["expected_pages"]) & set(pages):
        continue

    print("=" * 70)
    print(f"Q{q['id']}: {q['question']}")
    print(
        "Expected pages:", q["expected_pages"],
        "| Retrieved pages:", pages
    )

    print(
        "Top hit:",
        hits[0]["text"][:200].replace("\n", " ")
        if hits else "none"
    )
'''

import json
from analyst.config import ROOT
from analyst.retrieval import retrieve

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

for q in questions:
    if q["id"] not in [8, 13, 27]:
        continue

    hits = retrieve(
        q["question"],
        k=3,
        company=q.get("company"),
        fy=q.get("fy")
    )

    print("\n" + "=" * 80)
    print(f"Q{q['id']}: {q['question']}")
    print("Expected pages:", q["expected_pages"])

    for hit in hits:
        print("\nMetadata:", hit["meta"])
        print("Passage:")
        print(hit["text"][:700])