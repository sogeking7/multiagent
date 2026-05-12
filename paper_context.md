# Paper Context — Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review

This document is the complete research-context bundle for the paper
*"Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review: A Controlled Comparison Under Equal Token Budgets."*
Everything a writer needs is captured below; no access to the source repository
should be required.

---

## 1. Research Question & Hypothesis

**Research question.** *Given a fixed output-token budget per sample, does
role-specialised multi-agent code review (sequential or parallel + aggregator)
produce better reviews than a single generalist agent operating under the
same budget?*

The framing matters. The popular intuition that "multi-agent beats single
agent" is almost always tested without a budget control: the multi-agent
system also issues more LLM calls and emits more total tokens, so any lift
is jointly explained by architecture and by raw compute. This experiment
holds output-token budget constant across configurations so that the
architectural question is isolated from the compute question.

**Hypothesis (pre-registered, framed as the multi-agent claim under test).**
Role-specialised multi-agent review (Configs B and C) will produce higher
recall and lower redundancy than a single generalist agent (Config A) at
the same total output-token budget, because (i) focused-role prompts admit
denser, less hedged reviews per role, and (ii) explicit deduplication —
sequential context-sharing in B or an aggregator in C — should keep the
final output clean.

**Result (preview).** The hypothesis is *not* supported on the headline
recall metric. Across 30 samples, multi-agent (B or C) never exceeds
single-agent recall on any single sample; on style/maintainability defects
it loses substantially. The role-specialisation architecture buys a small
precision lift (Config C) at a large recall cost. Details follow.

---

## 2. Experiment Design Summary

### Three configurations under equal 600-token output budget

| Config | Architecture | Budget split |
|--------|--------------|--------------|
| **A — Single agent** | One `gpt-4o-mini` call. System prompt asks for a numbered list of logic, security, and style issues. | 600 tokens total |
| **B — Sequential multi-agent** | Three specialists run in order: Logic → Security → Style. Each sees the original code plus all earlier reviews and is told not to duplicate prior findings. | 200 × 3 = 600 |
| **C — Parallel multi-agent + aggregator** | Three specialists (Logic, Security, Style) run independently via `asyncio.gather`, then a fourth Aggregator agent merges their findings into a unified deduplicated list. | 150 × 3 + 150 = 600 |

`max_tokens` is set per call to enforce each split; `usage.completion_tokens`
from the API response is recorded for verification (see §3 cost table:
mean output tokens never exceed the budget for any config).

**Why budget control matters.** Without an equal output-token cap, a
multi-agent system that "wins" cannot be distinguished from one that
"used more compute." Equalising output tokens isolates the architectural
contribution from the compute contribution. Input tokens are *not*
equalised — by design, B (later agents read prior output) and C
(aggregator reads all specialists) have larger input footprints. We
report input, output, and total tokens separately.

### Dataset

`dataset/samples.json` — **30 Python snippets**, 10–22 lines each, stratified
into three categories of 10 samples:

- **Logic bugs (L1–L10):** off-by-one in pagination/moving-average, missing
  empty-input handling, mutable default arg, integer floor-division on a
  mean, late-binding closure, inverted comparison enabling privilege
  escalation, missing recursive base case (factorial(0)), naive CSV
  splitting on quoted commas, float-equality on money.
- **Security issues (S1–S10):** SQL injection via f-string, hardcoded
  production credentials, `pickle.loads` on a cookie, path traversal,
  `random` (Mersenne Twister) for reset tokens, command injection via
  `shell=True`, stored XSS, MD5 password hashing (+ non-constant-time
  comparison), SSRF on a user-supplied URL, `eval()` on user input.
- **Style / maintainability (ST1–ST10):** 5-level nested `if`, missing
  error handling on `json.loads`, single-letter parameter names + magic
  tax rates, length-only password strength, missing validation +
  non-atomic money transfer, DRY violation across three near-identical
  renderers, signup handler with five responsibilities, bare `except`,
  module-level mutable cache without invalidation, inconsistent return
  types (User / False / None).

