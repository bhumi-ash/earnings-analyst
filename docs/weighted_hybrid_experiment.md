# Weighted Hybrid Retrieval Experiment

## 1. Objective

Evaluate whether assigning greater importance to BM25 than vector retrieval improves hybrid retrieval performance.

## 2. Experimental Configuration

- Dataset: Infosys FY2024 and FY2025 annual reports
- Evaluation questions: 33 total
- Answerable questions: 28
- Unanswerable questions: 5
- Chunk size: 1200 characters
- Chunk overlap: 150 characters
- Embedding model: BAAI/bge-small-en-v1.5
- Final retrieval K: 10
- Candidate K: 50
- RRF constant: 60

## 3. Methods Compared

1. Rewritten BM25 retrieval.
2. Equal-weight hybrid retrieval using Reciprocal Rank Fusion (RRF).
3. BM25-weighted hybrid retrieval using RRF.

The weighted hybrid assigned BM25 a weight of 2 and vector retrieval a weight of 1.

Formula:

RRF(d) = 2 / (60 + BM25_rank) + 1 / (60 + Vector_rank)

Each question was rewritten once, and the same rewritten query was supplied to all three retrieval methods.

## 4. Results

| Method | Correct retrievals | Hit rate |
|---|---:|---:|
| Rewritten BM25 | 27/28 | 96.4% |
| Equal-weight hybrid | 26/28 | 92.9% |
| BM25-weighted hybrid | 26/28 | 92.9% |

### Missed Questions

- Rewritten BM25: Q16
- Equal-weight hybrid: Q17, Q25
- BM25-weighted hybrid: Q17, Q25

## 5. Observations

- BM25 remained the strongest retrieval method.
- Both hybrid methods successfully retrieved the expected page for Q16, which BM25 missed.
- Both hybrid methods failed to retrieve the expected pages for Q17 and Q25.
- Increasing the BM25 weight from 1 to 2 did not improve the overall hybrid hit rate.
- Hybrid fusion did not outperform rewritten BM25 on this evaluation dataset.

## 6. Conclusion

Query rewriting combined with BM25 achieved the highest retrieval hit rate of 96.4%.

Neither equal-weight nor BM25-weighted hybrid retrieval improved upon this result.

Therefore, rewritten BM25 is selected as the current retrieval baseline. Hybrid retrieval remains a possible future improvement, but further tuning is not justified by the current experimental results.

## 7. Limitations

- The evaluation uses only two annual reports from one company.
- The answerable evaluation set contains only 28 questions.
- Results may vary with different companies, document structures, and query types.
- Retrieval hit rate measures whether an expected page appears in the top 10 results; it does not measure final answer correctness or citation accuracy.
