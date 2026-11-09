
from analyst.retrieval import retrieve
from analyst.reranking import rerank

question = "What is the CEO's favourite food?"

# Retrieve 20 candidates using the existing embedding search
hits = retrieve(
    question,
    k=20,
    company="INFOSYS",
    fy="FY2025"
)

print("\n========== BEFORE RERANKING ==========")

for i, hit in enumerate(hits, start=1):
    print(
        f"\n{i}. Distance: {hit['distance']:.4f} | "
        f"Page: {hit['meta']['page']}"
    )
    print(hit["text"][:300])

# Rerank the retrieved candidates
reranked_hits = rerank(question, hits, top_n=10)

print("\n========== AFTER RERANKING ==========")

for i, hit in enumerate(reranked_hits, start=1):
    print(
        f"\n{i}. Rerank score: {hit['rerank_score']:.4f} | "
        f"Distance: {hit['distance']:.4f} | "
        f"Page: {hit['meta']['page']}"
    )
    print(hit["text"][:300])
