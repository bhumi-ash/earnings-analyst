
import sys
from pathlib import Path

from analyst.chunking import chunk_text, parse_filename
from analyst.embeddings import embed_passages
from analyst.pdf_extract import extract_pages, remove_repeated_lines
from analyst.store import upsert_chunks


def ingest(pdf_path):
    pdf_path = Path(pdf_path)
    meta = parse_filename(pdf_path)

    pages, _ = remove_repeated_lines(extract_pages(pdf_path))

    ids, documents, metadatas = [], [], []

    for p in pages:
        for n, chunk in enumerate(chunk_text(p["text"])):
            ids.append(f"{pdf_path.stem}-p{p['page']}-c{n}")
            documents.append(chunk)
            metadatas.append({
                **meta,
                "page": p["page"],
                "source": pdf_path.name,
            })

    print(
        f"{pdf_path.name}: {len(documents)} chunks "
        f"from {len(pages)} pages"
    )

    batch_size = 32

    for i in range(0, len(documents), batch_size):
        j = i + batch_size

        batch_embeddings = embed_passages(documents[i:j])

        upsert_chunks(
            ids[i:j],
            documents[i:j],
            batch_embeddings,
            metadatas[i:j]
        )

        print(
            f"Processed {min(j, len(documents))}/"
            f"{len(documents)} chunks"
        )

    print("Stored.")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        ingest(arg)
