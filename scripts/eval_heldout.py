
import json
import csv

from analyst.config import ROOT
from analyst.retrieval import retrieve
from analyst.hybrid import retrieve_bm25, retrieve_hybrid
from analyst.query_rewriting import rewrite_query


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

K = 10
CANDIDATE_K = 50

DATASET_PATH = ROOT / "eval" / "heldout_questions.json"
OUTPUT_PATH = ROOT / "eval" / "heldout_results.csv"


# --------------------------------------------------
# LOAD DATASET
# --------------------------------------------------

with open(DATASET_PATH, "r", encoding="utf-8") as file:
    questions = json.load(file)


pipelines = [
    "Vector",
    "BM25",
    "Rewritten BM25",
    "Rewritten Hybrid"
]

results = {name: [] for name in pipelines}

answerable_total = 0
unanswerable_total = 0


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def get_pages(hits):
    return [
        int(hit["meta"]["page"])
        for hit in hits
    ]


def evaluate_answerable(hits, expected_pages):
    retrieved_pages = get_pages(hits)

    hit = any(
        page in retrieved_pages
        for page in expected_pages
    )

    return hit, retrieved_pages


# --------------------------------------------------
# RUN EVALUATION
# --------------------------------------------------

print("=" * 65)
print("HELD-OUT RETRIEVAL BENCHMARK")
print("=" * 65)

for q in questions:

    qid = q["id"]
    question = q["question"]

    company = q.get("company")
    fy = q.get("fy")
    

    expected_pages = q.get("expected_pages", [])
    is_answerable = q["answerable"]

    if is_answerable:
        answerable_total += 1
    else:
        unanswerable_total += 1

    print(f"\n{'-' * 65}")
    print(f"{qid}: {question}")

    # Rewrite ONCE. The same rewritten query is
    # used by both rewritten retrieval pipelines.
    rewritten_question = rewrite_query(question)

    print("Rewritten query:", rewritten_question)

    # --------------------------------------------------
    # 1. VECTOR
    # --------------------------------------------------

    vector_hits = retrieve(
        question,
        k=K,
        company=company,
        fy=fy,
        
    )

    # --------------------------------------------------
    # 2. BM25
    # --------------------------------------------------

    bm25_hits = retrieve_bm25(
        question,
        k=K,
        company=company,
        fy=fy,
        
    )

    # --------------------------------------------------
    # 3. REWRITTEN BM25
    # --------------------------------------------------

    rewritten_bm25_hits = retrieve_bm25(
        rewritten_question,
        k=K,
        company=company,
        fy=fy,
       
    )

    # --------------------------------------------------
    # 4. REWRITTEN HYBRID
    # --------------------------------------------------

    rewritten_hybrid_hits = retrieve_hybrid(
        rewritten_question,
        k=K,
        candidate_k=CANDIDATE_K,
        company=company,
        fy=fy,
       
    )

    all_hits = {
        "Vector": vector_hits,
        "BM25": bm25_hits,
        "Rewritten BM25": rewritten_bm25_hits,
        "Rewritten Hybrid": rewritten_hybrid_hits
    }

    # --------------------------------------------------
    # EVALUATE EACH PIPELINE
    # --------------------------------------------------

    for pipeline, hits in all_hits.items():

        pages = get_pages(hits)

        if is_answerable:
            success, _ = evaluate_answerable(
                hits,
                expected_pages
            )

            results[pipeline].append({
                "id": qid,
                "answerable": True,
                "success": success,
                "pages": pages
            })

        else:
            # This is a retrieval-only test.
            # No retrieved passages means retrieval
            # did not supply evidence to the generator.
            success = len(hits) == 0

            results[pipeline].append({
                "id": qid,
                "answerable": False,
                "success": success,
                "pages": pages
            })

        status = (
            "HIT" if success else "MISS"
        )

        print(
            f"{pipeline:20} | {status:4} | Pages: {pages}"
        )


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

print("\n" + "=" * 65)
print("ANSWERABLE QUESTION RESULTS")
print("=" * 65)

for pipeline in pipelines:

    pipeline_results = [
        r for r in results[pipeline]
        if r["answerable"]
    ]

    hits = sum(
        r["success"] for r in pipeline_results
    )

    misses = [
        r["id"]
        for r in pipeline_results
        if not r["success"]
    ]

    accuracy = (
        hits / answerable_total * 100
        if answerable_total else 0
    )

    print(
        f"{pipeline:20}: "
        f"{hits}/{answerable_total} "
        f"({accuracy:.1f}%)"
    )

    print("Misses:", misses)


# --------------------------------------------------
# UNANSWERABLE QUESTION RESULTS
# --------------------------------------------------

print("\n" + "=" * 65)
print("UNANSWERABLE QUESTION RESULTS")
print("=" * 65)

for pipeline in pipelines:

    pipeline_results = [
        r for r in results[pipeline]
        if not r["answerable"]
    ]

    empty_results = sum(
        r["success"] for r in pipeline_results
    )

    print(
        f"{pipeline:20}: "
        f"{empty_results}/{unanswerable_total} "
        "returned no passages"
    )


# --------------------------------------------------
# SAVE RESULTS TO CSV
# --------------------------------------------------

with open(
    OUTPUT_PATH,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "Question ID",
        "Pipeline",
        "Answerable",
        "Expected Page Hit",
        "Retrieved Pages"
    ])

    for pipeline in pipelines:
        for result in results[pipeline]:

            writer.writerow([
                result["id"],
                pipeline,
                result["answerable"],
                result["success"],
                ", ".join(
                    map(str, result["pages"])
                )
            ])


print("\n" + "=" * 65)
print("EVALUATION COMPLETED")
print(f"Results saved to: {OUTPUT_PATH}")
print("=" * 65)
