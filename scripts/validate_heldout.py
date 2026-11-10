
import json
from collections import Counter

from analyst.config import ROOT
from analyst.store import get_collection


# Load held-out questions
dataset_path = ROOT / "eval" / "heldout_questions.json"

with open(dataset_path, "r", encoding="utf-8") as file:
    questions = json.load(file)


# Load metadata from ChromaDB
collection = get_collection()

result = collection.get(
    include=["metadatas"]
)

metadata = result["metadatas"]

# Build available page numbers for Infosys FY2025
available_pages = set()

for item in metadata:
    if (
        item.get("company") == "INFOSYS"
        and item.get("fy") == "FY2025"
    ):
        available_pages.add(int(item["page"]))


# Validate dataset structure
print("=" * 55)
print("HELD-OUT DATASET VALIDATION")
print("=" * 55)

print(f"Total questions: {len(questions)}")

ids = [q["id"] for q in questions]
duplicate_ids = [
    item for item, count in Counter(ids).items()
    if count > 1
]

print("Duplicate IDs:", duplicate_ids if duplicate_ids else "None")

answerable = [q for q in questions if q["answerable"]]
unanswerable = [q for q in questions if not q["answerable"]]

print(f"Answerable questions: {len(answerable)}")
print(f"Unanswerable questions: {len(unanswerable)}")


# Validate expected pages
print("\nPAGE VALIDATION")
print("-" * 55)

page_errors = []

for q in answerable:
    missing_pages = [
        page for page in q["expected_pages"]
        if page not in available_pages
    ]

    if missing_pages:
        page_errors.append((q["id"], missing_pages))
        print(f"{q['id']}: MISSING pages {missing_pages}")
    else:
        print(f"{q['id']}: OK - {q['expected_pages']}")


# Validate unanswerable questions
invalid_unanswerable = [
    q["id"]
    for q in unanswerable
    if q["expected_pages"]
]

# Final summary
print("\n" + "=" * 55)
print("VALIDATION SUMMARY")
print("=" * 55)

print("Duplicate IDs:", len(duplicate_ids))
print("Questions with missing pages:", len(page_errors))
print(
    "Unanswerable questions with expected pages:",
    len(invalid_unanswerable)
)

if duplicate_ids or page_errors or invalid_unanswerable:
    print("\nVALIDATION FAILED - Review the issues above.")
else:
    print("\nSTRUCTURAL VALIDATION PASSED")
