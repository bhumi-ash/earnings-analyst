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

### Step 8 — Loading Embeddings

- Created analyst/embeddings.py using BAAI/bge-small-en-v1.5.
- Created scripts/test_embed.py to test document and query embeddings.
- The model downloaded successfully on the first run.
- Test passed: 2 sample documents produced 2 vectors.
- Document embedding dimension: 384.
- Query embedding dimension: 384.
- The first 10 values of the first embedding were printed successfully.
- The embedding model is cached locally for reuse; the first model download required an internet       connection.
- Similarity test passed: the question "How much did sales increase?" scored 0.716 against the revenue sentence and 0.331 against the unrelated cat sentence.
- The revenue sentence scored higher, confirming the expected ranking in this small test.

### Step 9 — Vector store and injestion

- Installed ChromaDB successfully.
- Created analyst/store.py with persistent collection access and batched upsert functionality.
- Created and ran scripts/test_store.py successfully.
- Confirmed collection name: reports_bge_small_v1.
- Initial collection count: 0, as expected before ingestion.

## Known limitations
s6:
- Table values are extracted as text rather than structured rows and columns, so row-to-value associations should be checked during chunking and retrieval.
s7:
- Limitation observed: a chunk boundary can fall inside a table heading or table content. Table-aware chunking may be considered in a future improvement; 

### Step 10: Retrieval quality evaluation

Test question: What was the operating margin?
Filter: INFOSYS, FY2025
Top 6 retrieved chunks.

Relevant result:
- Page 75: Contains segmental operating margin figures.
  Total segmental operating margin was 24.1% in FY2025
  compared with 23.7% in FY2024.

Partially relevant:
- Page 30: Contains financial results, revenue, expenses
  and profit figures, but does not directly state
  operating margin.

Irrelevant results:
- Page 241: Revenue recognition accounting policy.
- Page 292: Operating margin assumptions used for
  goodwill impairment testing.
- Page 325: Lease accounting and right-of-use assets.
- Page 320: Deferred income taxes and revenue
  recognition accounting policy.

Observation:
Only one of the six retrieved chunks directly answered
the question. The retrieval system sometimes matches
financial terminology without retrieving the exact
financial metric requested.

Improvement needed: Evaluate retrieval quality and
consider improving chunking and retrieval relevance.

### Step 11: Grounded answer generation

- Implemented Gemini-based answer generation.
- Added source formatting and JSON response parsing.
- Added retry handling for temporary API errors.
- Tested an answerable question:
  "What was the revenue in FY2025?"
  The system returned standalone revenue of ₹1,36,592 crore
  and consolidated revenue of ₹1,62,990 crore.
- Tested an unanswerable question:
  "What is the CEO's favourite food?"
  The system correctly returned FOUND: False.
- Both initial end-to-end tests passed.

### Step 12: Multiple document ingestion

- Downloaded and inspected Infosys FY2024 annual report.
- FY2024 PDF: 352 pages, 3 pages with very little extractable text.
- Successfully ingested FY2024 report: 1,227 chunks.
- ChromaDB total: 2,518 chunks.
- Tested FY2024 retrieval filter: all results belonged to FY2024.
- Tested FY2025 retrieval filter: all results belonged to FY2025.
- Metadata filtering works correctly across financial years.
- Retrieval relevance still needs improvement and will be evaluated in Step 15.

### Step 13: Streamlit application

- Installed Streamlit and created the main app.py interface.
- Added company, financial-year and document-type filters.
- Added a configurable top-k retrieval slider.
- Integrated the retrieval and Gemini answer-generation pipelines.
- Added expandable source passages with PDF viewer page numbers.
- Successfully launched the app locally at localhost:8501.
- Tested: "What was the revenue from operations in FY2025?"
- Retrieved consolidated revenue of ₹1,62,990 crore.
- Retrieved standalone revenue of ₹1,36,592 crore.
- Verified both figures against the retrieved annual-report passages.
- Initial end-to-end Streamlit test passed.


### Step 14 — Evaluation dataset and initial retrieval baseline

- Created an evaluation dataset containing 33 questions:
  - 28 answerable questions.
  - 5 unanswerable questions.
- Established the original vector retrieval baseline on the development evaluation set.

**Initial vector retrieval baseline:**
- Retrieval hits: 18/28 (64.3%).
- Correct refusals: 5/5 (100%) in the evaluation comparison.
- This baseline was used to compare subsequent retrieval improvements.

- Evaluation results were saved to CSV files.
- The initial baseline showed that retrieval relevance needed improvement before relying on generated answers.

**Manual answer review from the later rewritten-BM25 development run:**
- Answer correctness: 31/33 (93.9%), provisional.
- Q15: Revenue growth answer was incomplete because it omitted the FY2024 comparison.
- Q16: The system incorrectly refused to identify the highest-revenue segment.
- Citation correctness was not fully audited at this stage, so no overall citation-accuracy score was recorded.



