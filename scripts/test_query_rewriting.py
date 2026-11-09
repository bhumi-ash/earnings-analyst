
from analyst.query_rewriting import rewrite_query

questions = [
    "What were the consolidated total assets of Infosys in FY2025?",
    "Which Infosys business segment recorded the highest revenue growth?",
    "How many employees did Infosys have globally as of March 31, 2025?",
    "What was the standalone revenue from operations in FY2024?"
]

for question in questions:
    rewritten = rewrite_query(question)

    print("\nOriginal:", question)
    print("Rewritten:", rewritten)
