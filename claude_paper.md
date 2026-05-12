# Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review: A Controlled Comparison Under Equal Token Budgets

**Abstract**

The architectural choice between a single generalist LLM agent and a role-specialized multi-agent system is a key design decision in automated code review, since it determines defect coverage, review noise, and per-pull-request inference cost at scale. Practically such choices are frequently made on the basis of analogy with human review teams or on the headline numbers of benchmark papers, without a controlled comparison in which the total inference budget is held constant across architectures. This paper presents a controlled comparison of three code-review configurations based on `gpt-4o-mini` under an enforced 600-token output budget per sample: a single generalist agent (Config A), a sequential pipeline of role-specialized agents (Config B), and a parallel pipeline of role-specialized agents with an aggregator (Config C). The framework uses a combination of two hand-curated inputs: a 30-sample Python dataset with author-written canonical issue lists (10 logic / 10 security / 10 style snippets, 10–22 lines each), and a GPT-4o-as-judge scorer that grades every review on recall, precision, redundancy, and holistic relevance. Findings across the 30 samples indicate that role specialization did not improve recall under matched output-token budgets: the GPT-4o judge assigned a mean recall of 0.983 to Config A, 0.939 to Config B, and 0.806 to Config C, and on no individual sample did either multi-agent configuration exceed the single agent on recall. Config B exhibited a mean redundancy of 1.733 against Config A's 0.200 — nearly nine times higher despite each downstream specialist being explicitly instructed not to duplicate prior findings — and Config C gained 7 percentage points of mean precision over Config A (0.550 against 0.480) at a 17.7-percentage-point cost in mean recall. The paper generalizes the equal-budget critique of multi-agent systems from multi-hop reasoning (Tran and Kiela, 2025) to the code-review setting, through paired per-sample evaluation of three architectures under a fixed output-token budget.

**Keywords:** large language models, multi-agent systems, code review, software engineering automation, token budget, role specialization, GPT-4o-mini

---

## 1. Introduction

The issue of code review is a key activity in modern software engineering pipelines, and increasingly a host for LLM-based agents. What began as autocomplete assistance in editors has expanded into autonomous agents that draft code, write tests, generate pull-request descriptions, triage bugs, and review code before it is merged (Yang et al., 2024). The decision of how to architect such a reviewer — as a single generalist call to a model, or as a coordinated team of role-specialized agents — influences which defects the system catches, how much noise it adds to a pull-request thread, the developer trust the system accumulates over time, and how much an organization pays per review at the scale of an engineering team.

In the rapidly expanding ecosystem of LLM-assisted developer tools, where a new agent framework appears every few weeks and production teams are pushed to adopt one before they have validated it, this architectural choice has real consequences. Nonetheless, in most production deployments the choice is made without controlled empirical evidence and is instead made by analogy with human review teams — a security engineer, a senior developer, a QA reviewer — or by reference to benchmark papers whose compute envelopes were not held constant across the architectures being compared.

Meanwhile, a clean empirical method for adjudicating the question has been articulated in the broader LLM literature but has not yet been applied to code review. Tran and Kiela (2025) demonstrated on multi-hop reasoning benchmarks that the observed performance advantages of multi-agent systems over single-agent baselines largely dissolve when output token budgets are equalized across architectures. Their account attributes the apparent multi-agent advantage to disproportionately larger compute expenditure rather than to architectural innovation per se: each inter-agent compression step, in which the rich internal reasoning of one agent is collapsed into a natural-language summary that the next must re-interpret, introduces potential signal loss that a single unmediated forward pass does not face. In a closely related software-engineering setting, Yang et al. (2024) report that the design of the Agent-Computer Interface in SWE-agent — the linearity and completeness of the agent's interaction history with the codebase — was more predictive of task performance on SWE-bench than the addition of multiple specialized agent roles.

Code review is a natural setting in which to revisit this question for software engineering specifically. Reviews are bounded in scope, are evaluable against a ground-truth list of defects, and decompose along (logic / security / style) lines that map directly onto the role boundaries multi-agent architectures typically impose. If role specialization is going to help anywhere, it ought to help here. Yet the question of whether it actually does — under an equal-budget control — has not been answered in this setting.

Based on this, the research question guiding the present work is: *Given a fixed output-token budget per sample, does role-specialized multi-agent code review (sequential or parallel-plus-aggregator) produce better reviews than a single generalist agent operating under the same budget?* The framing is methodologically deliberate. A multi-agent system that issues four LLM calls and generates 1,800 total output tokens is not cleanly comparable, on the architectural question, to a single agent generating 600 tokens — any observed difference is jointly attributable to topology and to compute. We hold output tokens constant to isolate the architectural contribution from the compute contribution.

Based on these observations, this paper makes the following contributions. We design a controlled experimental methodology that enforces an equal 600-token output budget per sample across three architectures and verifies compliance against logged `usage.completion_tokens` on every API call. We test the methodology on a hand-curated 30-sample Python dataset stratified into three categories of defect, with author-written canonical issue lists serving as the recall ground truth. We report that across all 30 samples and both multi-agent architectures, no multi-agent configuration achieved a recall advantage over the single agent on any individual sample, and that the aggregate recall gap was concentrated entirely in style/maintainability defects. We characterize the specific failure modes responsible — role-restriction hallucination in the sequential pipeline, aggregator compression loss in the parallel-plus-aggregator pipeline, and the failure of prompted deduplication to suppress sequential redundancy. We report a cost analysis showing that the single agent cost approximately 45% less per sample than either multi-agent configuration while delivering higher recall.

The rest of this paper is organized in the following way. Section 2 reviews related work on multi-agent systems for software engineering, on the single-versus-multi-agent debate, and on LLM-as-judge evaluation. Section 3 describes the experimental design. Section 4 reports quantitative and qualitative results. Section 5 discusses the mechanisms behind the results and their practical implications. Section 6 addresses limitations and future directions. Section 7 concludes.

---

## 2. Related Work

### 2.1 Multi-Agent Systems for Software Engineering

