# Comparison Table

Token budget: 600 output tokens per sample across all configurations.
Costs are for agent calls only (gpt-4o-mini) and exclude judge tokens.

| Metric              | Config A (Single) | Config B (Sequential) | Config C (Parallel) |
|---------------------|-------------------|-----------------------|---------------------|
| Mean Recall         | 98.3% | 93.9% | 80.6% |
| Mean Precision      | 48.0% | 48.1% | 55.0% |
| Mean Redundancy     | 0.200 | 1.733 | 0.300 |
| Mean Relevance      | 3.100 | 2.933 | 3.133 |
| Mean Tokens Used    | 595.9 | 1692.6 | 1791.6 |
| Est. Cost per 30    | $0.0086 | $0.0149 | $0.0157 |

## Per-category recall (defect-finding by issue type)

| Category | Config A | Config B | Config C |
|----------|----------|----------|----------|
| logic    | 100.0% | 100.0% | 100.0% |
| security | 100.0% | 95.0% | 95.0% |
| style    | 95.0% | 86.7% | 46.7% |

## Run / judge errors

| Config | Run errors | Judge errors | Samples scored |
|--------|-----------:|-------------:|---------------:|
| A_single_agent | 0 | 0 | 30 |
| B_sequential_multi | 0 | 0 | 30 |
| C_parallel_multi | 0 | 0 | 30 |
