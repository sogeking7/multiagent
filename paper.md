Title: Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review: A Controlled Comparison Under Equal Token Budgets


Abstract

Multi-agent large language model (LLM) systems are increasingly deployed for software engineering tasks, with role-specialised configurations claimed to outperform single-agent baselines. However, reported gains are typically confounded by inference budget: multi-agent pipelines also emit more tokens than the single-agent comparators they are measured against. We presented a controlled comparison of three code-review configurations — a single generalist agent, a sequential role-specialised pipeline, and a parallel pipeline with an aggregator — under an equal 600 output-token budget per sample. On a hand-curated dataset of 30 Python snippets containing labelled logic, security, and style/maintainability defects, the GPT-4o judge assigned mean recall of 98.3\%, 93.9\%, and 80.6\% to the three configurations respectively. On no individual sample did either multi-agent configuration exceed the single-agent recall, with the gap concentrated in style/maintainability defects. Under matched inference budgets, role specialisation did not improve code-review recall in our setting.


1 Introduction

Software engineering pipelines have become a popular host for LLM-based agents. Agents now draft code, write tests, generate pull-request descriptions, triage incoming bugs, and — most relevant for this paper — review code before it is merged. A common architectural choice in this space is to compose several agents with role-specialised system prompts under the intuition that specialisation should produce denser, less hedged reviews than a single generalist could. Typical designs allocate one agent to correctness, a second to security, and a third to style or maintainability, with a coordinator stitching their outputs together.

The empirical basis for this intuition is contested. Recent work outside the software-engineering domain has challenged the assumption that more agents are better when inference budget is held constant. Tran and Kiela~\cite{tran2025single} reported that under equal "thinking" token budgets, single-agent LLM systems matched or outperformed multi-agent systems on multi-hop reasoning, and that the apparent advantage of multi-agent pipelines in earlier work was largely explained by their using more compute rather than by their architecture. The interface-quality finding from SWE-agent~\cite{yang2024sweagent} points in a similar direction: most of the gain attributed to "agentic" behaviour came from interface design rather than from agent count or inter-agent coordination.

Code review is a natural setting in which to revisit this question for software engineering. Reviews are bounded in scope, evaluable against a ground-truth list of defects, and amenable to clean role decomposition along (logic / security / style) lines. Unlike open-ended reasoning tasks, code-review outputs are easy to compare both quantitatively against a known-issues list and qualitatively against each other. Production CI systems also have a strong reason to care about the compute--quality trade-off: reviews run on every pull request, so the architectural choice has real cost implications at the scale of an engineering organisation. To our knowledge, no published study has compared single- and multi-agent code-review configurations while holding output-token budget constant; this paper supplies one.

Our research question was: \emph{Under a fixed output-token budget per sample, does role-specialised multi-agent code review (sequential or parallel-plus-aggregator) achieve higher recall, higher precision, or lower redundancy than a single generalist agent operating under the same budget?}

Contributions of this paper are:

\begin{itemize}
\item A controlled experimental design that holds total output-token budget constant at 600 tokens across three code-review architectures, enforced via \texttt{max\_tokens} on every API call and verified against logged usage.
\item A hand-curated 30-sample Python dataset stratified across three defect categories (logic, security, style/maintainability), with explicit canonical-issue labels for recall scoring.
\item A negative empirical result: across all 30 samples, multi-agent recall never exceeded single-agent recall, with the gap concentrated in style/maintainability defects.
\end{itemize}


2 Related Work

\textbf{Multi-agent systems for software engineering.} ChatDev~\cite{qian2024chatdev} pioneered the application of role-specialised LLM crews to end-to-end software construction, with separate agents acting as designer, programmer, and tester. Subsequent systems including AgentMesh~\cite{agentmesh} and HyperAgent~\cite{hyperagent} extended this pattern to broader SE tasks such as bug triage, repository question answering, and pull-request authoring. A common framing in these works is that role specialisation, decomposition, and inter-agent communication yield qualitative improvements over a monolithic agent, although the experimental designs typically vary inference budget alongside architecture.

