from analyst.store import get_collection

collection = get_collection()

result = collection.get(
    where={
        "$and": [
            {"fy": "FY2025"},
            {"page": 135}
        ]
    },
    include=["documents", "metadatas"]
)

print("Number of chunks:", len(result["ids"]))

for i, document in enumerate(result["documents"]):
    print("\n" + "=" * 70)
    print("Metadata:", result["metadatas"][i])
    print(document[:2500])