Multi-agent systems for software engineering have been widely explored across code generation, repository-level engineering, and reviewing tasks. The seminal ChatDev framework (Qian et al., 2024) organized multiple LLM agents into structured corporate roles — Chief Executive Officer, Chief Technology Officer, programmer, reviewer, and tester — and coordinated them through formatted chat turns to automate the full software development lifecycle, lending influential empirical support to the premise that specialization and structured communication enhance LLM output quality.

Subsequent work elaborated this premise at greater architectural scale. Phan et al. (2024) present HyperAgent, a four-agent pipeline (Planner, Navigator, Code Editor, Executor) that decomposes repository-level engineering tasks into specialized subtasks and achieved state-of-the-art results on SWE-bench at the time of publication, showing that specialization of subtask responsibility could yield measurable improvements on complex, multi-step engineering challenges. Khanzadeh (2025) extends the pattern in AgentMesh, a layered cooperative framework in which agents at different hierarchical levels communicate via structured protocols and which the author argues scales to multi-repository settings.

In this landscape, Chen (2025) proposed AutoReview, a three-agent architecture specialized for security-oriented code review at FSE 2025, arguing that dedicating separate model instances to vulnerability identification enables deeper analytical penetration than a single generalist prompt scanning for all issue types simultaneously. AutoReview is the closest prior work to ours in problem framing, though it does not hold the per-system inference budget constant across the architectures it compares — so the contribution of architectural specialization in its reported numbers cannot be cleanly separated from raw compute expenditure.

### 2.2 Challenges to Multi-Agent Superiority

The advent of equal-budget benchmarking has provided a new line of inquiry into agent comparisons. Tran and Kiela (2025) conducted controlled experiments on multi-hop reasoning tasks and report that when output token budgets — the tokens devoted to generation, or "thinking tokens" — are equalized across single-agent and multi-agent configurations, single agents consistently match or outperform multi-agent equivalents. The authors attribute this finding to the fact that a single agent retains direct, unmediated access to the full task representation at every generation step, whereas inter-agent communication necessarily involves compressing rich internal reasoning into natural-language summaries that the next agent must re-interpret. Each compression and re-expansion step introduces potential for signal loss, misinterpretation, and drift from the original task specification.

Yang et al. (2024) provide complementary evidence from the software engineering domain. SWE-agent's primary contribution was the design of an Agent-Computer Interface that enables fluid interaction between a single LLM and a software repository. The authors report that the quality of the interface — the linearity and completeness of the agent's context history — was more predictive of performance than the addition of multiple specialized agent roles, and that minimal single-agent implementations leveraging clean linear histories frequently matched or exceeded multi-agent baselines.

Dong et al. (2025) document an additional risk specific to role-restricted reviewing. LLM agents prompted to adopt fixed reviewer roles are susceptible to role-anchored confirmation bias: a security-designated agent, instructed to find vulnerabilities and given example vulnerability patterns, tends to find security-shaped artifacts even in code where no genuine vulnerabilities exist. This hallucination-by-role-pressure dynamic is a structural risk in multi-agent code-review pipelines that single-agent generalist prompts do not face in the same way — we return to it in Section 5.

Although such systems demonstrate the worth of multi-agent decomposition in complex software engineering problems, none of them have been compared to single-agent baselines under an equal output-token budget in the code-review setting specifically. The current work expands the equal-budget paradigm of Tran and Kiela (2025) to LLM-based code review and addresses a gap that the surveyed literature has not yet resolved.

### 2.3 LLM-as-Judge Evaluation

Evaluating the quality of open-ended generated text — including code reviews — presents methodological challenges that simple automated metrics cannot resolve. Human annotation is costly and subject to inter-rater variability; traditional NLP metrics such as BLEU and ROUGE are inadequate for evaluating analytical depth against a semantic ground truth. Zheng et al. (2023) describe the LLM-as-judge paradigm and report that, against human pairwise preferences on Chatbot Arena and MT-bench, a strong LLM (GPT-4) agreed with the majority human verdict at a rate comparable to human-human agreement. The paradigm is well suited to code-review evaluation: the judge sees the source code, the canonical known-issue list, and the review under evaluation, and is asked to score recall, precision, redundancy, and holistic relevance against a structured rubric. We use GPT-4o as judge for reviews produced by `gpt-4o-mini`; known concerns about in-family bias and rubric sensitivity are addressed in Section 6.

---

## 3. Methodology

### 3.1 Research Question and Pre-Registered Hypothesis

This section formalizes the experimental design as a paired-architectures, fixed-budget comparison and defines the inputs, configurations, and evaluation operations underlying the framework.

The research question motivating the study has been stated in Section 1 and is repeated here for reference: *Given a fixed output-token budget per sample, does role-specialized multi-agent code review (sequential or parallel with aggregator) produce better reviews than a single generalist agent operating under the same budget?*

The framing is methodologically significant. The dominant prior claim — that multi-agent systems produce better code reviews — has almost universally been tested without controlling for computational resources. A multi-agent system that issues four LLM calls and generates 1,800 total output tokens is not directly comparable, architecturally, to a single agent generating 600 tokens; any performance advantage in such comparisons is jointly attributable to topology and to the simple fact of more compute. The present design holds output-token budget constant to isolate the architectural contribution.

The hypothesis, pre-registered and framed as the multi-agent claim under test, was: role-specialized multi-agent review (Configs B and C) will produce higher recall and lower redundancy than a single generalist agent (Config A) at the same total output-token budget, because (i) focused-role prompts admit denser, less hedged reviews per role, and (ii) explicit deduplication — sequential context-sharing in B or an aggregator in C — should keep the final output clean.

### 3.2 Dataset Construction

The empirical basis consists of a hand-authored 30-sample Python dataset, constructed in lieu of drawing on a pre-existing benchmark. Existing benchmarks such as SWE-bench consist of real-world pull requests and issues where the ground truth is a merged patch or a discussion thread, which makes precise recall measurement against a fixed issue list impractical. We did not draw on those benchmarks because the experimental control we required — a closed, author-written list of canonical issues per sample, against which recall can be scored without judge-side speculation — is not present in them. The implications of this choice for external validity are discussed in Section 6.

