
import sys

from analyst.pdf_extract import extract_pages, remove_repeated_lines

pages = extract_pages(sys.argv[1])
pages, removed = remove_repeated_lines(pages)

print("removed repeated lines:", list(removed)[:10])

wanted = int(sys.argv[2])
print(pages[wanted - 1]["text"][:2000])
