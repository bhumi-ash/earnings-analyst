
import json
import sys
import time

from analyst.metrics import CANDIDATES, QUERIES, propose


if len(sys.argv) < 3:
    print(
        "Usage: python -m scripts.propose_metrics "
        "COMPANY FY1 FY2 ..."
    )
    raise SystemExit(1)


company = sys.argv[1].upper()
years = [year.upper() for year in sys.argv[2:]]

results = (
    json.loads(CANDIDATES.read_text(encoding="utf-8"))
    if CANDIDATES.exists()
    else []
)

for fy in years:
    for metric in QUERIES:
        print(f"\nExtracting {metric} for {company} {fy}...")

        try:
            row = propose(company, fy, metric)
            results.append(row)
            print(json.dumps(row, indent=2))

        except Exception as exc:
            print(f"Extraction failed: {exc}")

        time.sleep(4)

CANDIDATES.parent.mkdir(parents=True, exist_ok=True)

CANDIDATES.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print(f"\nCandidate figures saved to: {CANDIDATES}")