Each snippet is 10 to 22 lines long and represents a self-contained function or pair of functions. The 30 samples are stratified into three equal categories of ten.

Logic bugs (samples L1–L10) include an off-by-one error in 1-indexed pagination, a moving-average loop that misses its final window, a median function that does not handle empty input, the mutable-default-argument trap on a logging helper, integer floor-division on what should be a floating-point mean, the late-binding closure pattern in a list of lambdas, an inverted privilege check enabling escalation, a missing recursive base case in `factorial(0)`, naive comma-splitting on CSV with quoted fields, and float equality on monetary values.

Security vulnerabilities (S1–S10) include SQL injection via f-string formatting, hardcoded production credentials, `pickle.loads` deserialization on a cookie-supplied blob, path traversal via unsanitized user-supplied filenames, use of the `random` module (Mersenne Twister) for password-reset tokens, command injection via `subprocess` with `shell=True`, stored cross-site scripting in an HTML rendering helper, MD5 password hashing paired with a non-constant-time comparison, server-side request forgery (SSRF) on a user-supplied URL, and `eval()` on user input.

Style and maintainability defects (ST1–ST10) include five-level nested conditional structures, missing error handling around `json.loads`, single-letter parameter names paired with magic tax-rate constants, password-strength validation relying solely on length, missing input validation combined with a non-atomic financial transfer, a DRY violation across three near-identical rendering functions, a signup handler violating the Single Responsibility Principle across five concerns, bare `except` clauses, a module-level mutable cache with no invalidation, and a function with inconsistent return types yielding `User`, `False`, or `None` depending on the code path.

Each sample carries one to three canonical issues in its `known_issues` list. Several samples carry multiple known issues, which makes recall scoring more discriminating than a one-issue-per-sample design would be.

### 3.3 Experimental Configurations

All agent calls use `gpt-4o-mini` as the base model. The three configurations differ in topology and in the way they partition a shared 600-token output budget across calls.

**Config A — Single Generalist Agent.** One LLM call per sample with a system prompt asking the model to produce a numbered list of logic, security, and style issues. The user message is the raw source code with no additional framing. The full 600-token output budget is available to this single call. The system prompt is reproduced in full in Appendix A.

**Config B — Sequential Multi-Agent.** Three role-specialized agents execute in a fixed order: Logic Reviewer → Security Reviewer → Style Reviewer. Each agent receives the original source code and the verbatim text of all preceding reviews, and is explicitly instructed not to duplicate findings already raised. The 600-token budget is split equally at 200 tokens per agent. The artifact passed to the judge is the concatenation of the three specialist sections. The sequential structure is intended to enable deduplication through shared context.

**Config C — Parallel Multi-Agent with Aggregator.** Three role-specialized agents — with the same role definitions as Config B's specialists — execute independently and concurrently via `asyncio.gather`. They cannot deduplicate against one another because they cannot see one another's outputs at generation time. A fourth Aggregator agent then receives the original code and all three specialist reviews and is instructed to merge their findings into a unified, deduplicated numbered list. The 600-token budget is split as 150 tokens to each specialist and 150 tokens to the Aggregator. The Aggregator's output is the artifact passed to the judge.

All agent calls run at `temperature=0.2` — low enough to keep output focused but non-zero, so that the three Config C specialists do not produce literally identical text, which would inflate the redundancy metric artifactually. We did not tune sampling temperature further because the task is structured rather than open-ended and the prompts request a numbered-list output format. The implications of this choice are discussed in Section 6.

### 3.4 Token Budget Enforcement and Verification

The `max_tokens` parameter on each API call sets the per-call cap (600 for A; 200, 200, 200 for B; 150, 150, 150, 150 for C). Every API response carries a `usage.completion_tokens` field, which the harness logs for every call and aggregates after the run.

Across all 30 samples and all configurations, no individual API call exceeded its assigned cap on any call. Mean output tokens were 434.7 for Config A (against a 600-token cap), a total of 538.1 across the three Config B specialists per sample (an average of 179.4 per specialist call against a 200-token cap), and a total of 569.1 across the three Config C specialists plus the Aggregator (an average of 142.3 per call against a 150-token cap). The experiment therefore confirms budget compliance at the per-call level.

Input tokens are not equalized across configurations and we did not attempt to equalize them. Config B agents must read prior reviews in addition to the source code; Config C's Aggregator must read all three specialist outputs. This is a structural property of the architectures, not an experimental artifact: any real deployment of either multi-agent design incurs this input overhead. We report input, output, and total tokens separately so that the asymmetry remains visible to the reader.

### 3.5 Evaluation Protocol

Each of the 30 × 3 = 90 (sample, configuration) pairs is scored by a GPT-4o judge. The judge receives three inputs: (1) the original source code, (2) the canonical `known_issues` list for that sample, and (3) the final review text produced by the configuration under evaluation. The judge returns a structured JSON object with four scored dimensions and a one-sentence reasoning trace:

- `recall_score` as a float in [0.0, 1.0]: the fraction of canonical known issues the review identifies, where near-paraphrases count as identifications.
- `precision_score` as a float in [0.0, 1.0]: the fraction of distinct issues raised in the review that are valid real problems in the code, whether or not they appear in the canonical list.
- `redundancy_count` as a non-negative integer: the count of duplicate or near-duplicate points within the review.
- `relevance_score` as an integer in {1, 2, 3, 4, 5}: a holistic rating of the review as a code-review artifact.

The judge is explicitly instructed to count near-paraphrases as recall hits, so that stylistic variation in how an issue is described does not artifactually penalize the recall score. Judge calls run at `temperature=0.0`, `max_tokens=400`, and `response_format={"type": "json_object"}` to enforce structured output. The harness defensively extracts the JSON object from the response (handling cases where the judge wraps it in markdown fences or appends trailing commentary), clamps each scored field into its expected range, and treats parse failures as scoring failures. Across all 90 judge calls in the reported run, zero parse errors occurred.

---

## 4. Results

### 4.1 Run Reliability

All 90 agent pipelines and all 90 judge evaluations completed without runtime errors or response-parsing failures. The result matrix is complete; the analyses below are not subject to attrition bias.