Each sample carries a hand-written `known_issues` list (1–3 items) that
serves as the canonical ground truth for recall. Several samples carry
multiple known issues, making recall scoring more discriminating than a
one-issue-per-sample design.

### Evaluation: GPT-4o as judge

`evaluation/judge.py` calls `gpt-4o` (the larger sibling of the agent model)
once per (sample, config) pair. The judge sees:

1. The original code.
2. The canonical `known_issues` list.
3. The configuration's final review text.

It returns a JSON object with:

- `recall_score` ∈ [0.0, 1.0] — fraction of canonical known issues
  identified (near-paraphrases count).
- `precision_score` ∈ [0.0, 1.0] — fraction of distinct issues raised
  that are valid real problems (whether or not they appear in the
  canonical list).
- `redundancy_count` ∈ ℤ≥0 — count of duplicate or near-duplicate points
  in the review.
- `relevance_score` ∈ {1,2,3,4,5} — overall quality of the review as a
  holistic code-review artifact.
- `reasoning` — one-sentence justification.

Judge response format is `{"type": "json_object"}` with `temperature=0`.
The harness extracts the JSON defensively and clamps each field into its
expected range. Across the 30 × 3 = 90 judge calls in this run, **zero**
parse errors occurred.

Agents run at `temperature=0.2` — low but non-zero, so the three Config-C
specialists do not produce literally identical text that would
artificially inflate the redundancy metric.

---

## 3. Full Results

### Aggregate metrics (verbatim from `results/comparison_table.md`)

> Token budget: 600 output tokens per sample across all configurations.
> Costs are for agent calls only (gpt-4o-mini) and exclude judge tokens.

| Metric              | Config A (Single) | Config B (Sequential) | Config C (Parallel) |
|---------------------|-------------------|-----------------------|---------------------|
| Mean Recall         | 98.3%             | 93.9%                 | 80.6%               |
| Mean Precision      | 48.0%             | 48.1%                 | 55.0%               |
| Mean Redundancy     | 0.200             | 1.733                 | 0.300               |
| Mean Relevance      | 3.100             | 2.933                 | 3.133               |
| Mean Tokens Used    | 595.9             | 1692.6                | 1791.6              |
| Est. Cost per 30    | $0.0086           | $0.0149               | $0.0157             |

### Per-category recall (defect-finding by issue type)

| Category | Config A | Config B | Config C |
|----------|----------|----------|----------|
| logic    | 100.0%   | 100.0%   | 100.0%   |
| security | 100.0%   | 95.0%    | 95.0%    |
| style    | 95.0%    | 86.7%    | 46.7%    |

### Per-category precision

| Category | Config A | Config B | Config C |
|----------|----------|----------|----------|
| logic    | 41.7%    | 41.5%    | 46.7%    |
| security | 55.6%    | 50.0%    | 62.4%    |
| style    | 46.6%    | 52.9%    | 55.8%    |

### Token-usage breakdown (input vs. output)

| Config | Mean tokens in | Mean tokens out | Mean total | Σ in (30) | Σ out (30) | $ (30 samples) |
|--------|---------------:|----------------:|-----------:|----------:|-----------:|---------------:|
| A      | 161.2          | 434.7           | 595.9      | 4,837     | 13,041     | 0.00855        |
| B      | 1,154.5        | 538.1           | 1,692.6    | 34,636    | 16,142     | 0.014881       |
| C      | 1,222.5        | 569.1           | 1,791.6    | 36,676    | 17,072     | 0.015745       |

Output tokens stay under budget for every configuration on every sample
(no API call exceeded its `max_tokens`). Input cost grows substantially
for B (later agents re-read prior reviews) and C (aggregator reads all
specialist outputs).

### Reliability

