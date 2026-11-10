
import sys
from collections import defaultdict

from analyst.metrics import (
    get_value,
    growth_pct,
    load_verified,
    margin_pct,
)


rows = load_verified()

if not sys.argv[1:]:
    print(
        "Usage: python -m scripts.compare "
        "INFOSYS:FY2024 INFOSYS:FY2025"
    )
    raise SystemExit(1)

pairs = [arg.split(":") for arg in sys.argv[1:]]

if any(len(pair) != 2 for pair in pairs):
    raise ValueError("Each argument must be COMPANY:FY")


print("REPORTED FIGURES (verified; page = PDF viewer page)")

for company, fy in pairs:
    for metric in ("revenue", "operating_profit", "net_profit"):
        r = get_value(rows, company, fy, metric)

        print(
            f" {company} {fy} {metric}: "
            f"{r['value']} {r['unit']} (p. {r['page']})"
        )


print("\nCALCULATED METRICS (computed by Python from verified figures)")

by_company = defaultdict(list)

for company, fy in pairs:
    by_company[company].append(fy)

    rev = get_value(rows, company, fy, "revenue")
    op = get_value(rows, company, fy, "operating_profit")
    net = get_value(rows, company, fy, "net_profit")

    print(
        f" {company} {fy}: "
        f"operating margin {margin_pct(op, rev):.1f}%, "
        f"net margin {margin_pct(net, rev):.1f}%"
    )


for company, years in by_company.items():
    years = sorted(set(years))

    if len(years) >= 2:
        old, new = years[-2:]

        for metric in ("revenue", "net_profit"):
            g = growth_pct(
                get_value(rows, company, old, metric),
                get_value(rows, company, new, metric),
            )

            print(
                f" {company} {metric} growth "
                f"{old}->{new}: {g:.1f}%"
            )


print("\nThese are calculations on reported figures, not investment advice.")
