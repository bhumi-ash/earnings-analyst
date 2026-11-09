
import logging

from analyst.generation import call_llm, parse_json

log = logging.getLogger(__name__)



REWRITE_PROMPT = """You are a query-rewriting assistant for a
financial annual-report search system.

Rewrite the user's question into one concise search query that is
likely to retrieve the exact evidence from a company annual report.

Rules:
1. Preserve the original meaning. Do not answer the question.
2. Always preserve the company name if provided.
3. Always preserve the financial year or reporting date.
4. Preserve whether the question concerns consolidated or
   standalone figures.
5. Use terminology commonly found in annual reports.
6. Use terminology appropriate to the exact question:
   - For financial statements, use terms like balance sheet
     and revenue from operations.
   - For business-segment questions, preserve terms like
     business segment, segment revenue, and segment reporting.
   - Do not convert a business-segment revenue question into
     a general revenue-from-operations question.
   - For employee questions, preserve terms like total employees
     and permanent employees where relevant.
7. Do not invent facts, figures, companies, or financial years.
8. For employee headcount questions, preserve the reporting date
   and use relevant terminology such as total number of employees,
   permanent employees, other-than-permanent employees, and
   employee headcount. Do not reduce a specific headcount question
   to the generic phrase "employees globally".
9. Return JSON only in this format:
   {"rewritten_query": "..."}

User question:
"""



def rewrite_query(question):
    """Rewrite a question for better annual-report retrieval."""

    prompt = REWRITE_PROMPT + question

    try:
        data = parse_json(call_llm(prompt))

        rewritten = data.get("rewritten_query", "")

        if not isinstance(rewritten, str) or not rewritten.strip():
            return question

        return rewritten.strip()

    except Exception as exc:
        log.warning("Query rewriting failed: %s", exc)
        return question