| Config | Run errors / 30 | Judge parse errors / 30 | Samples scored |
|--------|----------------:|------------------------:|---------------:|
| A      | 0               | 0                       | 30             |
| B      | 0               | 0                       | 30             |
| C      | 0               | 0                       | 30             |

### Per-sample recall pattern (full grid)

Auditing each sample reveals the clean conclusion that the aggregates
above hide. "A wins" means `recall(A) > max(recall(B), recall(C))`.

| Sample | Category | A | B | C | Pattern |
|--------|----------|---|---|---|---------|
| L1–L10 | logic    | 1.00 | 1.00 | 1.00 | 3-way tie (10/10) |
| S1–S8, S10 | security | 1.00 | 1.00 | 1.00 | 3-way tie (9/10) |
| S9     | security | 1.00 | 0.50 | 0.50 | **A wins** |
| ST1    | style    | 1.00 | 1.00 | 0.50 | A wins |
| ST2    | style    | 1.00 | 1.00 | 1.00 | tie |
| ST3    | style    | 1.00 | 1.00 | 0.00 | A wins |
| ST4    | style    | 1.00 | 1.00 | 0.50 | A wins |
| ST5    | style    | 1.00 | 0.67 | 0.67 | A wins |
| ST6    | style    | 1.00 | 1.00 | 0.00 | A wins |
| ST7    | style    | 0.50 | 0.50 | 0.50 | tie (low) |
| ST8    | style    | 1.00 | 1.00 | 0.50 | A wins |
| ST9    | style    | 1.00 | 0.50 | 0.50 | A wins |
| ST10   | style    | 1.00 | 1.00 | 0.50 | A wins |

**Critical observation: across all 30 samples, there is not a single
sample on which multi-agent (B or C) beats single-agent (A) on recall.**
A either ties or wins every time. Single-agent wins are concentrated
entirely in the style/maintainability category.

---

## 4. Qualitative Examples

The auto-selected examples below come from `results/qualitative_examples.md`
verbatim. **Note (also flagged in §7):** the "Multi-agent clearly won"
selector degenerated to a tied sample because no sample actually exists
where multi-agent beats single-agent — the picker therefore selected the
first sample with the maximum (zero) recall gap. A more honest framing
is given underneath the verbatim block.

### 4a. Verbatim qualitative examples

#### "Multi-agent clearly won" — sample `L1` (logic)

Recall by config: A=1.00, B=1.00, C=1.00 *(actually a tie; see §7)*

**Code under review**

```python
from typing import Iterable, List, TypeVar

T = TypeVar("T")


def paginate(items: List[T], page: int, page_size: int) -> List[T]:
    """Return the items belonging to the requested 1-indexed page."""
    start = page * page_size
    end = start + page_size
    return items[start:end]


def page_count(items: Iterable[T], page_size: int) -> int:
    return (len(list(items)) + page_size - 1) // page_size
```

**Canonical known issues**

- Off-by-one in paginate: start should be `(page - 1) * page_size` for
  1-indexed pages; current code skips the first page entirely (page=1
  returns `items[size:2*size]`).

**Config A — Single Agent** (recall=1.00, precision=0.86, redundancy=0,
relevance=5)

> 1. **Logic Bug**: `paginate` function, line 6 — The pagination logic is
>    incorrect for 1-indexed pages. The calculation for `start` should be
>    `(page - 1) * page_size`.
> 2. **Logic Bug**: `page_count` function, line 10 — converts `items` to a
>    list via `list(items)`, consuming the iterable; subsequent calls
>    misbehave on generators.
> 3. **Style Problem**: `paginate` — docstring should specify 1-indexed
>    semantics and out-of-range behaviour.
> 4. **Style Problem**: `page_count` missing docstring.
> 5. **Type Hinting Issue**: `items: Iterable[T]` is misleading given the
>    body converts to a list.
> 6. **Performance Issue**: `len(list(items))` materialises the entire
>    iterable.
> 7. **Security note**: validate `page` and `page_size` to prevent
>    pathological inputs.