### 4.2 Aggregate Performance Metrics

Table 1 reports aggregate performance metrics across all 30 samples for each configuration.

| Metric | Config A (Single) | Config B (Sequential) | Config C (Parallel) |
|---|---|---|---|
| Mean Recall | 0.983 | 0.939 | 0.806 |
| Mean Precision | 0.480 | 0.481 | 0.550 |
| Mean Redundancy | 0.200 | 1.733 | 0.300 |
| Mean Relevance | 3.100 | 2.933 | 3.133 |
| Mean Total Tokens | 595.9 | 1,692.6 | 1,791.6 |
| Est. Cost (30 samples) | $0.0086 | $0.0149 | $0.0157 |

*Table 1. Aggregate metrics across configurations. Token budget: 600 output tokens per sample. Costs cover agent calls only (`gpt-4o-mini` at $0.15 / $0.60 per million tokens in / out) and exclude judge tokens.*

Three patterns are visible at the aggregate level. The GPT-4o judge assigned a mean recall of 0.983 to Config A, 0.939 to Config B, and 0.806 to Config C — a separation of 4.4 percentage points between A and B and 17.7 percentage points between A and C. Config A also received the lowest mean redundancy (0.200) — about a factor of nine below Config B (1.733) and a factor of about one and a half below Config C (0.300). Config C received the highest mean precision (0.550), a 7-point lift over Configs A and B (0.480 and 0.481 respectively), and a marginally higher mean relevance score (3.133 against 3.100 and 2.933 on the 1–5 scale).

### 4.3 Token Usage and Cost Breakdown

Equalizing output tokens does not equalize total compute. Table 2 reports the full token breakdown by configuration.

| Config | Mean Tokens In | Mean Tokens Out | Mean Total | Σ In (30 samples) | Σ Out (30 samples) | Cost (30 samples) |
|---|---|---|---|---|---|---|
| A | 161.2 | 434.7 | 595.9 | 4,837 | 13,041 | $0.00855 |
| B | 1,154.5 | 538.1 | 1,692.6 | 34,636 | 16,142 | $0.01488 |
| C | 1,222.5 | 569.1 | 1,791.6 | 36,676 | 17,072 | $0.01575 |

*Table 2. Token usage and cost by configuration. Input tokens are not equalized by design; multi-agent configurations incur larger input footprints due to context sharing.*

Config B and Config C consume approximately seven and seven and a half times more input tokens than Config A respectively, because their later or aggregator agents must re-read prior context. Total tokens per sample (input plus output) are approximately three times Config A's for both multi-agent configurations. At current `gpt-4o-mini` pricing, Config A cost about $0.0086 across the full 30-sample run, against $0.0149 for Config B and $0.0157 for Config C — approximately 45% less per sample than either multi-agent alternative, while delivering higher recall.

### 4.4 Per-Category Performance

The aggregate recall figures mask a categorical pattern that is informative in itself. Tables 3 and 4 report recall and precision broken down by defect category.

| Category | Config A Recall | Config B Recall | Config C Recall |
|---|---|---|---|
| Logic | 1.000 | 1.000 | 1.000 |
| Security | 1.000 | 0.950 | 0.950 |
| Style/Maintainability | 0.950 | 0.867 | 0.467 |

*Table 3. Per-category recall by configuration.*

| Category | Config A Precision | Config B Precision | Config C Precision |
|---|---|---|---|
| Logic | 0.417 | 0.415 | 0.467 |
| Security | 0.556 | 0.500 | 0.624 |
| Style/Maintainability | 0.466 | 0.529 | 0.558 |

*Table 4. Per-category precision by configuration.*

On logic defects, all three configurations achieved 1.000 mean recall across the 10 logic samples — a ceiling effect that the experimental design has no power to discriminate against. This indicates that well-defined logic defects of the form represented in this dataset are within the reliable detection capacity of `gpt-4o-mini` regardless of architectural framing. On security defects, Config A again reached 1.000 mean recall; Configs B and C both dropped to 0.950, losing half a point on one shared sample (S9), discussed below. On style and maintainability defects, Config A's mean recall was 0.950, Config B's was 0.867, and Config C's fell to 0.467. The 48.3-percentage-point gap between Config A and Config C on style is the primary driver of the aggregate recall difference observed in Table 1.

### 4.5 Per-Sample Recall Pattern

Table 5 reports per-sample recall for all 30 samples. The pattern is uniform across the dataset.

| Sample | Category | Config A | Config B | Config C | Pattern |
|---|---|---|---|---|---|
| L1–L10 | Logic | 1.00 | 1.00 | 1.00 | three-way tie (all 10) |
| S1–S8, S10 | Security | 1.00 | 1.00 | 1.00 | three-way tie (9/10) |
| S9 | Security | 1.00 | 0.50 | 0.50 | A wins |
| ST1 | Style | 1.00 | 1.00 | 0.50 | A wins |
| ST2 | Style | 1.00 | 1.00 | 1.00 | tie |
| ST3 | Style | 1.00 | 1.00 | 0.00 | A wins |
| ST4 | Style | 1.00 | 1.00 | 0.50 | A wins |
| ST5 | Style | 1.00 | 0.67 | 0.67 | A wins |
| ST6 | Style | 1.00 | 1.00 | 0.00 | A wins |
| ST7 | Style | 0.50 | 0.50 | 0.50 | tie (low) |
| ST8 | Style | 1.00 | 1.00 | 0.50 | A wins |
| ST9 | Style | 1.00 | 0.50 | 0.50 | A wins |
| ST10 | Style | 1.00 | 1.00 | 0.50 | A wins |

*Table 5. Per-sample recall grid. "A wins" indicates that Config A's recall strictly exceeded the maximum of Config B and Config C on that sample.*

Across all 30 samples, Config A's recall was greater than or equal to the maximum of Config B and Config C; Config A strictly led at least one multi-agent configuration on nine samples (S9, ST1, ST3, ST4, ST5, ST6, ST8, ST9, ST10), and there was no sample on which Config B or Config C strictly exceeded Config A on recall. The hypothesis that role-specialized multi-agent review achieves higher recall under matched output-token budgets is therefore not supported at the sample level in this dataset.

