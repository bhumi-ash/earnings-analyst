
import sys

from analyst.logging_setup import setup_logging
setup_logging()

from analyst.redflags import scan


if len(sys.argv) != 3:
    print("Usage: python -m scripts.red_flags COMPANY FY")
    raise SystemExit(1)


company = sys.argv[1].upper()
fy = sys.argv[2].upper()

findings = scan(company, fy)

for finding in findings:

    print(f"\n== {finding['theme']} ==")

    if not finding["evidence_found"]:
        print("No supporting evidence found in retrieved passages.")
        print("This does not establish that the disclosure is absent.")
        continue

    print("Summary:", finding["summary"])

    print("\nReported evidence:")
    for item in finding["reported_evidence"]:
        print("-", item)

    print("\nManagement explanation:")
    for item in finding["management_explanation"]:
        print("-", item)

    print("\nSupporting quotation:")
    print(finding["quote"])

    print(
        f"Source: {finding['source']} "
        f"| PDF page: {finding['page']}"
    )

    print("\nWhy review:", finding["why_review"])
    print("Counterpoint:", finding["counterpoint"])
    print("Assessment:", finding["assessment"])

    if finding["wording_flag"]:
        print("WARNING: Review wording for unsupported claims.")

print(
    "\nDisclaimer: These are screening observations based on "
    "retrieved report passages, not findings of wrongdoing "
    "or investment advice."
)