\textbf{Multi-agent code review.} AutoReview~\cite{autoreview2025}, presented at FSE 2025, applied a three-agent role-specialised configuration to security-oriented code review and reported improvements over a single-agent baseline on a curated benchmark. AutoReview did not hold the per-system inference budget constant, so the contribution of architectural specialisation cannot be cleanly separated from raw compute in its reported numbers. Our experimental design is closest to AutoReview in spirit; the key difference is the equal-budget control.

\textbf{Single- versus multi-agent comparisons.} Tran and Kiela~\cite{tran2025single} reported that on multi-hop reasoning benchmarks, single-agent LLMs matched or beat multi-agent systems under equal thinking-token budgets, suggesting that the multi-agent advantage seen in earlier work may have been a compute confound. SWE-agent~\cite{yang2024sweagent} reported that most of the agentic uplift on its software-engineering tasks came from interface design rather than from agent count or coordination overhead. Our paper extends this line of work to the code-review setting, which has different evaluation primitives (recall against known defects, judged review quality) than open-ended reasoning or repository-level patch generation.

\textbf{LLM-as-judge evaluation.} The use of a stronger LLM as a judge for outputs of weaker models is now standard practice for open-ended generation tasks~\cite{zheng2023judging}. Known concerns include in-family bias and brittleness to formatting. We adopted GPT-4o as judge for outputs of GPT-4o-mini agents and report the design alongside its limitations.


3 Methodology

3.1 Research Question and Hypothesis

The research question was stated above. The pre-experiment hypothesis, framed in the way most favourable to the multi-agent claim under test, was that role-specialised multi-agent review (Configs B and C) would produce higher recall and lower redundancy than a single generalist agent (Config A) at the same total output-token budget, because focused-role prompts would admit denser per-role analysis and explicit deduplication mechanisms would keep the final output clean.

3.2 Dataset

We constructed a dataset of 30 Python snippets, each 10--22 lines, stratified into three categories of ten samples: logic bugs (e.g.\ off-by-one in pagination, mutable default arguments, late-binding closure, missing recursive base case), security vulnerabilities (e.g.\ SQL injection via f-string, hardcoded credentials, \texttt{pickle.loads} on a cookie, command injection via \texttt{shell=True}, SSRF on a user-supplied URL), and style/maintainability problems (e.g.\ five-level nested conditionals, missing error handling on \texttt{json.loads}, DRY violation across near-identical renderers, mutable module-level cache without invalidation). Each sample was authored by hand to resemble code that a working engineer might commit and was annotated with a canonical \texttt{known\_issues} list of one to three items that served as the recall ground truth. Several samples carried multiple known issues, making the recall metric more discriminating than a one-defect-per-sample design would. The dataset was kept small and curated rather than scaled in order to preserve label quality and to allow per-sample inspection of every output; we discuss this trade-off in Section 6.

3.3 Experimental Configurations

Three configurations were implemented, all using GPT-4o-mini as the agent model.

\textbf{Config A (Single Agent)} used one API call per sample with a system prompt asking for a numbered list of logic, security, and style issues. The full 600-token output budget was allocated to this single call.

\textbf{Config B (Sequential Multi-Agent)} ran three role-specialised agents in fixed order — Logic Reviewer, then Security Reviewer, then Style Reviewer — at 200 output tokens each. Each later agent received the original code and the verbatim text of all prior agents' reviews, and was instructed not to duplicate findings already raised by earlier agents. The final review handed to the judge was the concatenation of the three specialist sections.

\textbf{Config C (Parallel Multi-Agent with Aggregator)} ran the same three specialist roles concurrently via \texttt{asyncio.gather}, each at 150 output tokens, with no cross-visibility between specialists. A fourth Aggregator agent then received the original code and the three specialist reviews and was instructed to merge findings, remove duplicates, and emit a unified numbered list, at a 150-token budget of its own. The aggregator's text was the artefact handed to the judge.

