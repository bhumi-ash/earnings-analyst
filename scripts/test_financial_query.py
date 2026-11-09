
from analyst.hybrid import retrieve_bm25
from analyst.retrieval import retrieve

queries = [
    "What were the consolidated total assets of Infosys in FY2025?",
    "Infosys FY2025 consolidated balance sheet total assets",
    "Total assets as at March 31 2025 consolidated financial statements",
]

for question in queries:
    print("\n" + "=" * 80)
    print("QUERY:", question)

    print("\nBM25:")
    hits = retrieve_bm25(
        question,
        k=10,
        company="INFOSYS",
        fy="FY2025"
    )

    for rank, hit in enumerate(hits, start=1):
        print(f"{rank}. Page {hit['meta']['page']} | {hit['text'][:180]}")

    print("\nVECTOR:")
    hits = retrieve(
        question,
        k=10,
        company="INFOSYS",
        fy="FY2025"
    )

    for rank, hit in enumerate(hits, start=1):
        print(f"{rank}. Page {hit['meta']['page']} | {hit['text'][:180]}")
