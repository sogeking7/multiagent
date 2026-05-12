# Experiment Prompt for Claude Code

You are building a research experiment for an academic paper titled:
**"Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review: A Controlled Comparison Under Equal Token Budgets"**

Your job is to implement, run, and log a complete experiment comparing three LLM-based code review configurations under a controlled token budget. Everything you produce will feed directly into the paper — so structure your code, comments, and output files with that in mind.

---

## Project Structure to Create

```
code_review_experiment/
├── dataset/
│   └── samples.json          # 30 code snippets with known issues
├── configs/
│   ├── single_agent.py       # Config A
│   ├── sequential_multi.py   # Config B
│   └── parallel_multi.py     # Config C
├── evaluation/
│   └── judge.py              # GPT-4o-as-judge scorer
├── results/
│   ├── raw_outputs.json      # Full per-sample agent outputs
│   ├── metrics.json          # Aggregated metrics per config
│   └── comparison_table.md   # Human-readable summary table
├── run_experiment.py         # Master runner
└── README.md                 # Design decisions log (important for paper)
```

---

## Dataset

Create `dataset/samples.json` with **30 Python code snippets**. Each sample must have:
- `id`: string
- `code`: a Python function or short class (10–40 lines)
- `known_issues`: list of strings describing real problems in the code

Distribute issues across these categories (10 samples each):
1. **Logic bugs** — off-by-one errors, wrong conditionals, incorrect return values
2. **Security issues** — SQL injection, hardcoded credentials, unsafe deserialization
3. **Style/maintainability** — overly complex functions, missing error handling, poor naming

Write the code snippets yourself — make them realistic but intentionally flawed. Do NOT use placeholder comments like `# bug here`. The issues should be subtle enough that a non-expert might miss them.

---

## Token Budget Control

**Total output token budget per sample: 600 tokens.**

- Config A (single agent): 600 tokens in one completion
- Config B (sequential, 3 agents): 200 tokens per agent
- Config C (parallel, 3 agents + aggregator): 150 tokens per specialist agent, 150 tokens for aggregator

This is the core scientific control of the experiment. Enforce it via `max_tokens` in every API call. Log actual tokens used from the API response.

---

## Config A — Single Agent

`configs/single_agent.py`

One GPT-4o-mini call. System prompt:
```
You are an expert code reviewer. Review the provided code thoroughly.
Identify all issues including logic bugs, security vulnerabilities, and style problems.
For each issue: state the issue type, the line or area affected, and a brief explanation.
Be concise. Format: numbered list.
```

User prompt: the raw code.

---

## Config B — Sequential Multi-Agent

`configs/sequential_multi.py`

Three agents run in sequence. Each agent sees: (1) the original code, (2) all previous agents' reviews.

- **Agent 1 — Logic Reviewer**: only identify logic and correctness issues
- **Agent 2 — Security Reviewer**: only identify security vulnerabilities. You may reference Agent 1's findings to avoid duplication.
- **Agent 3 — Style Reviewer**: only identify style, readability, and maintainability issues. You may reference previous findings to avoid duplication.

Each agent's system prompt must include its role restriction explicitly.

---

## Config C — Parallel Multi-Agent

`configs/parallel_multi.py`

Three specialist agents run **independently and simultaneously** (use `asyncio` + `asyncio.gather`). Each sees only the original code, not other agents' outputs.

- **Agent 1 — Logic Reviewer**: same role as Config B Agent 1
- **Agent 2 — Security Reviewer**: same role as Config B Agent 2
- **Agent 3 — Style Reviewer**: same role as Config B Agent 3

Their outputs are then passed to a **4th Aggregator Agent**:
```
You are a senior code review coordinator. You have received three independent reviews
of the same code from specialist agents. Your job is to:
1. Merge their findings, removing exact duplicates
2. Resolve any contradictions
3. Output a clean, unified numbered list of all unique issues found
Be concise. Do not add new issues not mentioned by the specialists.
```

---

## Evaluation — GPT-4o as Judge

`evaluation/judge.py`

For each sample, for each config's final output, call GPT-4o (not mini) as a judge. Pass it:
- The original code
- The known issues list
- The config's review output

Ask it to return a JSON object:
```json
{
  "recall_score": <0.0–1.0, fraction of known_issues that were identified>,
  "precision_score": <0.0–1.0, fraction of raised issues that are valid>,
  "redundancy_count": <integer, number of duplicate or near-duplicate points in the review>,
  "relevance_score": <1–5, overall quality of the review>,
  "reasoning": "<one sentence justification>"
}
```

Instruct the judge to return ONLY valid JSON, no markdown fences.

---

## Master Runner

`run_experiment.py`

- Run all 3 configs on all 30 samples
- For each run, catch and log any API errors without crashing
- After all runs, call the judge on every output
- Aggregate metrics per config: mean recall, mean precision, mean redundancy, mean relevance, mean actual tokens used, total cost estimate (use $0.15/1M input + $0.60/1M output for gpt-4o-mini)
- Save everything to `results/`

---

## README.md — Design Decisions Log

Write a README that documents:
1. Why token budget control was chosen as the primary experimental control
2. Why these three configurations (the architectural hypothesis each one tests)
3. Why GPT-4o-mini for agents and GPT-4o for judge
4. Limitations of this experimental design
5. How the dataset was constructed and what bias it may have

**This README will be used directly as source material for the paper's Methodology section. Write it in precise, academic-adjacent language.**

---

## Final Output

After the experiment completes, print and save `results/comparison_table.md` in this format:

```
| Metric              | Config A (Single) | Config B (Sequential) | Config C (Parallel) |
|---------------------|-------------------|-----------------------|---------------------|
| Mean Recall         |                   |                       |                     |
| Mean Precision      |                   |                       |                     |
| Mean Redundancy     |                   |                       |                     |
| Mean Relevance      |                   |                       |                     |
| Mean Tokens Used    |                   |                       |                     |
| Est. Cost per 30    |                   |                       |                     |
```

Also print 3 qualitative examples: one where multi-agent clearly won, one where single-agent won, one where they tied. Save these to `results/qualitative_examples.md`.

Use the `OPENAI_API_KEY` environment variable. Do not hardcode keys.