3.4 Token Budget Control

The central design choice was to fix the total output-token budget per sample at 600 across all three configurations. Output tokens were enforced via \texttt{max\_tokens} on every individual API call (600 for A; 200, 200, 200 for B; 150, 150, 150, 150 for C). Actual completion tokens were read from each API response's \texttt{usage} field and aggregated. Across all 90 agent pipelines in the reported run, no completion exceeded its allocated cap on any call, and mean output tokens were 434.7, 538.1, and 569.1 for Configs A, B, and C respectively.

Equalising output tokens isolates the architectural contribution of role specialisation from the compute contribution of issuing additional calls. Without this control, a multi-agent system that scored higher could not be distinguished from one that simply emitted more text. Input tokens were not equalised — by construction, later agents in Config B re-read prior output and the Config C aggregator re-read all three specialist outputs — and were reported separately so that the asymmetry in total inference cost remains visible to the reader.

3.5 Evaluation Protocol

For every (sample, configuration) pair, we passed the original code, the canonical \texttt{known\_issues} list, and the configuration's final review text to GPT-4o as judge. The judge returned a JSON object with four scores: \texttt{recall\_score} in $[0,1]$ defined as the fraction of canonical known issues identified (near-paraphrases counting); \texttt{precision\_score} in $[0,1]$ defined as the fraction of distinct raised issues that were valid real problems (whether or not in the canonical list); \texttt{redundancy\_count} as a non-negative integer counting duplicate or near-duplicate points within the review; and a holistic \texttt{relevance\_score} on a 1--5 ordinal scale. The judge was instructed to return JSON only and was invoked at \texttt{temperature=0.0} with \texttt{response\_format = \{"type": "json\_object"\}}. Agents ran at \texttt{temperature=0.2}, low but non-zero, so that Config C specialists did not emit literally identical text and thereby inflate redundancy artificially. Across the 90 judge calls in our run, zero parse errors occurred.


4 Results

The aggregate metrics across all 30 samples are summarised in Table~\ref{tab:main}.

\begin{table}[t]
\centering
\caption{Aggregate results across 30 samples under a 600 output-token budget per sample. ``Recall'', ``precision'', and ``relevance'' are means of judge-assigned scores. ``Redundancy'' is the mean count of duplicate points per review. ``Tokens'' is mean total (input + output) tokens per sample. ``Cost'' is the total agent-only USD cost over the 30-sample run.}
\label{tab:main}
\begin{tabular}{lccc}
\toprule
Metric & Config A & Config B & Config C \\
\midrule
Mean recall (\%) & 98.3 & 93.9 & 80.6 \\
Mean precision (\%) & 48.0 & 48.1 & 55.0 \\
Mean redundancy & 0.20 & 1.73 & 0.30 \\
Mean relevance (1--5) & 3.10 & 2.93 & 3.13 \\
Mean tokens (in+out) & 595.9 & 1692.6 & 1791.6 \\
Cost over 30 (USD) & 0.0086 & 0.0149 & 0.0157 \\
\bottomrule
\end{tabular}
\end{table}

The GPT-4o judge assigned a mean recall of 98.3\% to Config A (Single Agent), 93.9\% to Config B (Sequential Multi-Agent), and 80.6\% to Config C (Parallel Multi-Agent with Aggregator). Mean precision was 48.0\%, 48.1\%, and 55.0\% respectively. Config B exhibited substantially higher mean redundancy (1.73 duplicate points per review) than Config A (0.20) or Config C (0.30), despite its specialist agents being explicitly instructed not to duplicate prior findings. Mean relevance scores on the 1--5 ordinal scale clustered tightly at 3.10, 2.93, and 3.13.

A per-category breakdown of recall revealed where the aggregate differences originated (Table~\ref{tab:cat}). Logic and security recall were near-saturated across all three configurations. The recall gap between configurations was concentrated entirely in style/maintainability defects, where Config C dropped to a judged recall of 46.7\%.