**Config B — Sequential Multi-Agent** (recall=1.00, precision=0.50,
redundancy=3, relevance=3)

> *logic_reviewer*
> 1. Off-by-one in `start`; should be `(page - 1) * page_size`.
> 2. `list(items)` consumes the iterable.
> 3. No validation for `page <= 0`.
>
> *security_reviewer*
> 1. **Injection Vulnerability** in `paginate` — *invalid claim*.
> 2. **Insecure Deserialization** in `page_count` — *invalid claim*.
> 3. **Path Traversal** in `paginate` — *invalid claim*.
>
> *style_reviewer*
> 1. Rename `page_size` to `items_per_page`.
> 2. `+ page_size - 1` is a magic expression.
> 3. Single Responsibility violation in `page_count`.
> 4. No error handling in `paginate`. *(truncated by max_tokens)*

**Config C — Parallel Multi-Agent** (recall=1.00, precision=0.67,
redundancy=0, relevance=4)

> *Merged and unified*
> 1. Off-by-one error in `paginate`.
> 2. `page_count` consumes the iterable.
> 3. Potential index error — *(truncated by max_tokens)*

**What this example actually shows.** All three configs identified the
canonical off-by-one. Config A also raised six additional valid concerns
without redundancy. Config B's specialist roles induced **hallucinated
vulnerabilities** (injection, insecure deserialization, path traversal —
none applicable to pure pagination code); the security specialist felt
obliged to find security issues even when none existed. Config C's
aggregator suppressed B's redundancy but also discarded most of the
specialist content because of its own 150-token cap; the third bullet
got cut off mid-sentence.

#### "Single-agent clearly won" — sample `S9` (security)

Recall by config: A=1.00, B=0.50, C=0.50

**Code under review**

```python
import requests


def fetch_user_avatar(image_url: str) -> bytes:
    """Download a user-supplied avatar URL and return the image bytes."""
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()
    return response.content


def save_avatar_for(user_id: int, image_url: str, store) -> None:
    data = fetch_user_avatar(image_url)
    store.put(f"avatars/{user_id}.png", data)
```

**Canonical known issues**

- SSRF: unvalidated user-supplied URL can be pointed at internal services.
- No content-type or size limit: a malicious URL can return arbitrary
  bytes that the store persists under a `.png` extension.

**Config A — Single Agent** (recall=1.00, precision=0.50, redundancy=0,
relevance=3): identified the SSRF, also caught the hardcoded `.png`
extension issue (which corresponds to the "no content-type" canonical
issue), plus several adjacent points (lack of `user_id` validation,
missing logging, no graceful exception handling).

**Config B — Sequential Multi-Agent** (recall=0.50, precision=0.50,
redundancy=2, relevance=3): security specialist caught the SSRF but
missed the content-type issue. The logic specialist hallucinated a
"mutable default argument" warning for a parameter that has no default
value at all.

**Config C — Parallel Multi-Agent** (recall=0.50, precision=0.33,
redundancy=0, relevance=3): aggregator surfaced SSRF and a generic
"input validation" point, but the aggregator's 150-token budget
truncated the specialist findings before the content-type issue could
be preserved.

**What this example actually shows.** Both multi-agent configs caught
50% of the canonical issues; A caught 100%. The content-type/size issue
crosses domain boundaries (security ↔ defensive coding), and the
specialist role-restrictions prevented any one specialist from owning
it. The single-agent prompt — which asks for "all issues including
logic, security, and style" — has no such territorial constraint.

#### "All configs tied" — sample `L1` (logic)

(Duplicated by the auto-picker; identical content to the first example.)

### 4b. Honest re-pick — best evidence for "multi loses on style"

The picker reused `L1` because no genuine "multi wins" sample exists.
For the paper, a better Single-Agent-wins example is **ST3** or **ST6**:
both samples show Config C dropping to **recall = 0.00** while A and B
hit 1.00. These samples are diffuse-style cases where a 150-token
specialist could not enumerate the relevant issues and the 150-token
aggregator dropped what little remained.

