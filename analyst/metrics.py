
import json

from analyst.config import ROOT
from analyst.generation import call_llm, format_context, parse_json
from analyst.retrieval import retrieve


CANDIDATES = ROOT / "data" / "metrics_candidates.json"
VERIFIED = ROOT / "data" / "metrics_verified.json"


QUERIES = {
    "revenue": "total revenue from operations for the year",
    "operating_profit": "operating profit EBITDA for the year",
    "net_profit": "net profit profit for the year after tax",
}


RULES = """Extract ONE figure from the numbered sources.

Return JSON only:
{
  "found": true or false,
  "value": number,
  "unit": "crore, million, lakh ...",
  "year_label": "the financial year this number belongs to",
  "source_id": 1,
  "quote": "exact text, under 25 words"
}

Rules:
- Use only the supplied sources.
- Reports may show current-year and prior-year figures side by side.
- Make sure the selected figure belongs to the requested financial year.
- Do not guess or calculate missing figures.
- If you are unsure, set found to false.
"""


def propose(company, fy, metric):
    if metric not in QUERIES:
        raise ValueError(f"Unknown metric: {metric}")

    company = company.upper()
    fy = fy.upper()

    hits = retrieve(
        QUERIES[metric],
        k=6,
        company=company,
        fy=fy,
        doc_type="annual-report",
    )

    if not hits:
        return {
            "found": False,
            "company": company,
            "fy": fy,
            "metric": metric,
            "note": "No passages were retrieved.",
        }

    prompt = (
        f"{RULES}\n\n"
        f"Requested: {metric} of {company} for {fy}.\n\n"
        f"Sources:\n{format_context(hits)}"
    )

    data = parse_json(call_llm(prompt))

    if not isinstance(data, dict):
        raise ValueError("The model did not return a JSON object.")

    sid = data.get("source_id")

    if (
        data.get("found")
        and isinstance(sid, int)
        and not isinstance(sid, bool)
        and 1 <= sid <= len(hits)
    ):
        data["page"] = hits[sid - 1]["meta"]["page"]
        data["source"] = hits[sid - 1]["meta"]["source"]
    else:
        data["found"] = False
        data["note"] = "No valid source passage was cited."

    data.update({
        "company": company,
        "fy": fy,
        "metric": metric,
    })

    return data


def load_verified():
    return json.loads(
        VERIFIED.read_text(encoding="utf-8")
    )


def get_value(rows, company, fy, metric):
    for row in rows:
        if (
            row["company"],
            row["fy"],
            row["metric"],
        ) == (
            company.upper(),
            fy.upper(),
            metric,
        ):
            return row

    raise KeyError(
        f"No verified {metric} for {company} {fy}"
    )


def _check(a, b):
    if a["unit"].lower() != b["unit"].lower():
        raise ValueError(
            f"Unit mismatch: {a['unit']} vs {b['unit']}"
        )

    if b["value"] == 0 or a["value"] == 0:
        raise ValueError("Zero value; cannot compute a ratio")


def growth_pct(old, new):
    _check(old, new)

    return (
        (new["value"] - old["value"])
        / old["value"]
        * 100
    )


def margin_pct(profit, revenue):
    _check(profit, revenue)

    return (
        profit["value"]
        / revenue["value"]
        * 100
    )
