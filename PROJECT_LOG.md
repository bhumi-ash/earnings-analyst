# Project log
## Decisions
- Embeddings: local (fastembed, BAAI/bge-small-en-v1.5) because Gemini free-tier embedding quotas are tight.
- Vector store: Chroma persistent, metadata filters for company/FY/doc type/page.
- No LangChain: custom pipeline so every stage is explainable.
## Tests passed

- PDF inspection passed for INFOSYS_FY2025_annual-report.pdf:
  383 pages total; only pages 1 and 383 had fewer than 100 extractable characters.
  OCR is not needed for this document at the initial inspection stage.
### Step 6 — PDF text extraction validation

- Successfully extracted readable text from PDF viewer page 88, containing the CSR activities section.
- Repeated running header `Infosys Integrated Annual Report 2024-25` was detected and removed.
- Successfully extracted the financial table from PDF viewer page 274, containing the Consolidated Balance Sheet.
- Financial labels, note references, and figures for 2025 and 2024 were preserved in the extracted text.
- Observation: PDF viewer page numbers may differ from the report's printed page numbers.

### Step 7 — Text chunking validation

- Created `analyst/chunking.py` with `parse_filename()` and `chunk_text()`.
- Filename parsing passed for `INFOSYS_FY2025_annual-report.pdf`, producing company `INFOSYS`, financial year `FY2025`, and document type `annual-report`.
- Synthetic text test passed, producing 4 chunks.
- PDF viewer page 274 (printed page 302), containing the Consolidated Balance Sheet, produced 1 chunk of 1,041 characters.
- PDF viewer page 149 (printed page 177), containing employee disclosures and tables, produced 2 chunks of 1,196 and 1,128 characters.
- The test workflow chunks each page independently and displays the PDF viewer page number for each chunk.
.
## Known limitations
s6:
- Table values are extracted as text rather than structured rows and columns, so row-to-value associations should be checked during chunking and retrieval.
s7:
- Limitation observed: a chunk boundary can fall inside a table heading or table content. Table-aware chunking may be considered in a future improvement; 