---

## 5. Agent Prompts Used

These are the exact strings used at run time. Reproduced verbatim from
`configs/single_agent.py`, `configs/sequential_multi.py`,
`configs/parallel_multi.py`, and `evaluation/judge.py`.

### 5.1 Config A — Single Agent system prompt

```
You are an expert code reviewer. Review the provided code thoroughly. Identify all issues including logic bugs, security vulnerabilities, and style problems. For each issue: state the issue type, the line or area affected, and a brief explanation. Be concise. Format: numbered list.
```

User message: the raw code, no wrapper.

### 5.2 Config B — Sequential Multi-Agent system prompts

**Agent 1 — Logic Reviewer**

```
You are a senior software engineer reviewing code SPECIFICALLY for LOGIC and CORRECTNESS issues only. Examples: off-by-one errors, wrong conditionals, missing edge cases, incorrect return values, mutable default arguments, closure-capture bugs. Do NOT comment on security or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Agent 2 — Security Reviewer**

```
You are a senior application security engineer reviewing code SPECIFICALLY for SECURITY vulnerabilities only. Examples: injection, insecure deserialization, weak crypto, hardcoded secrets, SSRF, path traversal, XSS. Do NOT comment on general logic bugs or style. You may reference Agent 1's logic findings to avoid duplication, but only report security issues. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Agent 3 — Style Reviewer**

```
You are a senior software engineer reviewing code SPECIFICALLY for STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor naming, magic numbers, deep nesting, missing error handling, DRY violations, inconsistent return types, single-responsibility violations. Do NOT re-report logic or security issues already raised by previous agents. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Config B user-prompt template (each agent):**

```
CODE UNDER REVIEW:
```python
<code>
```

PREVIOUS REVIEW — <role>:
<text>
... (one block per prior reviewer)
```

### 5.3 Config C — Parallel Multi-Agent system prompts

**Agent 1 — Logic Reviewer** (identical role wording to B, but without
"reference previous findings"):

```
You are a senior software engineer reviewing code SPECIFICALLY for LOGIC and CORRECTNESS issues only. Examples: off-by-one errors, wrong conditionals, missing edge cases, incorrect return values, mutable default arguments, closure-capture bugs. Do NOT comment on security or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Agent 2 — Security Reviewer**

```
You are a senior application security engineer reviewing code SPECIFICALLY for SECURITY vulnerabilities only. Examples: injection, insecure deserialization, weak crypto, hardcoded secrets, SSRF, path traversal, XSS. Do NOT comment on general logic bugs or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Agent 3 — Style Reviewer**

```
You are a senior software engineer reviewing code SPECIFICALLY for STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor naming, magic numbers, deep nesting, missing error handling, DRY violations, inconsistent return types, single-responsibility violations. Do NOT comment on logic or security issues. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
```

**Aggregator (4th agent)**

```
You are a senior code review coordinator. You have received three independent reviews of the same code from specialist agents. Your job is to:
1. Merge their findings, removing exact duplicates
2. Resolve any contradictions
3. Output a clean, unified numbered list of all unique issues found
Be concise. Do not add new issues not mentioned by the specialists.
```

**Config C specialist user template:**

```
CODE UNDER REVIEW:
```python
<code>
```
```

**Config C aggregator user template:**

```
CODE UNDER REVIEW:
```python
<code>
```

REVIEW — logic_reviewer:
<text>

REVIEW — security_reviewer:
<text>

REVIEW — style_reviewer:
<text>
```

### 5.4 Judge system prompt

```
You are a careful, impartial reviewer judging the quality of a code review. You will be given (a) source code, (b) a canonical list of known issues in that code, and (c) a review produced by another system.

