# BM25 Retrieval Experiment

## 1. Objective
Evaluate BM25 keyword-based retrieval against the existing vector-search baseline for the Infosys FY2024 and FY2025 annual reports.

## 2. Experimental Setup
- Dataset: 2 Infosys annual reports (FY2024 and FY2025)
- Total evaluation questions: 33
- Answerable questions: 28
- Unanswerable questions: 5
- Retrieval method: BM25
- Top-K: 10
- Chunk size: 1200 characters
- Chunk overlap: 150 characters
- Embedding model: BAAI/bge-small-en-v1.5 (used by the vector baseline)

## 3. Original Evaluation Results

| Retrieval Method | Successful | Total | Hit Rate |
|---|---:|---:|---:|
| Vector Search | 17 | 28 | 60.7% |
| BM25 | 23 | 28 | 82.1% |

BM25 outperformed the original vector-search baseline by 21.4 percentage points on this evaluation dataset.

## 4. Investigation of BM25 Misses

Five questions were initially missed by BM25:

| Question | Topic | Reformulated Query Result |
|---|---|---|
| Q8 | FY2025 consolidated total assets | Page 274, Rank 1 |
| Q9 | FY2024 consolidated total assets | Page 274, Rank 1 |
| Q16 | Highest consolidated segment revenue | Page 75, Rank 5 |
| Q17 | Highest segment revenue growth | Page 75, Rank 1 |
| Q28 | Total employee count | Page 134, Rank 4 |

All five questions successfully retrieved their expected evidence pages using manually reformulated queries.

## 5. Key Findings

1. BM25 performed better than the existing vector-search baseline on the current evaluation dataset.
2. Query terminology significantly influenced BM25 retrieval performance.
3. Financial statements, segment disclosures and employee information sometimes required terminology-aligned queries.
4. Query reformulation improved retrieval for all five initially missed questions in targeted experiments.

## 6. Limitations

- The evaluation dataset is relatively small.
- Query reformulation was manually performed.
- The reformulated-query results have not yet been evaluated across the entire dataset.
- Retrieval hit rate measures evidence retrieval, not final answer correctness.
- Results are based on two annual reports from one company.

## 7. Next Step

Investigate automated query reformulation and evaluate it against the original BM25 baseline using the complete evaluation dataset.