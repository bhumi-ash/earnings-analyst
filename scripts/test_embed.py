
from analyst.embeddings import embed_passages, embed_query


docs = [
    "Revenue grew 6% year on year.",
    "The cat sat on the mat.",
]

vecs = embed_passages(docs)
q = embed_query("How much did sales increase?")

print("Number of document vectors:", len(vecs))
print("Document embedding dimensions:", len(vecs[0]))
print("Query embedding dimensions:", len(q))
print("First 10 numbers:", vecs[0][:10])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


print(
    "revenue sentence score:",
    round(dot(q, vecs[0]), 3),
)
print(
    "cat sentence score:",
    round(dot(q, vecs[1]), 3),
)
