
import sys

from analyst.pdf_extract import extract_pages, remove_repeated_lines
from analyst.chunking import parse_filename, chunk_text


pdf_path = sys.argv[1]
page_number = int(sys.argv[2])

# Extract the PDF pages and remove repeated headers/footers
pages = extract_pages(pdf_path)
pages, removed = remove_repeated_lines(pages)

# Select one page and split only that page into chunks
page = pages[page_number - 1]
chunks = chunk_text(page["text"])

# Parse report metadata from the filename
metadata = parse_filename(pdf_path)

print("Report metadata:", metadata)
print("PDF viewer page:", page_number)
print("Chunks created:", len(chunks))
print("Chunk lengths:", [len(chunk) for chunk in chunks])

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Page {page_number}, Chunk {index} ---")
    print(chunk[:250])
