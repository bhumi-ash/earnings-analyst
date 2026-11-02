import sys

from analyst.generation import answer_question
from analyst.retrieval import retrieve

question = sys.argv[1]
company = sys.argv[2] if len(sys.argv) > 2 else None
fy = sys.argv[3] if len(sys.argv) > 3 else None

result = answer_question(
    question,
    retrieve(question, k=6, company=company, fy=fy)
)

print("FOUND:", result["found"])
print(result["answer"])

for s in result["sources"]:
    print(f"- {s['meta']['source']} page {s['meta']['page']}")