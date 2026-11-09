from analyst.hybrid import retrieve_bm25

question = (
    "Infosys total number of employees "
    "permanent employees as at March 31 2025"
)

print("QUESTION:", question)

hits = retrieve_bm25(
    question,
    k=10,
    company="INFOSYS",
    fy="FY2025"
)

for rank, hit in enumerate(hits, start=1):
    print(
        f"\nRank {rank}: Page {hit['meta']['page']}\n"
        f"{hit['text'][:500]}"
    )