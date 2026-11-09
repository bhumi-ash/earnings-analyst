
import csv
import json
import time
from datetime import datetime

from analyst.config import ROOT
from analyst.generation import answer_question
from analyst.retrieval import retrieve

K = 10
PAUSE_SECONDS = 4

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

rows = []
hits_ok = answerable = refusals_ok = unanswerable = 0

for q in questions:
    print(f"\nEvaluating question {q['id']}: {q['question']}")

    hits = retrieve(
        q["question"],
        k=K,
        company=q.get("company"),
        fy=q.get("fy")
    )

    pages = {h["meta"]["page"] for h in hits}
    result = answer_question(q["question"], hits)

    if q["answerable"]:
        answerable += 1
        retrieval_hit = bool(set(q["expected_pages"]) & pages)
        hits_ok += retrieval_hit
    else:
        unanswerable += 1
        retrieval_hit = ""
        refusals_ok += not result["found"]

    rows.append({
        "id": q["id"],
        "question": q["question"],
        "answerable": q["answerable"],
        "retrieval_hit": retrieval_hit,
        "model_found": result["found"],
        "answer": result["answer"],
        "expected_answer": q["expected_answer"],
        "retrieved_pages": sorted(pages),
        "correct": ""
    })

    time.sleep(PAUSE_SECONDS)

out = ROOT / "eval" / f"results_{datetime.now():%Y%m%d_%H%M}.csv"

with out.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n========== EVALUATION SUMMARY ==========")
print(f"Retrieval hit rate @k={K}: {hits_ok}/{answerable}")
print(f"Correct refusals: {refusals_ok}/{unanswerable}")
print("Now open the CSV and fill the 'correct' column with 1 or 0.")
print("Results saved to:", out)
