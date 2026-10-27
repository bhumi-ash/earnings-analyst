
from collections import Counter

import pymupdf


def extract_pages(pdf_path):
    """Return a list of page numbers and their extracted text."""
    doc = pymupdf.open(str(pdf_path))
    try:
        return [
            {"page": number, "text": page.get_text("text")}
            for number, page in enumerate(doc, start=1)
        ]
    finally:
        doc.close()


def remove_repeated_lines(pages, threshold=0.4):
    """Remove short lines repeated across many pages, such as headers and footers."""
    counts = Counter()

    for p in pages:
        for line in {line.strip() for line in p["text"].splitlines() if line.strip()}:
            counts[line] += 1

    limit = threshold * len(pages)
    repeated = {
        line for line, count in counts.items()
        if count > limit and len(line) < 120
    }

    for p in pages:
        kept = [
            line for line in p["text"].splitlines()
            if line.strip() not in repeated
        ]
        p["text"] = "\n".join(kept)

    return pages, repeated