Score the review on four dimensions and return ONLY a single valid JSON object with these keys:
  recall_score:     float in [0.0, 1.0] — fraction of canonical known issues the review identifies (a near-paraphrase counts).
  precision_score:  float in [0.0, 1.0] — fraction of distinct issues raised by the review that are valid real problems in the code (whether or not they appear in the canonical list).
  redundancy_count: integer >= 0 — count of duplicate or near-duplicate points within the review (e.g. the same SQL injection raised twice).
  relevance_score:  integer in {1,2,3,4,5} — overall quality of the review as a holistic code-review artifact.
  reasoning:        one short sentence justifying the scores.

Do not output markdown, code fences, or any text outside the JSON object.
```

Judge runs at `temperature=0.0`, `max_tokens=400`, and
`response_format={"type": "json_object"}`.

---

## 6. Key Findings

1. **The "multi-agent always wins" hypothesis fails under budget control.**
   On 30/30 samples, multi-agent recall is ≤ single-agent recall. There is
   not a single sample on which B or C beats A on recall.
2. **Logic and security are saturated.** Across 19/20 logic+security
   samples all three configs hit recall = 1.00. The 600-token budget is
   ample for clearly-bounded defects and the agents (gpt-4o-mini) are
   already strong at them.
3. **Style is where the architecture matters — and where multi-agent
   loses.** Style recall: A = 95.0%, B = 86.7%, C = **46.7%**.
   Parallel-plus-aggregator drops Config-C recall by more than half
   because (i) each 150-token specialist can only enumerate a few items
   and (ii) the 150-token aggregator further compresses, dropping items
   the specialists raised. Style issues are diffuse and don't fit neatly
   into the Logic/Security/Style trichotomy the multi-agent prompts
   impose.
4. **Specialisation buys precision but only in Config C.** Mean
   precision: A = 48.0%, B = 48.1%, C = 55.0%. The Config-C aggregator
   acts as a quality filter on specialist output; B has no equivalent
   filter, so its three role-restricted agents stack false positives
   (most notably security hallucinations on non-security code).
5. **Sequential context-sharing does not deduplicate.** Despite explicit
   "do not duplicate prior findings" instructions, Config B's mean
   redundancy is **1.73**, nearly 9× Config A's 0.20 and ~6× Config C's
   0.30. Specialists tend to re-cover earlier ground at the boundaries
   of their role definitions.
6. **The budget multiplier in input tokens is the hidden cost.** Output
   tokens are equal by construction. Input tokens are ~7× higher in B
   and ~7.5× higher in C. Total tokens used (in + out) are nearly 3× A
   for both multi-agent configs. Multi-agent isn't just "no better" —
   it's "no better at substantially higher real cost."

---

## 7. Surprises & Anomalies

- **No multi-agent wins at all.** The result is not "multi-agent wins
  slightly less than expected"; it is "multi-agent never wins on any
  individual sample on recall." Even on samples where one would expect
  the specialist framing to help (e.g. ST7, a sample where every config
  scores 0.50), the configurations tie rather than separate.
- **The qualitative-example picker degenerated.** The `pick_qualitative_examples`
  function in `run_experiment.py` picks the sample with the largest value
  of `max(recall_B, recall_C) - recall_A` as "multi-agent clearly won."
  Because no sample has a positive value (the maximum is 0, achieved on
  every tie-at-1.00 sample), the picker selected `L1` — the first such
  sample — and labelled it "multi-agent clearly won." The label is
  artefactual; the example is actually a 3-way tie. A more truthful
  output would have stated "no sample with multi-agent recall lead." The
  saved file `results/qualitative_examples.md` contains this artefact
  verbatim. The honest re-pick in §4b above describes ST3 / ST6 as the
  best examples of the real pattern.
- **The security specialist hallucinated security issues on non-security
  code.** In sample `L1` (a pure pagination function), the Config-B
  security specialist raised "injection vulnerability," "insecure
  deserialization," and "path traversal." This is the role's
  *instruction-following* hurting precision: told to find security
  bugs and given no exit clause, it produced security-shaped
  speculation. Several Config-B reviews show the same pattern.
- **Truncation by `max_tokens` is visible in the reviews.** Multiple
  Config-B and Config-C outputs (notably L1 and S9 above) end
  mid-sentence because the 150–200-token budgets per role are not enough
  to enumerate findings politely. The judge appears to score truncated
  reviews charitably (assigning credit if the partial point is
  recognisable), but a paper should note that the per-role budget for
  this experimental design may be at the painful end of viable.
- **Logic recall ceiling.** All three configs achieve 100% logic recall.
  This suggests either (i) the logic samples are too easy for the
  experimental design to discriminate, or (ii) gpt-4o-mini is at
  ceiling on this class of bug. A future replication should include
  harder logic samples (e.g. concurrency races, subtle aliasing bugs)
  to widen the dynamic range.
- **Judge agreement is uniformly high.** No judge parse errors occurred
  across 90 calls. No judge call produced an obviously wild score; all
  scores fell within their declared ranges. This is encouraging for
  the judge-as-evaluator approach.

---

## 8. Limitations

1. **N = 30 is small.** Differences in means should be reported with
   confidence intervals (paired bootstrap or Wilcoxon signed-rank are
   appropriate given paired per-sample structure). The per-sample
   judge scores are preserved in `results/raw_outputs.json`, so any
   such test can be run post-hoc.
2. **Single language (Python), single domain (single-function
   snippets).** Findings may not transfer to long-context, multi-file
   review or to languages with different idioms (Rust ownership,
   JavaScript event loops, Go concurrency).
3. **Single judge model.** GPT-4o judging GPT-4o-mini outputs is an
   in-family evaluation. Cross-family judging (e.g. Claude as judge,
   or human raters) would be a stronger robustness check.
4. **Single token budget.** 600 output tokens is one operating point.
   At much larger budgets the multi-agent split may stop being
   painful; at much smaller budgets the gap may widen. A budget-sweep
   experiment is left to future work.
5. **No iteration, no tools, no retrieval.** All configurations issue a
   single forward pass per agent. Real production systems often use
   multi-turn refinement, retrieval over codebase context, or tool calls
   (e.g. static analysers). The conclusions speak only to the
   "single forward pass" regime.
6. **Dataset construction bias.** Snippets were written knowing that
   LLMs would later be asked to find planted issues — a selection bias
   toward LLM-detectable bugs. Issues that require runtime evidence
   (numerical instability, concurrency races) were not included.
7. **Category boundaries map onto specialist roles.** The
   logic/security/style trichotomy in the dataset is *exactly* the
   trichotomy used for specialists in B and C. This is the most
   favourable design for role-specialisation; in real reviews categories
   blur and a single defect may have logic, security, and style
   components.

---

## 9. Cost Summary

- **Agent calls (gpt-4o-mini at $0.15 / $0.60 per 1M tokens in / out):**
  - Config A: $0.00855 for 30 samples
  - Config B: $0.014881 for 30 samples
  - Config C: $0.015745 for 30 samples
  - **Subtotal: $0.0392** for all 90 agent pipelines.
- **Judge calls (gpt-4o at $2.50 / $10.00 per 1M tokens in / out):**
  - 72,231 input tokens + 6,435 output tokens across 90 calls
  - **Subtotal: $0.2449.**
- **Total experiment cost: ≈ $0.28** for the full 30-sample, 3-config,
  judge-included run. Costs are inferred from logged `usage` fields on
  every API response; not estimated.

---

## 10. File Inventory

Paths are relative to the repository root.

- `prompt1_experiment.md` — Original experiment-design brief from the
  PI, defining the three configurations, budget, dataset categories,
  judge metrics, and required deliverables.
- `prompt2a_harvester.md` — The harvester prompt that produced this
  document.
- `.gitignore` — Excludes `.env`, `__pycache__/`, `*.pyc`, `.DS_Store`,
  `.venv/`, `venv/`, `*.egg-info/`.
- `code_review_experiment/README.md` — Methodology document
  (academic-adjacent prose) covering budget control, configuration
  hypotheses, model selection, dataset construction bias, and
  experiment limitations. Source material for the paper's Methodology
  section.
- `code_review_experiment/.gitignore` — Subdir-level gitignore (mirrors
  the top-level one; ensures `.env` cannot be committed).
- `code_review_experiment/.env.example` — Template for the API-key
  environment file. The runtime `.env` is gitignored.
- `code_review_experiment/run_experiment.py` — Master orchestrator.
  Loads `.env`, runs all configs over all samples (serially, with
  per-sample persistence to `raw_outputs.json`), then runs the judge
  on every output, then aggregates metrics, then emits the comparison
  table and qualitative examples. Supports `--limit N`, `--skip-run`,
  `--skip-judge`.
- `code_review_experiment/dataset/build_samples.py` — Generator script
  that builds `samples.json` from triple-quoted inline Python snippets.
  Enforces 10–40-line bounds and the 10/10/10 category split.
- `code_review_experiment/dataset/samples.json` — The 30-sample dataset
  (id, category, code, known_issues per sample). Committed for
  reproducibility.
- `code_review_experiment/configs/__init__.py` — Marks `configs/` as a
  package.
- `code_review_experiment/configs/_common.py` — Shared infrastructure:
  pinned model IDs (`gpt-4o-mini`, `gpt-4o`), pricing constants,
  `AgentCall` and `ConfigResult` dataclasses, sync + async OpenAI
  client constructors, `call_chat` and `call_chat_async` helpers that
  log every call's `usage` fields and capture exceptions instead of
  raising.
- `code_review_experiment/configs/single_agent.py` — Config A
  implementation: one `gpt-4o-mini` call, 600-token budget, returns a
  `ConfigResult`.
- `code_review_experiment/configs/sequential_multi.py` — Config B
  implementation: three specialists in sequence (Logic → Security →
  Style), each at 200-token budget, each seeing original code + all
  prior reviews, instructed not to duplicate prior findings. Final
  output is the concatenation of all three specialist sections.
- `code_review_experiment/configs/parallel_multi.py` — Config C
  implementation: three specialists run concurrently via
  `asyncio.gather` (150 tokens each), then a fourth Aggregator agent
  (150 tokens) merges their findings. Final output is the
  aggregator's text.
- `code_review_experiment/evaluation/__init__.py` — Marks `evaluation/`
  as a package.
- `code_review_experiment/evaluation/judge.py` — GPT-4o judge.
  Implements defensive JSON extraction (handles bare JSON, fenced
  JSON, and trailing-commentary JSON), score clamping, and per-call
  token logging. Always returns a `JudgeScore` even on API failure.
- `code_review_experiment/results/raw_outputs.json` — Per-sample,
  per-config agent outputs with per-call token counts and judge scores
  (recall, precision, redundancy, relevance, reasoning, plus the
  judge's raw response text for auditability).
- `code_review_experiment/results/metrics.json` — Aggregated metrics
  per config and per (config, category). Includes mean recall,
  precision, redundancy, relevance; total/mean token counts;
  estimated agent-only cost; error counts.
- `code_review_experiment/results/comparison_table.md` — The headline
  table reproduced in §3 of this document.
- `code_review_experiment/results/qualitative_examples.md` — Three
  qualitative case studies emitted by the master runner. (Caveat:
  the "multi-agent clearly won" pick is artefactual; see §7.)
- `code_review_experiment/results/run.log` — Captured stdout from the
  full 30-sample run; contains per-sample run-phase and judge-phase
  progress lines and the final printed comparison table.
- `code_review_experiment/.env` — Contains the OpenAI API key used at
  run time. Gitignored — never committed to the repository.

---

*End of paper_context.md.*
