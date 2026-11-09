from analyst.hybrid import retrieve_bm25

query = (
    "Infosys FY2025 total number of employees "
    "permanent employees as at March 31 2025"
)

hits = retrieve_bm25(
    query,
    k=10,
    company="INFOSYS",
    fy="FY2025",
)

print("\nQ28 TARGETED QUERY RESULTS")

for hit in hits:
    print(
        "Page:", hit["meta"]["page"],
        "| Score:", round(hit["bm25_score"], 4)
    )