\begin{table}[t]
\centering
\caption{Per-category mean recall (\%) by configuration ($n=10$ samples per category).}
\label{tab:cat}
\begin{tabular}{lccc}
\toprule
Category & Config A & Config B & Config C \\
\midrule
Logic & 100.0 & 100.0 & 100.0 \\
Security & 100.0 & 95.0 & 95.0 \\
Style/maintainability & 95.0 & 86.7 & 46.7 \\
\bottomrule
\end{tabular}
\end{table}

Inspection of the per-sample recall grid showed a still cleaner pattern: across all 30 samples, neither multi-agent configuration achieved strictly higher recall than the single-agent configuration on any single sample. Config A's recall was equal to or greater than the maximum of Config B and Config C on 30 out of 30 samples. Config A strictly won on three samples (S9, ST5, ST9) and on additional samples where it tied with one multi-agent configuration but beat the other (ST1, ST3, ST4, ST6, ST8, ST10).

Two qualitative examples illustrate the pattern. On sample S9 (an avatar-fetching function with a known SSRF vulnerability and an unbounded-content issue), Config A identified both canonical issues and the GPT-4o judge assigned it a recall of 100\%, while both multi-agent configurations identified only the SSRF and received recall scores of 50\%. The content-type issue crosses domain boundaries (it is partly a security concern and partly defensive coding) and was not picked up by any role-restricted specialist. On sample ST6 (a deeply duplicated UI rendering function with an obvious DRY violation), Config A identified the canonical issue and the Config B specialists also identified it via the style reviewer, but Config C's aggregator emitted no valid issues from the canonical list within its 150-token budget, receiving a recall score of 0\%.


5 Discussion

The research question was whether role-specialised multi-agent code review beats a single generalist agent under an equal output-token budget. In our setting the answer was no on recall, indistinguishable on precision and relevance for the sequential pipeline, and weakly yes on precision only for the parallel-with-aggregator pipeline. The clearest aggregate result was that the GPT-4o judge assigned higher mean recall to the single agent than to either multi-agent configuration, and that no individual sample reversed the ordering.

Two mechanisms appear to drive the recall gap. First, the per-role token budgets in Configs B and C (200 and 150 tokens respectively) were tight relative to the breadth of issues an enumerative style reviewer would surface; we observed mid-sentence truncation in several Config B and C outputs. Second, role partitioning created a coverage gap on defects that span roles. The SSRF example above is illustrative: the canonical content-type-validation issue is neither a textbook security bug nor a textbook style bug, and no role-restricted specialist treated it as its responsibility. A single generalist agent, asked for all issues, had no such territorial constraint.

The redundancy finding warrants its own attention. Despite explicit "do not duplicate prior findings" instructions to its later agents, Config B's mean redundancy of 1.73 was approximately nine times Config A's 0.20. This suggests that prompted instructions to deduplicate against a shared context are an unreliable coordination mechanism for role-specialised agents in this regime, and that more reliable approaches — for example a dedicated aggregator agent, as in Config C, which achieved redundancy 0.30 — are required if low duplication is a design goal.

Our results connect to Tran and Kiela~\cite{tran2025single}: their finding that single-agent LLMs matched or outperformed multi-agent systems on multi-hop reasoning under equal thinking-token budgets extends, in our experiment, to the code-review setting on recall. We do not claim that role specialisation is never useful — Config C's small precision lift is real — only that its widely-assumed recall advantage was not present in our controlled comparison.

The practical implication for production code-review pipelines is that adopting a multi-agent architecture should be justified by something other than expected recall under matched budgets — for example, parallel latency reduction, separate failure isolation per role, integration with role-specific tools or static analysers, or organisational requirements to log distinct security and style verdicts.


6 Limitations and Future Work

