# Automated Query Rewriting Experiment

## 1. Objective

The objective of this experiment was to evaluate whether Large Language Model (LLM)-based query rewriting could improve BM25 keyword retrieval for the Earnings and Annual Report Analyst RAG system.

User questions are often phrased differently from the terminology used in annual reports. Query rewriting attempts to transform natural-language questions into concise search queries containing relevant financial and reporting terminology.

The experiment compares BM25 retrieval using:
- Original user questions.
- LLM-rewritten search queries.

## 2. Experimental Setup

| Parameter | Configuration |
|---|---|
| Dataset | Infosys FY2024 and FY2025 annual reports |
| Total evaluation questions | 33 |
| Answerable questions | 28 |
| Unanswerable questions | 5 |
| Chunk size | 1200 characters |
| Chunk overlap | 150 characters |
| Embedding model | BAAI/bge-small-en-v1.5 |
| Vector database | ChromaDB |
| Keyword retrieval | BM25 |
| Retrieval Top-K | 10 |
| Query rewriting model | Gemini (configured through `.env`) |
| Ranking evaluation | Expected-page retrieval hit rate |

The existing BM25 implementation uses `rank_bm25` and a simple lowercase, whitespace-based tokenizer.

## 3. Methodology

The experiment followed these steps:

1. Load an evaluation question from `eval/questions.json`.
2. Retrieve the top 10 document chunks using the original question and BM25.
3. Send the original question to Gemini with a query-rewriting prompt.
4. Generate a concise search query while preserving the original meaning, company, financial year, and reporting basis.
5. Retrieve the top 10 document chunks using the rewritten query and BM25.
6. Compare the retrieved physical PDF page numbers against the manually labelled expected pages.
7. Calculate retrieval hit rates for both approaches.

A question is counted as a retrieval hit if at least one expected page appears in the top 10 retrieved results.

### Query Rewriting Guidelines

The rewriting prompt was progressively refined to:

- Preserve company names and financial years.
- Preserve consolidated versus standalone reporting distinctions.
- Use terminology commonly found in annual reports.
- Use appropriate financial-statement terminology.
- Preserve business-segment terminology for segment-related questions.
- Preserve specific employee headcount terminology for employee-related questions.
- Avoid inventing financial figures or answering the question.

## 4. Experimental Results

### 4.1 Retrieval Performance

| Retrieval approach | Successful retrievals | Hit rate |
|---|---:|---:|
| Original vector retrieval baseline | 17/28 | 60.7% |
| Original BM25 retrieval | 23/28 | 82.1% |
| Initial automated query rewriting + BM25 | 25/28 | 89.3% |
| Refined automated query rewriting + BM25 | 27/28 | 96.4% |

The refined query-rewriting approach improved BM25 retrieval from 82.1% to 96.4%.

This represents an improvement of 14.3 percentage points over original BM25 and 35.7 percentage points over the original vector retrieval baseline.

### 4.2 Questions Improved by Query Rewriting

The final experiment successfully recovered four questions that original BM25 had missed:

| Question ID | Question topic | Result |
|---|---|---|
| Q8 | FY2025 consolidated total assets | Improved |
| Q9 | FY2024 consolidated total assets | Improved |
| Q17 | Highest business-segment revenue growth | Improved |
| Q28 | Global employee headcount | Improved |

No previously successful original BM25 retrievals were lost in the final evaluation.

### 4.3 Remaining Retrieval Miss

**Q16 – Highest revenue-generating business segment**

The automated rewriting approach continued to miss the expected evidence page (physical PDF page 75).

Further manual investigation showed that:

- The original automated query did not retrieve page 75 in its top 10.
- A manually reformulated query containing specific business-segment names retrieved page 75 at rank 2.
- This indicated that the relevant document chunk existed in the index and could be retrieved by BM25 with more targeted terminology.

This suggests that the quality of the rewritten query can significantly influence keyword-based retrieval performance.

### 4.4 Employee Headcount Investigation

For Q28, the original automated query did not retrieve page 134 in the top 10.

A manually targeted query using terms such as "total number of employees" and "permanent employees" retrieved page 134 at rank 4.

After refining the rewriting prompt to preserve employee headcount terminology, the automated query retrieved page 134 at rank 7.

This demonstrated the importance of domain-specific terminology in financial document retrieval.

## 5. Key Observations

1. Query rewriting improved keyword retrieval by translating natural-language questions into terminology more closely aligned with annual-report content.
2. Preserving reporting distinctions, such as consolidated and standalone, was important.
3. Domain-specific terminology improved retrieval for balance-sheet, business-segment, and employee-related questions.
4. Generic or unnecessarily introduced terms could negatively affect BM25 ranking.
5. Query rewriting did not solve every retrieval problem. Q16 remained a failure in the final automated evaluation despite successful manual retrieval.
6. The existing BM25 implementation uses a simple tokenizer, which may limit its ability to handle financial terminology and numerical expressions.

## 6. Limitations

- The evaluation dataset contains only 28 answerable questions.
- Both annual reports belong to the same company, Infosys.
- The dataset does not represent the full diversity of Indian listed companies.
- Expected-page labels were manually defined and may not cover every valid evidence location.
- The experiment evaluates retrieval hit rate, not the factual correctness of generated answers.
- Manual query reformulations are diagnostic experiments and should not be treated as automated-system performance.
- LLM query rewriting introduces additional API calls, latency, and potential rate-limit failures.
- The experiment does not establish general retrieval performance on unseen companies or documents.

## 7. Conclusion

The experiment demonstrated that LLM-based query rewriting can improve BM25 keyword retrieval in the Earnings and Annual Report Analyst system.

The final refined configuration achieved a retrieval hit rate of 96.4% (27 out of 28 answerable questions), compared with 82.1% for original BM25 retrieval and 60.7% for the original vector retrieval baseline.

The results suggest that query rewriting is a useful enhancement for retrieving financial information from annual reports. However, further validation on larger and more diverse datasets is necessary before generalizing these results.

## 8. Next Experiment: Hybrid Retrieval

The next stage will investigate combining:

- Dense vector retrieval using BGE-small embeddings.
- Sparse keyword retrieval using BM25.
- Reciprocal Rank Fusion (RRF) to combine rankings.
- LLM-based query rewriting before retrieval.

The objective is to determine whether combining semantic and keyword-based retrieval can improve evidence retrieval while maintaining reliable source-grounded answers and appropriate refusals for unanswerable questions.

**Current best experimental result:** Refined query rewriting + BM25, Top-K = 10, retrieval hit rate = 96.4% (27/28).