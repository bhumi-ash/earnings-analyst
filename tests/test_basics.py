
import pytest

from analyst.chunking import chunk_text, parse_filename
from analyst.metrics import growth_pct, margin_pct


def test_chunks_respect_max_size():
    chunks = chunk_text(
        "Revenue grew. " * 500,
        max_chars=300,
        overlap=50
    )

    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)


def test_filename_parsing():
    meta = parse_filename(
        "data/raw/infosys_FY2025_annual-report.pdf"
    )

    assert meta == {
        "company": "INFOSYS",
        "fy": "FY2025",
        "doc_type": "annual-report"
    }


def test_bad_filename_rejected():
    with pytest.raises(ValueError):
        parse_filename("bad name.pdf")


def test_growth_and_margin():
    old = {"value": 100.0, "unit": "crore"}
    new = {"value": 120.0, "unit": "crore"}

    assert growth_pct(old, new) == pytest.approx(20.0)

    assert margin_pct(
        {"value": 25.0, "unit": "crore"},
        new
    ) == pytest.approx(25.0 / 120.0 * 100)


def test_unit_mismatch_is_refused():
    with pytest.raises(ValueError):
        growth_pct(
            {"value": 1, "unit": "crore"},
            {"value": 2, "unit": "million"}
        )
