
import json
import logging
import time

from google import genai
from google.genai import types

from analyst.config import require_env

log = logging.getLogger(__name__)


SYSTEM_RULES = """You are a careful analyst of company annual reports and
earnings-call transcripts.
Rules:
1. Use ONLY the numbered sources below. Never use outside knowledge.
2. If the sources do not contain the answer, set "found" to false and say
   what is missing. Do not guess.
3. Quote numbers exactly as written, with units and the financial year they
   refer to.
4. Do not give investment advice or predictions.
5. Reply with JSON only, in this shape:
   {"found": true or false, "answer": "...", "source_ids": [1, 2]}
   source_ids must list only the sources you actually used."""


def format_context(hits):
    blocks = []

    for n, h in enumerate(hits, start=1):
        m = h["meta"]

        header = (
            f"[Source {n}] {m['company']} {m['fy']} "
            f"{m['doc_type']}, page {m['page']}"
        )

        blocks.append(f"{header}\n{h['text']}")

    return "\n\n".join(blocks)


def call_llm(prompt, retries=3):
    """Call Gemini, retrying on rate-limit and temporary server errors."""
    client = genai.Client(api_key=require_env("GEMINI_API_KEY"))
    model = require_env("GEMINI_MODEL")

    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                ),
            )

            return response.text

        except Exception as exc:
            code = getattr(exc, "code", None)

            if code in (429, 500, 503) and attempt < retries:
                wait = 5 * attempt**2

                log.warning(
                    "LLM error %s, retrying in %ss", code, wait
                )

                time.sleep(wait)
                continue

            raise


def parse_json(raw):
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.strip("`")

        if raw.lower().startswith("json"):
            raw = raw[4:]

    return json.loads(raw)


def answer_question(question, hits):
    if not hits:
        return {
            "found": False,
            "answer": "No passages were retrieved.",
            "sources": []
        }

    prompt = (
        f"{SYSTEM_RULES}\n\nSources:\n{format_context(hits)}"
        f"\n\nQuestion: {question}"
    )

    try:
        data = parse_json(call_llm(prompt))

    except json.JSONDecodeError:
        return {
            "found": False,
            "answer": "The model reply could not be read.",
            "sources": []
        }

    ids = [
        i for i in data.get("source_ids", [])
        if isinstance(i, int) and 1 <= i <= len(hits)
    ]

    return {
        "found": bool(data.get("found")),
        "answer": str(data.get("answer", "")),
        "sources": [hits[i - 1] for i in ids],
    }
LABELLED_RULES = """You are a careful analyst of company reports. Use ONLY
the numbered sources.
Reply with JSON only:
{"found": true or false, "note": "what is missing, if anything",
  "reported_facts": [{"text": "...", "source_ids": [1]}],
  "management_claims": [{"text": "...", "source_ids": [2]}],
  "interpretation": [{"text": "...", "source_ids": [1, 2]}]}
Definitions:
- reported_facts: numbers or statements the documents present as facts.
- management_claims: explanations, opinions or outlook by management. Start
  with "Management says".
- interpretation: your own cautious reading. Say it is an inference. Never do
  arithmetic yourself.
Do not give investment advice. If sources disagree (for example report vs
call), say so in interpretation."""


def answer_labelled(question, hits):
    empty = {
        "found": False,
        "answer": "",
        "sources": [],
        "reported_facts": [],
        "management_claims": [],
        "interpretation": [],
    }

    if not hits:
        return {**empty, "answer": "No passages were retrieved."}

    prompt = (
        f"{LABELLED_RULES}\n\nSources:\n{format_context(hits)}"
        f"\n\nQuestion: {question}"
    )

    try:
        data = parse_json(call_llm(prompt))

    except json.JSONDecodeError:
        return {
            **empty,
            "answer": "The model reply could not be read."
        }

    out = {
        **empty,
        "found": bool(data.get("found")),
        "answer": str(data.get("note", "")),
    }

    used = set()

    for key in (
        "reported_facts",
        "management_claims",
        "interpretation",
    ):
        items = data.get(key, [])

        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, dict):
                continue

            raw_ids = item.get("source_ids", [])

            if not isinstance(raw_ids, list):
                raw_ids = []

            ids = sorted({
                i for i in raw_ids
                if isinstance(i, int)
                and not isinstance(i, bool)
                and 1 <= i <= len(hits)
            })

            used.update(ids)

            cites = ", ".join(
                f"{hits[i - 1]['meta']['source']} "
                f"p.{hits[i - 1]['meta']['page']}"
                for i in ids
            )

            text = str(item.get("text", "")).strip()

            if text:
                citation = f" [{cites}]" if cites else " [No valid source cited]"
                out[key].append({
                    "text": text + citation
                })

    out["sources"] = [
        hits[i - 1] for i in sorted(used)
    ]

    return out