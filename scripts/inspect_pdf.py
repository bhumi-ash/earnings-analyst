
import sys
import pymupdf

doc = pymupdf.open(sys.argv[1])
print("pages:", len(doc))

low = 0
for number, page in enumerate(doc, start=1):
    chars = len(page.get_text("text").strip())
    if chars < 100:
        low += 1
        print(f"page {number}: only {chars} characters")

print("pages with very little text:", low)