### Step 15 — Retrieval improvement experiments

The following experiments were conducted using the 33-question development evaluation dataset (28 answerable and 5 unanswerable questions), unless otherwise specified.

**1. Chunk size**

Compared chunk sizes of 800, 1,200 and 2,000 characters.

| Chunk size | Retrieval hit rate |
|---|---:|
| 800 | 50.0% |
| 1,200 | 60.7% |
| 2,000 | 57.1% |

- Retained 1,200 characters as the chunk size.
- Overlap: 150 characters.

**2. Top-k**

- Tested retrieval values K = 4, 6 and 10.
- The application supports configurable top-k retrieval.
- K = 10 was used for the final development-set end-to-end evaluation.

**3. Metadata filters**

- Implemented company and financial-year filters.
- Tested filtering across Infosys FY2024 and FY2025 reports.
- Confirmed that retrieved results respected the selected financial-year filters.

**4. Distance threshold**

- Tested distance-threshold filtering to exclude less relevant retrieval results.
- No numerical threshold result is recorded in this log.

**5. Prompt improvements**

- Improved query-rewriting rules to preserve company, financial year and reporting context.
- Updated answer-generation instructions to include the financial year when reporting numerical values.
- Retained source-grounded answers and refusal behaviour for questions unsupported by retrieved passages.

**6. BM25 and hybrid retrieval**

Compared retrieval methods on the 28 answerable questions in the development evaluation set.

| Retrieval method | Retrieval hits |
|---|---:|
| Original vector retrieval | 18/28 (64.3%) |
| BM25 | 23/28 (82.1%) |
| Rewritten BM25 | 27/28 (96.4%) |
| Hybrid retrieval | 26/28 (92.9%) |

- Rewritten BM25 produced the best retrieval result in this comparison.
- Rewritten BM25 was selected as the final retrieval method for the current MVP.
- Development-set end-to-end evaluation using rewritten BM25 with K = 10:
  - Retrieval hit rate: 27/28 (96.4%).
  - Correct refusals: 5/5 (100%).
  - Model/API errors: 0.
- Manual answer review from this run recorded provisional answer correctness of 31/33 (93.9%).

**7. Additional held-out retrieval evaluation**

- A separate held-out dataset contained 25 questions:
  - 20 answerable questions.
  - 5 unanswerable questions.

Initial recorded comparison:

| Retrieval method | Hits |
|---|---:|
| Rewritten BM25 | 14/20 (70%) |
| BM25 | 12/20 (60%) |
| Vector retrieval | 5/20 (25%) |

- The held-out dataset was subsequently used for retrieval debugging and expected-page corrections.
- In the later recorded rewritten-BM25 run, retrieval hit rate was 15/20 (75%).
- Manual review of the later held-out run:
  - Answer correctness: 16/20 (80%).
  - Citation correctness: 17/20 (85%).
  - Correct refusals: 5/5 (100%).
- These later held-out results are diagnostic results, not a pristine final test score, because the dataset was used during debugging.
- Answer correctness and citation correctness were evaluated separately. An answer can be incorrect while its cited source is still relevant.

**Step 15 conclusion**

- Rewritten BM25 was selected as the current retrieval method based on the development evaluation.
- Chunk size remains 1,200 characters with 150-character overlap.
- Company and financial-year metadata filtering is implemented.
- The optional Gemini embedding-model comparison was skipped because local embeddings were retained to avoid free-tier embedding quota limitations.
- Development-set and held-out results are reported separately and should not be directly treated as equivalent measurements.

### Step 15 — Document ingestion and BM25 index refresh verification

- Inspected `scripts/ingest.py` and `analyst/store.py`.
- Confirmed that PDF ingestion extracts text, performs page-level chunking, generates embeddings and stores chunks in the persistent ChromaDB collection.
- Confirmed that `upsert_chunks()` uses ChromaDB upsert operations.
- Chunk IDs are generated using the PDF filename, page number and chunk number.
- Re-ingesting an unchanged PDF updates existing records with matching IDs rather than creating duplicate records.

**BM25 index refresh behaviour:**

- `retrieve_bm25()` fetches the current filtered documents directly from ChromaDB whenever retrieval is performed.
- The BM25 index is constructed dynamically for each retrieval request.
- Newly ingested or updated documents are therefore available to subsequent BM25 queries without a separate index-refresh operation.
- No persistent BM25 index is maintained.

**Known limitation:**

- If document chunking changes, previously stored chunk IDs that are no longer generated may remain in ChromaDB.
- Document replacement or re-chunking may therefore require explicit cleanup of obsolete records.
- Dynamic BM25 index construction also introduces additional retrieval-time computation as the document collection grows.

**Verification outcome:** Ingestion and BM25 refresh behaviour confirmed by code inspection.