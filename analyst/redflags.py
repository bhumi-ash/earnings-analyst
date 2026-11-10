
import time

from analyst.generation import call_llm, format_context, parse_json
from analyst.retrieval import retrieve


THEMES = {
    "Auditor remarks": (
        "auditor qualified opinion adverse opinion disclaimer "
        "emphasis of matter key audit matters"
    ),
    "Related-party transactions": (
        "related party transactions material transactions "
        "shareholder approval conflict of interest transaction amount"
    ),
    "Contingent liabilities and litigation": (
        "contingent liabilities claims litigation tax disputes "
        "legal proceedings commitments amounts"
    ),
    "Liquidity and debt": (
        "borrowings outstanding debt liquidity cash flow "
        "debt repayment going concern"
    ),
    "Exceptional items": (
        "exceptional items impairment write-off restructuring "
        "one-time charges unusual expenses"
    ),
    "Accounting changes": (
        "accounting policy changes accounting estimates "
        "restatement prior period errors new accounting standards"
    ),
    "Leadership changes": (
        "resignation appointment auditor CFO chief financial officer "
        "CEO director leadership transition"
    ),
}


RULES = """You are a careful analyst reviewing company annual reports.

Use ONLY the numbered sources provided.

Return valid JSON only, using this structure:
{
  "evidence_found": true,
  "summary": "neutral summary of what the report states",
  "reported_evidence": [
    "specific fact or amount reported in the document"
  ],
  "management_explanation": [
    "management's explanation or stated position"
  ],
  "quote": "exact supporting quotation under 25 words",
  "source_id": 1,
  "why_review": "why an analyst may want to investigate this further",
  "counterpoint": "relevant context or normal explanation",
  "assessment": "routine disclosure, monitor, or requires further investigation"
}

Rules:
- Use only the supplied sources.
- Do not invent numbers, dates, entities or explanations.
- Preserve financial units and financial years exactly.
- Distinguish reported facts from management opinions.
- Include amounts and comparisons when they appear in the sources.
- If the report says there are no materially significant transactions,
  include that statement.
- Do not treat routine statutory disclosures as evidence of wrongdoing.
- A key audit matter is not automatically an adverse audit opinion.
- A leadership appointment is not automatically a governance problem.
- If evidence is insufficient, set evidence_found to false.
- If the sources do not contain management's explanation,
  return an empty management_explanation list.
- Never allege fraud, manipulation or misconduct.
- Never provide buy or sell recommendations.
"""


VALID_ASSESSMENTS = {
    "routine disclosure",
    "monitor",
    "requires further investigation",
}


def _empty_finding(theme):
    return {
        "theme": theme,
        "evidence_found": False,
        "summary": "",
        "reported_evidence": [],
        "management_explanation": [],
        "quote": "",
        "why_review": "",
        "counterpoint": "",
        "assessment": "inconclusive",
        "source": "",
        "page": None,
        "wording_flag": False,
    }


def _valid_source_id(value, hits):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 1 <= value <= len(hits)
    )


def _contains_risky_wording(data):
    text = " ".join(
        str(data.get(key, ""))
        for key in (
            "summary",
            "why_review",
            "counterpoint",
            "assessment",
        )
    ).lower()

    risky_terms = (
        "fraud",
        "scam",
        "manipulation",
        "manipulated",
        "cooked books",
        "guaranteed return",
        "buy this stock",
        "sell this stock",
    )

    return any(term in text for term in risky_terms)


def scan(company, fy, k=10, pause=4):
    """
    Scan annual-report disclosures for potential risk indicators.

    Results are screening observations, not findings of wrongdoing.
    """

    company = company.upper()
    fy = fy.upper()

    findings = []

    for theme, query in THEMES.items():

        print(f"Scanning: {theme}")

        hits = retrieve(
            query,
            k=k,
            company=company,
            fy=fy,
            doc_type="annual-report",
        )

        if not hits:
            findings.append(_empty_finding(theme))
            time.sleep(pause)
            continue

        prompt = (
            f"{RULES}\n\n"
            f"Company: {company}\n"
            f"Financial year: {fy}\n"
            f"Theme: {theme}\n\n"
            f"Sources:\n{format_context(hits)}"
        )

        try:
            data = parse_json(call_llm(prompt))

            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object.")

        except (ValueError, TypeError):
            findings.append(_empty_finding(theme))
            time.sleep(pause)
            continue

        finding = _empty_finding(theme)

        sid = data.get("source_id")

        if data.get("evidence_found") and _valid_source_id(sid, hits):

            source = hits[sid - 1]

            finding.update({
                "evidence_found": True,
                "summary": str(data.get("summary", "")),
                "reported_evidence": (
                    data.get("reported_evidence", [])
                    if isinstance(data.get("reported_evidence"), list)
                    else []
                ),
                "management_explanation": (
                    data.get("management_explanation", [])
                    if isinstance(data.get("management_explanation"), list)
                    else []
                ),
                "quote": str(data.get("quote", "")),
                "why_review": str(data.get("why_review", "")),
                "counterpoint": str(data.get("counterpoint", "")),
                "assessment": (
                    data.get("assessment", "inconclusive")
                    if data.get("assessment") in VALID_ASSESSMENTS
                    else "inconclusive"
                ),
                "source": source["meta"]["source"],
                "page": source["meta"]["page"],
            })

        finding["wording_flag"] = _contains_risky_wording(data)

        findings.append(finding)

        time.sleep(pause)

    return findings