Our experiment was small ($n=30$) and conducted in a single programming language with hand-curated short snippets; we did not compute statistical-significance tests for the aggregate differences, although per-sample judge scores are released so that paired tests can be applied post hoc. The judge was GPT-4o, an in-family model relative to the GPT-4o-mini agents; a cross-family judge or human ratings would strengthen the evaluation. We tested a single 600-token output budget; the relative ranking of configurations may differ at substantially smaller or larger budgets. No configuration used multi-turn refinement, retrieval over codebase context, or tool calls, so our conclusions speak only to the single-forward-pass regime. Finally, the trichotomy of categories in the dataset coincides with the trichotomy of specialist roles in Configs B and C, which is the most favourable design for role specialisation; on heterogeneous real-world reviews the alignment may be looser.

Future directions include scaling the dataset to hundreds of samples drawn from real pull-request history; sweeping the output budget across two orders of magnitude to characterise the budget--architecture interaction; replacing prompt-only role specialisation with lightly fine-tuned specialist models; and extending the comparison to architectures with retrieval or tool calls in the loop.


7 Conclusion

We asked whether role-specialised multi-agent code review beats a single generalist agent under matched output-token budgets. Using three configurations over 30 hand-labelled Python snippets, with budget enforced via per-call \texttt{max\_tokens} and reviews scored by a GPT-4o judge, we observed that the single-agent configuration was assigned higher mean recall (98.3\%) than either the sequential (93.9\%) or parallel-with-aggregator (80.6\%) multi-agent configuration, with the gap concentrated in style/maintainability defects and no individual sample reversing the ordering. Role specialisation produced a small precision lift (55.0\% versus 48.0\%) only when paired with an explicit aggregator. The broader implication is that the multi-agent advantage often reported in software engineering benchmarks deserves re-examination under inference-budget controls; in our setting that advantage did not survive.


Appendix A: Agent Prompts

The system prompts used in each configuration are reproduced verbatim below. Agent calls used GPT-4o-mini at \texttt{temperature=0.2}; the judge used GPT-4o at \texttt{temperature=0.0} with \texttt{response\_format = \{"type": "json\_object"\}}.

A.1 Config A (Single Agent) system prompt:

\begin{quote}\small
You are an expert code reviewer. Review the provided code thoroughly. Identify all issues including logic bugs, security vulnerabilities, and style problems. For each issue: state the issue type, the line or area affected, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.2 Config B (Sequential Multi-Agent), Agent 1 — Logic Reviewer:

\begin{quote}\small
You are a senior software engineer reviewing code SPECIFICALLY for LOGIC and CORRECTNESS issues only. Examples: off-by-one errors, wrong conditionals, missing edge cases, incorrect return values, mutable default arguments, closure-capture bugs. Do NOT comment on security or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.3 Config B, Agent 2 — Security Reviewer:

\begin{quote}\small
You are a senior application security engineer reviewing code SPECIFICALLY for SECURITY vulnerabilities only. Examples: injection, insecure deserialization, weak crypto, hardcoded secrets, SSRF, path traversal, XSS. Do NOT comment on general logic bugs or style. You may reference Agent 1's logic findings to avoid duplication, but only report security issues. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.4 Config B, Agent 3 — Style Reviewer:

\begin{quote}\small
You are a senior software engineer reviewing code SPECIFICALLY for STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor naming, magic numbers, deep nesting, missing error handling, DRY violations, inconsistent return types, single-responsibility violations. Do NOT re-report logic or security issues already raised by previous agents. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.5 Config C (Parallel Multi-Agent), Logic Reviewer:

\begin{quote}\small
You are a senior software engineer reviewing code SPECIFICALLY for LOGIC and CORRECTNESS issues only. Examples: off-by-one errors, wrong conditionals, missing edge cases, incorrect return values, mutable default arguments, closure-capture bugs. Do NOT comment on security or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.6 Config C, Security Reviewer:

\begin{quote}\small
You are a senior application security engineer reviewing code SPECIFICALLY for SECURITY vulnerabilities only. Examples: injection, insecure deserialization, weak crypto, hardcoded secrets, SSRF, path traversal, XSS. Do NOT comment on general logic bugs or style. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.7 Config C, Style Reviewer:

