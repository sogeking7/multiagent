# Context Harvester Prompt (run inside the project with Claude Code)

You are preparing a research context document. Read every file in this project and produce a single, comprehensive markdown document called `paper_context.md`. This document will be handed to a research model to write an academic paper — so it must be complete, structured, and self-contained. Someone with no access to this project should be able to write the full paper from `paper_context.md` alone.

---

## What to Extract and Include

### 1. Research Question & Hypothesis
State the precise research question this experiment answers.
State the hypothesis that was being tested.

### 2. Experiment Design Summary
- The three configurations (A, B, C) with their architectural descriptions
- The token budget control mechanism and why it matters
- The dataset: how many samples, what categories, how issues were labeled
- The evaluation method: judge model, metrics definition

### 3. Full Results
Copy the entire comparison table from `results/metrics.json` and `results/comparison_table.md`.
Include per-category breakdowns if available (logic vs security vs style).

### 4. Qualitative Examples
Include all examples from `results/qualitative_examples.md` verbatim.
For each example, note which config won and what the winning config did differently.

### 5. Agent Prompts Used
Copy the exact system prompts used for every agent in every config.
Label clearly: Config A system prompt, Config B Agent 1 system prompt, etc.
These will appear in the paper appendix.

### 6. Key Findings (your interpretation)
Based on the results, write 4–6 bullet points summarizing what the numbers show.
Be honest — if multi-agent did not clearly win, say so. If results are mixed, describe the pattern.

### 7. Surprises & Anomalies
Note anything unexpected: a config that consistently failed on one category, 
unusually high redundancy, cases where the judge disagreed with known_issues, etc.

### 8. Limitations
List at least 5 concrete limitations of this experiment design.

### 9. Cost Summary
Total API cost of the experiment (agents + judge calls).

### 10. File Inventory
List every file in the project with a one-line description of its contents.

---

## Format Rules

- Use clear `##` headers for each section above
- Do not summarize or paraphrase results — copy numbers exactly
- Do not omit agent prompts — they are critical for the paper
- Flag any missing data with `[MISSING]` rather than skipping it
- Keep the document under 4000 words if possible, but do not sacrifice completeness for brevity

Save output as `paper_context.md` in the project root.