### 4.6 Qualitative Case Studies

**Case Study 1: SSRF (sample S9), where Config A's recall lead was largest.** The sample is a two-function avatar-fetching module. The canonical issues are (1) SSRF via an unvalidated user-supplied URL, and (2) absence of content-type or size validation, which permits arbitrary bytes to be persisted under a `.png` extension. Config A received recall 1.00: it flagged the SSRF directly and also raised the hardcoded `.png` extension issue, which the judge accepted as a near-paraphrase of the content-type canonical issue, alongside several adjacent observations (missing `user_id` validation, no logging, no graceful exception handling). Config B received recall 0.50: its security specialist caught the SSRF but the content-type issue was not raised by any specialist. The logic specialist additionally raised a "mutable default argument" warning for a parameter that has no default value at all — an example of the role-restriction pressure phenomenon discussed in Section 5. Config C also received recall 0.50: the Aggregator's 150-token output ceiling could not preserve the full range of specialist findings, and the content-type concern was dropped in the merge. This case shows a structural weakness of role-restricted architectures: defects that cross domain boundaries — the content-type issue is part security, part defensive coding — fall into gaps between specialist mandates. The single-agent prompt, which asks for "all issues including logic, security, and style", imposes no such territorial constraint.

**Case Study 2: Pagination (sample L1), where all three configurations achieved recall 1.00 but the qualitative texture differed sharply.** The sample is a 1-indexed pagination function with an off-by-one error in the `start` calculation. Config A produced a seven-point review identifying the off-by-one error, an iterable-consumption issue in `page_count`, missing docstring content, type-hinting inconsistency, a performance concern about list materialization, and a security note about input validation, with zero redundancy (judge relevance score: 5). Config B's review accumulated three genuine logic findings from the first specialist, followed by the security specialist raising "injection vulnerability", "insecure deserialization", and "path traversal" — none of which has any applicability to a pure pagination function that has no external inputs, no deserialization, and no filesystem access. The security specialist, instructed to find security bugs and given an example vocabulary to look for, produced security-shaped speculations rather than reporting that no security issues were found. This drove Config B's redundancy on this sample to 3 and its precision to 0.50. Config C's Aggregator output cut off mid-sentence: its 150-token ceiling could not enumerate all the issues the specialists raised, and the third bullet ("Potential Index Error") ran out of budget before the description was complete.

**Case Study 3: Style collapse (samples ST3 and ST6), where Config C's recall fell to 0.00 while Configs A and B reached 1.00.** Both samples carry multiple diffuse maintainability issues — ST3 involves single-letter parameter names and magic tax-rate constants spread across a tax calculation function; ST6 involves a DRY violation across three near-identical rendering functions. Each Config C style specialist received a 150-token budget that, in our observations, permitted enumerating one or two issues before hitting the cap. The Aggregator then received three already-incomplete specialist reviews and was instructed to merge them into a unified list within another 150-token budget. The merging process appears to retain issues that surface in multiple specialist reports (obvious candidates for deduplication) and to discard issues mentioned in only one specialist's review. Diffuse style defects are by construction unlikely to appear in multiple specialist domains, and so are precisely the issues most likely to be single-mention and discarded by the Aggregator's compression. Since these two samples are the strongest evidence for the mechanism, we treat them as an illustration rather than as proof.

---

## 5. Discussion

### 5.1 The Multi-Agent Hypothesis Is Not Supported Under Budget Control

The pre-registered hypothesis — that role-specialized multi-agent review would achieve higher recall and lower redundancy than a single generalist agent at the same output-token budget — is not supported by the data. Config A's mean recall (0.983) exceeded both Config B's (0.939) and Config C's (0.806), and on no individual sample did either multi-agent configuration exceed Config A on recall. The hypothesis was wrong both in aggregate and at the sample level.

This is consistent with Tran and Kiela's (2025) account of why single-agent systems match or exceed multi-agent systems under equal-budget control. A single agent receiving the full 600-token output budget retains unmediated access to the entire code under review and can freely allocate its attention across all issue categories. A multi-agent system must partition that budget across agents whose outputs are decoupled, and the mechanism that re-assembles the whole — either the concatenation step in B or the Aggregator pass in C — either introduces redundancy or introduces compression loss. Neither assembly mechanism in our setting recovered the coverage that a single unconstrained pass achieved.

### 5.2 The Style Category as Architectural Diagnostic

The per-category breakdown locates the aggregate recall advantage of Config A almost entirely in the style and maintainability category. On logic defects, all three configurations saturate at recall 1.000, which leaves no room for the architectural design to express any preference one way or the other. On security defects the gap is small (1.000 against 0.950). On style defects the gap is large (0.950 against 0.467 for Config C). The architecture only matters where the dataset has dynamic range, and in this dataset the dynamic range lies in style.

This pattern is interpretable. Logic and security defects in our samples tend to be focal: there is a specific line, a specific call, a specific construct, and identifying the defect requires a targeted observation that the agent can produce in a few sentences. Style and maintainability defects tend to be diffuse and multi-dimensional — a signup handler violating the Single Responsibility Principle across five concerns is not a one-line annotation but a multi-paragraph diagnosis. Documenting it fully requires a generalist analytical pass that crosses the logic/security/style trichotomy the multi-agent prompts impose.

The multi-agent architecture's design strength — narrow focus enforced through role-restricted prompting — is what makes it weak on style defects in this setting. A 150-token style specialist cannot draw on logic or security framing to characterize a defect that has both logic and style dimensions; the Aggregator further compresses; the result is that diffuse, cross-cutting style issues fall through the cracks of the specialized pipeline. This suggests a more general principle: multi-agent architectures may be structurally mismatched with tasks whose defect space does not decompose cleanly along role boundaries. For code review, the logic/security/style trichotomy is an attractive conceptual framework, but real-world defects routinely violate it.

### 5.3 Role-Restriction Pressure and Structured Hallucination

The Config B security specialist's behavior on sample L1 — raising injection, insecure deserialization, and path traversal vulnerabilities in a pagination function that has no external inputs, no deserialization, and no filesystem access — deserves attention. This is not a random hallucination; it is a structured one, shaped by the role the specialist has been assigned.

The specialist's system prompt instructs the model to find security vulnerabilities and supplies a list of example patterns to look for (injection, deserialization, path traversal, etc.). It does not authorize the agent to report zero findings. An agent that has been told to look for something and given a vocabulary for what to look for will, under sufficient prompt pressure, find that something even in its absence. The role definition creates an obligation to produce, and the production takes the shape of the role's domain. This is the precise behavior that the confirmation-bias account of Dong et al. (2025) predicts in role-restricted security review.

This phenomenon is structurally absent from Config A's single-agent prompt, which asks for all issues and implicitly permits a review to focus on the issues that exist. On the same pagination sample, Config A raised the off-by-one error, the type-hinting inconsistency, and a mild security note about input validation — all legitimate observations. It did not fabricate injection vulnerabilities, because it was not under role-pressure to find security-shaped content.

In production deployment, a Config B-style review of non-security code would regularly contribute false-positive security alerts to a pull-request review queue, generated by role-pressure hallucination. This would, plausibly, erode developer trust in the automated reviewer faster than would a review that missed a few style points — though we did not measure developer trust directly and treat this implication as a hypothesis for future work rather than as a result of the present study.

### 5.4 Sequential Deduplication Does Not Work

Config B's mean redundancy of 1.733 — against a budget split that includes explicit instructions to each downstream specialist to read prior reviews and not duplicate prior findings — is the single most surprising result in the dataset. Despite context-sharing and explicit anti-redundancy instructions, Config B's redundancy is approximately nine times Config A's (0.200) and six times Config C's (0.300).

The failure can be read off the role boundaries themselves. When the security specialist reads the logic specialist's output, it reads content that is framed as logic analysis. A point raised by the logic specialist as "this function does not validate its inputs" may be re-raised by the security specialist as "unvalidated inputs create injection risk" — substantively a near-duplicate, but framed differently enough that the security specialist's self-assessed deduplication check does not flag it. Role boundaries create semantic frames that interfere with cross-role redundancy detection.

For anyone designing multi-agent review pipelines, this implies that prompted deduplication against shared context is not a reliable mechanism. An explicit aggregation step — as in Config C — achieves substantially lower redundancy (0.300), suggesting that explicit merge logic is more effective than instruction-level deduplication. The aggregation step has its own failure mode, as Section 4 documented, but on the redundancy metric alone, it works.

### 5.5 The Precision–Recall Tradeoff of the Aggregator

Config C's mean precision (0.550) is approximately 7 percentage points higher than Config A's (0.480) and Config B's (0.481). The Aggregator appears to function as a quality filter: by merging specialist outputs and discarding points that appear in only one specialist's review, it reduces the false positive rate among the issues that survive aggregation. This is a real, if modest, advantage of the architecture.

The cost is severe recall degradation. The Aggregator's 150-token output ceiling means it can enumerate approximately 5–7 brief issue descriptions before truncating. When the three specialists collectively raise around 15 distinct issues (even after removing genuine duplicates), the Aggregator must discard roughly two-thirds of the content it received. The discarding process appears to favor issues that are short to describe and prominent in multiple specialist reviews. Diffuse style issues, which are verbose to describe and appear in only the style specialist's review, are disproportionately discarded.

For code review, the asymmetry of consequences matters. A missed critical issue (false negative) is typically more costly than a flagged non-issue (false positive): the former can reach production undetected, while the latter requires a developer to dismiss an alert. Under this asymmetry, Config C's precision-recall tradeoff is unfavorable for most deployment contexts.

### 5.6 Practical Deployment Implications

For teams considering LLM-assisted code review in continuous integration pipelines, the findings here offer concrete guidance for the conditions examined — a 600-token output budget per pull-request, single-function Python snippets, `gpt-4o-mini` as the base model. Under these conditions the single generalist agent provided the highest defect recall (0.983, minimizing the risk of critical issues reaching production), the lowest redundancy (0.200, producing clean review output without noise), the lowest cost per sample ($0.0086 across the 30-sample run against $0.0149–$0.0157 for the multi-agent configurations), and the absence of role-pressure hallucinated security findings.

The intuitive appeal of multi-agent specialization is real, and the organizational analogy to human review teams is compelling. But the data here suggest that, under a fixed inference budget, the overhead of coordination, context-passing, and aggregation can consume more than the benefit of specialization returns. We do not claim that this generalizes beyond our setting — see Section 6 — but the burden of proof for adopting a multi-agent architecture in a CI pipeline should rest on a budget-controlled demonstration of advantage, not on architectural intuition alone.

---

## 6. Limitations and Future Work

Several limitations of the experimental design should be acknowledged.

***Sample size and statistical power.*** The dataset contains 30 samples, which is sufficient for the directional conclusion that no individual sample reversed the ordering, but insufficient for tight confidence intervals on the aggregate mean differences. Per-sample judge scores are preserved in the released `raw_outputs.json` so that paired bootstrap or Wilcoxon signed-rank tests can be applied post hoc. Future replications should scale the dataset to 100–200 samples to enable rigorous estimation of effect sizes and to verify whether the per-sample uniformity holds robustly at larger N.

***Language and task generalizability.*** All samples are single-function Python snippets of 10 to 22 lines. The findings should not be extrapolated without qualification to multi-file review, where the single-agent context window may emerge as a binding constraint; to other languages with distinct idioms — Rust ownership, Go concurrency, JavaScript event-loop semantics — which may decompose differently along specialist roles; or to multi-turn refinement settings, where iterative agent dialogue could alter the comparative picture.

***Single judge model and in-family evaluation.*** GPT-4o judging `gpt-4o-mini` outputs is an in-family evaluation. The two models differ substantially in capability, but they share training provenance and may share systematic biases. Cross-family evaluation using a Claude or Gemini judge, or human expert raters, would provide a stronger robustness check. The zero parse-error rate and uniform compliance with declared score ranges are encouraging for judge reliability but do not rule out systematic bias.

