
import re
from pathlib import Path


def parse_filename(path):
    """INFOSYS_FY2025_annual-report.pdf -> company, fy, doc_type."""
    parts = Path(path).stem.split("_")

    if len(parts) != 3:
        raise ValueError(
            f"File name must be COMPANY_FYxxxx_doctype.pdf, "
            f"got: {Path(path).name}"
        )

    company, fy, doc_type = parts

    return {
        "company": company.upper(),
        "fy": fy.upper(),
        "doc_type": doc_type.lower(),
    }


def chunk_text(text, max_chars=1200, overlap=150):
    """Split text into overlapping chunks, preferring to break at
    line/sentence ends."""
    text = re.sub(r"[ \t]+", " ", text).strip()

    chunks, start = [], 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        if end < len(text):
            cut = max(
                text.rfind(". ", start, end),
                text.rfind("\n", start, end),
            )

            if cut > start + max_chars // 2:
                end = cut + 1

        piece = text[start:end].strip()

        if piece:
            chunks.append(piece)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks
