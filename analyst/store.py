
import chromadb
from analyst.config import CHROMA_DIR, COLLECTION


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def upsert_chunks(ids, documents, embeddings, metadatas, batch_size=200):
    """Insert or update chunks. The same ID overwrites the existing entry."""
    collection = get_collection()

    for i in range(0, len(ids), batch_size):
        j = i + batch_size
        collection.upsert(
            ids=ids[i:j],
            documents=documents[i:j],
            embeddings=embeddings[i:j],
            metadatas=metadatas[i:j],
        )
