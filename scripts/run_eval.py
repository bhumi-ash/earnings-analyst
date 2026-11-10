
import csv
import json
import time
from datetime import datetime

from analyst.config import ROOT
from analyst.generation import answer_question
from analyst.hybrid import retrieve_bm25
from analyst.query_rewriting import rewrite_query

K = 10
PAUSE_SECONDS = 4

questions = json.loads(
    (ROOT / "eval" / "questions.json").read_text(encoding="utf-8")
)

rows = []

hits_ok = 0
answerable = 0
refusals_ok = 0
unanswerable = 0
api_errors = 0

for q in questions:
    print(f"\nEvaluating {q['id']}: {q['question']}")

    original_query = q["question"]
    rewritten_query = rewrite_query(original_query)

    hits = retrieve_bm25(
        rewritten_query,
        k=K,
        company=q.get("company"),
        fy=q.get("fy")
    )

    pages = sorted({h["meta"]["page"] for h in hits})

    retrieval_hit = ""
    model_found = ""
    answer = ""
    cited_pages = []
    model_error = ""

    try:
        result = answer_question(original_query, hits)

        model_found = result["found"]
        answer = result["answer"]

        cited_pages = sorted({
            h["meta"]["page"] for h in result["sources"]
        })

    except Exception as exc:
        api_errors += 1
        model_error = str(exc)
        print(f"Model/API error: {exc}")

    if q["answerable"]:
        answerable += 1

        retrieval_hit = bool(
            set(q["expected_pages"]) & set(pages)
        )

        if retrieval_hit:
            hits_ok += 1

    else:
        unanswerable += 1

        if model_error == "" and model_found is False:
            refusals_ok += 1

    rows.append({
        "id": q["id"],
        "question": original_query,
        "rewritten_query": rewritten_query,
        "answerable": q["answerable"],
        "expected_pages": q["expected_pages"],
        "retrieval_hit": retrieval_hit,
        "retrieved_pages": pages,
        "model_found": model_found,
        "answer": answer,
        "expected_answer": q["expected_answer"],
        "cited_pages": cited_pages,
        "model_error": model_error,
        "answer_correct": "",
        "citation_correct": ""
    })

    time.sleep(PAUSE_SECONDS)

out = ROOT / "eval" / f"results_{datetime.now():%Y%m%d_%H%M}.csv"

with out.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n========== EVALUATION SUMMARY ==========")
print(f"Retrieval hit rate @k={K}: {hits_ok}/{answerable}")

if unanswerable:
    print(f"Correct refusals: {refusals_ok}/{unanswerable}")

print(f"Model/API errors: {api_errors}")
print("Results saved to:", out)
print("\nOpen the CSV to manually evaluate:")
print("1. answer_correct: enter 1 or 0")
print("2. citation_correct: enter 1 or 0")