***Single budget operating point.*** This experiment evaluates one budget: 600 output tokens per sample. Two boundary cases remain unexplored. At higher budgets, Config C's per-specialist and Aggregator allocations may grow generous enough to avoid the compression-driven recall loss documented here; the precision lift may then manifest without the recall penalty. At lower budgets, single-agent truncation may impose similar penalties to those observed in Config C, narrowing the gap. Characterizing the full budget–performance frontier across all three configurations is a natural next step.

***Dataset–architecture alignment.*** The logic/security/style trichotomy used to categorize samples is exactly the trichotomy used to define specialist roles in Configs B and C. This is the most architecturally favorable design for multi-agent role specialization — role boundaries are as clean as they will ever be. In real-world code review, defects are not pre-labeled and routinely cross category boundaries. The finding that multi-agent configurations underperformed even under maximally favorable alignment strengthens the negative result; the margin of single-agent advantage in real-world settings, where category boundaries blur, plausibly exceeds what is observed here.

***No retrieval, no tools, no iteration.*** All configurations issue a single forward pass per agent. We did not evaluate retrieval-augmented review (where an agent can look up related code, prior bug reports, or documentation), tool use (where an agent can run a static analyzer and consume its output), or iterative refinement. These capabilities may alter the comparative landscape, particularly for large codebases where retrieval could compensate for context-window pressure on a single agent. Extending the framework to those settings is a useful direction for future work.

---

## 7. Conclusion

This paper presented an equal-output-token-budget comparison of three architectures for LLM-assisted code review: a single generalist agent (Config A), a sequential pipeline of three role-specialized agents (Config B), and a parallel pipeline of three role-specialized agents with an Aggregator (Config C). The framework enforced a 600-token output budget per sample via `max_tokens` on every API call, verified compliance against logged `usage.completion_tokens`, and scored every (sample, configuration) pair with a GPT-4o judge.

Case-based evaluation across 30 hand-labelled Python snippets stratified into logic, security, and style/maintainability categories showed that the GPT-4o judge assigned a mean recall of 0.983 to Config A, 0.939 to Config B, and 0.806 to Config C. On every individual sample, Config A's recall was equal to or greater than the maximum of the two multi-agent configurations; on no individual sample did either multi-agent configuration exceed Config A on recall. The aggregate recall gap was concentrated entirely in the style/maintainability category, where Config C's mean recall fell to 0.467. Role specialization yielded a 7-percentage-point precision lift in Config C (0.550 against 0.480) at a cost of 17.7 percentage points of recall.

