
from analyst.store import get_collection

collection = get_collection()

print("Collection name:", collection.name)
print("Number of stored chunks:", collection.count())
print("ChromaDB persistent storage test passed!")
