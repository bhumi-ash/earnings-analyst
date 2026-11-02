
import sys

from analyst.retrieval import retrieve

question = sys.argv[1]
company = sys.argv[2] if len(sys.argv) > 2 else None
fy = sys.argv[3] if len(sys.argv) > 3 else None

for hit in retrieve(question, k=6, company=company, fy=fy):
    m = hit["meta"]
    print(f"{hit['distance']:.3f} {m['source']} page {m['page']}")
    print(" ", hit["text"][:200].replace("\n", " "))