\begin{quote}\small
You are a senior software engineer reviewing code SPECIFICALLY for STYLE, READABILITY, and MAINTAINABILITY issues only. Examples: poor naming, magic numbers, deep nesting, missing error handling, DRY violations, inconsistent return types, single-responsibility violations. Do NOT comment on logic or security issues. For each issue: state the type, the line/area, and a brief explanation. Be concise. Format: numbered list.
\end{quote}

A.8 Config C, Aggregator:

\begin{quote}\small
You are a senior code review coordinator. You have received three independent reviews of the same code from specialist agents. Your job is to:\\
1. Merge their findings, removing exact duplicates\\
2. Resolve any contradictions\\
3. Output a clean, unified numbered list of all unique issues found\\
Be concise. Do not add new issues not mentioned by the specialists.
\end{quote}

A.9 Judge system prompt:

\begin{quote}\small
You are a careful, impartial reviewer judging the quality of a code review. You will be given (a) source code, (b) a canonical list of known issues in that code, and (c) a review produced by another system.\\

Score the review on four dimensions and return ONLY a single valid JSON object with these keys:\\
~~recall\_score: float in [0.0, 1.0] --- fraction of canonical known issues the review identifies (a near-paraphrase counts).\\
~~precision\_score: float in [0.0, 1.0] --- fraction of distinct issues raised by the review that are valid real problems in the code (whether or not they appear in the canonical list).\\
~~redundancy\_count: integer >= 0 --- count of duplicate or near-duplicate points within the review.\\
~~relevance\_score: integer in \{1,2,3,4,5\} --- overall quality of the review as a holistic code-review artifact.\\
~~reasoning: one short sentence justifying the scores.\\

Do not output markdown, code fences, or any text outside the JSON object.
\end{quote}


REVISION NOTES

1. Citation keys (\texttt{tran2025single}, \texttt{qian2024chatdev}, \texttt{agentmesh}, \texttt{hyperagent}, \texttt{autoreview2025}, \texttt{yang2024sweagent}, \texttt{zheng2023judging}) are placeholders. Verify the exact venue, year, page numbers, and authors against the source documents before submission, and supply a matching \texttt{.bib} file. In particular, confirm the AutoReview reference (described in the prompt as "FSE 2025, a 3-agent security review system") and the precise title of Tran and Kiela 2025 (the prompt provided a working title only).

2. Statistical reporting: the paper currently reports differences in means without confidence intervals or significance tests, on a sample size of $n=30$. Consider running a paired bootstrap or paired Wilcoxon signed-rank test on per-sample recall scores (these are preserved in \texttt{results/raw\_outputs.json}) and adding either a confidence interval or a $p$-value to the headline numbers in Table 1 and the corresponding sentences in Sections 4 and 7.

3. Per-sample claim audit: the claim in Section 4 that "Config A's recall was equal to or greater than the maximum of Config B and Config C on 30 out of 30 samples" was verified by direct inspection of \texttt{results/raw\_outputs.json}. The list of "Config A strictly won" samples (S9, ST5, ST9, plus partial wins on ST1, ST3, ST4, ST6, ST8, ST10) likewise comes from that file. Re-verify with a fresh script run before submission, and consider adding a per-sample bar chart in a figure rather than relying on prose alone.

4. Threats to validity: the dataset categories (logic, security, style) coincide exactly with the specialist roles in Configs B and C. This is the design most favourable to role specialisation, and yet the multi-agent configurations still lost on recall. The paper notes this in Section 6; consider promoting it to a paragraph in Section 5 (Discussion) as a strengthening of the negative result rather than a limitation.

5. Tooling for reproducibility: the released artefacts (\texttt{run\_experiment.py}, \texttt{dataset/samples.json}, \texttt{results/raw\_outputs.json}) support replication, but the paper currently does not include a section pointing reviewers to the repository. Add a "Data and Code Availability" footnote with the URL before submission.