Two mechanisms account for the multi-agent shortfall under matched budgets. The sequential pipeline accumulated redundancy (mean 1.733 duplicate points per review, against the single agent's 0.200) despite explicit anti-duplication instructions, because role boundaries created semantic frames that prevented downstream specialists from recognising near-duplicate findings as such. The parallel-plus-Aggregator pipeline lost recall on diffuse style defects through compression, as the 150-token Aggregator budget systematically discarded issues mentioned in only one specialist's review. The single agent, free of role boundaries and unconstrained in within-budget allocation, avoided both failure modes.

The contribution of this work lies in extending the equal-budget critique of multi-agent systems from multi-hop reasoning (Tran and Kiela, 2025) to the code-review setting, and in providing a paired per-sample dataset and harness for future architectural comparisons.

Future work includes: (1) sweeping the output budget across two orders of magnitude to characterise the budget–architecture interaction; (2) extending the dataset to real pull-request history and to languages beyond Python; (3) evaluating cross-family judges or human raters to rule out judge bias; and (4) testing retrieval-augmented and tool-augmented multi-agent variants, which the single-pass design here did not exercise. The broader implication for the field is that controlled, budget-equalized comparisons should be a precondition for attributing performance to architectural innovation in agentic SE systems.

---

## Acknowledgments

The authors thank the OpenAI API for access to GPT-4o-mini and GPT-4o, used as the agent and judge models respectively throughout the experiment. The full 30-sample, 90-review, 90-judge-call run cost approximately $0.28, of which $0.0392 was spent on agent calls and $0.2449 on judge calls — a budget that puts replication and budget-sweep extensions within reach of resource-constrained teams.

---

## References

Chen, Y. (2025). AutoReview: An LLM-based multi-agent system for security issue-oriented code review. In *Proceedings of the 33rd ACM International Conference on the Foundations of Software Engineering (FSE Companion '25)* (pp. 1022–1024). ACM. https://doi.org/10.1145/3696630.3728578

Dong, R., et al. (2025). Measuring and exploiting confirmation bias in LLM-assisted security code review. *arXiv preprint arXiv:2603.18740*. https://arxiv.org/html/2603.18740v1

Khanzadeh, S. (2025). AgentMesh: A cooperative multi-agent generative AI framework for software development automation. *arXiv preprint arXiv:2507.19902*. https://arxiv.org/abs/2507.19902

Phan, H. N., et al. (2024). HyperAgent: Generalist software engineering agents to solve coding tasks at scale. *arXiv preprint arXiv:2409.16299*. https://arxiv.org/pdf/2409.16299

Qian, C., Liu, W., Liu, H., Chen, N., Dang, Y., Li, J., Yang, C., Chen, W., Su, Y., Cong, X., Xu, J., Li, D., Liu, Z., & Sun, M. (2024). ChatDev: Communicative agents for software development. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)* (pp. 15174–15186). Association for Computational Linguistics. https://aclanthology.org/2024.acl-long.810/

Tran, D., & Kiela, D. (2025). Single-agent LLMs outperform multi-agent systems on multi-hop reasoning under equal thinking token budgets. *arXiv preprint arXiv:2604.02460*. https://arxiv.org/pdf/2604.02460

Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S., Narasimhan, K. R., & Press, O. (2024). SWE-agent: Agent-computer interfaces enable language models to autonomously solve software engineering tasks. In *Proceedings of the 38th Conference on Neural Information Processing Systems (NeurIPS 2024)*. https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-bench and Chatbot Arena. In *Proceedings of the 37th Conference on Neural Information Processing Systems (NeurIPS 2023)*. https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf

---

## Appendix A — Complete Agent Prompts

### A.1 Config A — Single Agent System Prompt

```
You are an expert code reviewer. Review the provided code thoroughly.
Identify all issues including logic bugs, security vulnerabilities, and
style problems. For each issue: state the issue type, the line or area
affected, and a brief explanation. Be concise. Format: numbered list.
```

User message: the raw source code with no additional framing.

### A.2 Config B — Sequential Multi-Agent System Prompts

**Agent 1 — Logic Reviewer (max_tokens: 200)**

```
You are a senior software engineer reviewing code SPECIFICALLY for LOGIC
and CORRECTNESS issues only. Examples: off-by-one errors, wrong
conditionals, missing edge cases, incorrect return values, mutable default
arguments, closure-capture bugs. Do NOT comment on security or style.
For each issue: state the type, the line/area, and a brief explanation.
Be concise. Format: numbered list.
```

**Agent 2 — Security Reviewer (max_tokens: 200)**

```
You are a senior application security engineer reviewing code SPECIFICALLY
for SECURITY vulnerabilities only. Examples: injection, insecure
deserialization, weak crypto, hardcoded secrets, SSRF, path traversal, XSS.
Do NOT comment on general logic bugs or style. You may reference Agent 1's
logic findings to avoid duplication, but only report security issues.
For each issue: state the type, the line/area, and a brief explanation.
Be concise. Format: numbered list.
```

**Agent 3 — Style Reviewer (max_tokens: 200)**

```
You are a senior software engineer reviewing code SPECIFICALLY for STYLE,
READABILITY, and MAINTAINABILITY issues only. Examples: poor naming, magic
numbers, deep nesting, missing error handling, DRY violations, inconsistent
return types, single-responsibility violations. Do NOT re-report logic or
security issues already raised by previous agents. For each issue: state
the type, the line/area, and a brief explanation. Be concise.
Format: numbered list.
```

### A.3 Config C — Parallel Multi-Agent System Prompts

Specialist prompts are identical to Config B's specialist prompts, except that the Security and Style reviewers do not reference prior agents (since parallel execution means no prior output exists at call time). The Aggregator prompt (max_tokens: 150):

```
You are a senior code review coordinator. You have received three
independent reviews of the same code from specialist agents. Your job is to:
1. Merge their findings, removing exact duplicates
2. Resolve any contradictions
3. Output a clean, unified numbered list of all unique issues found
Be concise. Do not add new issues not mentioned by the specialists.
```

### A.4 Judge System Prompt

```
You are a careful, impartial reviewer judging the quality of a code review.
You will be given (a) source code, (b) a canonical list of known issues in
that code, and (c) a review produced by another system.

Score the review on four dimensions and return ONLY a single valid JSON
object with these keys:
  recall_score:     float in [0.0, 1.0] — fraction of canonical known
                    issues the review identifies (a near-paraphrase counts).
  precision_score:  float in [0.0, 1.0] — fraction of distinct issues
                    raised by the review that are valid real problems in the
                    code (whether or not they appear in the canonical list).
  redundancy_count: integer >= 0 — count of duplicate or near-duplicate
                    points within the review.
  relevance_score:  integer in {1,2,3,4,5} — overall quality of the review
                    as a holistic code-review artifact.
  reasoning:        one short sentence justifying the scores.

Do not output markdown, code fences, or any text outside the JSON object.
```

Judge settings: `temperature=0.0`, `max_tokens=400`, `response_format={"type": "json_object"}`.

---

## Appendix B — Dataset Category Examples

### B.1 Representative Logic Bug — Sample L1 (Off-by-One in Pagination)

```python
from typing import Iterable, List, TypeVar

T = TypeVar("T")

def paginate(items: List[T], page: int, page_size: int) -> List[T]:
    """Return the items belonging to the requested 1-indexed page."""
    start = page * page_size          # Bug: should be (page - 1) * page_size
    end = start + page_size
    return items[start:end]

def page_count(items: Iterable[T], page_size: int) -> int:
    return (len(list(items)) + page_size - 1) // page_size
```

*Canonical issue: `start = page * page_size` implements 0-indexed semantics despite the docstring claiming 1-indexed pages; page=1 returns `items[size:2*size]`, skipping the first page.*

### B.2 Representative Security Issue — Sample S9 (SSRF)

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

*Canonical issues: (1) SSRF via unvalidated user-supplied `image_url`; (2) no content-type or size validation, permitting arbitrary bytes to be persisted under a `.png` extension.*

### B.3 Representative Style Issue — Sample ST6 (DRY Violation)

```python
def render_html_report(data):
    html = "<html><body>"
    for item in data:
        html += f"<div class='report-item'>{item['name']}: {item['value']}</div>"
    html += "</body></html>"
    return html

def render_email_report(data):
    html = "<html><body>"
    for item in data:
        html += f"<div class='report-item'>{item['name']}: {item['value']}</div>"
    html += "</body></html>"
    return html

def render_pdf_report(data):
    html = "<html><body>"
    for item in data:
        html += f"<div class='report-item'>{item['name']}: {item['value']}</div>"
    html += "</body></html>"
    return html
```

*Canonical issue: three functions with identical bodies violate the DRY principle; a single parameterized renderer should replace all three.*

---

## Appendix C — Experiment Cost Breakdown

| Cost Component | Tokens In | Tokens Out | Rate (per 1M) | Total |
|---|---|---|---|---|
| Config A agents (30 samples) | 4,837 | 13,041 | $0.15 / $0.60 | $0.00855 |
| Config B agents (30 samples) | 34,636 | 16,142 | $0.15 / $0.60 | $0.01488 |
| Config C agents (30 samples) | 36,676 | 17,072 | $0.15 / $0.60 | $0.01575 |
| Judge calls (90 evaluations) | 72,231 | 6,435 | $2.50 / $10.00 | $0.24490 |
| **Total** | | | | **~$0.28** |

*All costs inferred from logged `usage` fields on every API response; not estimated post-hoc.*
