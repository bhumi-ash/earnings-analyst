from analyst.store import get_collection

collection = get_collection()

result = collection.get(
    where={
        "$and": [
            {"fy": "FY2025"},
            {
                "page": {
                    "$in": [73, 242, 321]
                }
            }
        ]
    },
    include=["documents", "metadatas"]
)

for i, document in enumerate(result["documents"]):
    metadata = result["metadatas"][i]

    print("\n" + "=" * 80)
    print("Metadata:", metadata)
    print(document)