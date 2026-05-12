# TODO — completed

## Phase 1: Humanize `claude_paper.md` — done

Rewrote `claude_paper.md` end-to-end using the sentence templates and paragraph skeletons from `humanize-skill/research_paper_sentence_templates.md`. All AI-tell phrasings ("rapid and profound", "headline finding is unambiguous", "striking in its consistency", "Crucially,", "Importantly,", "In essence,", "uniformly falsified", "significantly outperforming", "has emerged as", "critical empirical gap persists") were removed (each verified to zero occurrences). Human-writing signatures added in their place: Nonetheless/Meanwhile pivots, em-dash clarifications used naturally, "This is the precise behavior that..." interpretation right after evidence, "we did not X because Y" justifications, hedging via "appears to" and "we treat this as an illustration rather than as proof", italic-labelled limitations.

All data preserved: recall $0.983/0.939/0.806$, precision $0.480/0.481/0.550$, redundancy $0.200/1.733/0.300$, all five main-body tables, all eight references, all verbatim agent and judge prompts in Appendix A, all dataset examples in Appendix B, the cost breakdown in Appendix C.

## Phase 2: Port to Springer Nature LaTeX template — done

Rewrote `latex/main-article.tex` end-to-end so that its content matches `claude_paper.md` and its presentation matches the Springer Nature `sn-jnl` template the user already had in place. Title, authors, affiliation, abstract, keywords, all sections, all tables, both figures (tikz architecture diagram + pgfplots recall/precision bar chart), references, and appendices were replaced.

**Structure of the new `latex/main-article.tex`:**

- Title: "Single-Agent vs. Role-Specialized Multi-Agent LLM Systems for Code Review: A Controlled Comparison Under Equal Token Budgets"
- Authors: Danagul Ibaidullina, Diana Slyamkhanova (Astana IT University) — kept from the template; edit if attribution differs.
- Abstract + keywords.
- §1 Introduction (with embedded Contributions list and paper roadmap).
- §2 Related Work (Multi-Agent SE / Challenges to MAS / LLM-as-Judge).
- §3 Methodology (RQ + hypothesis / Dataset / Configurations / Budget enforcement / Evaluation).
- §4 Results (Reliability / Aggregate metrics / Tokens & cost / Per-category / Per-sample grid / Three case studies).
- §5 Discussion (Hypothesis not supported / Style as diagnostic / Role-pressure hallucination / Sequential dedup failure / Precision–recall tradeoff / Practical implications).
- §6 Limitations and Future Work.
- §7 Conclusion.
- References (8 bibitems matching the cite keys: chen2025, dong2025, khanzadeh2025, phan2024, qian2024, tran2025, yang2024, zheng2023).
- Appendix A — Agent System Prompts (verbatim).
- Appendix B — Representative Dataset Samples (L1 / S9 / ST6 code + canonical issues).
- Appendix C — Experiment Cost Breakdown.

**Figures:**

- Figure 1: Side-by-side schematic of Configs A/B/C, drawn with tikzpicture using the same node-style conventions as the original template's architecture figure.
- Figure 2: Mean recall and precision by configuration, drawn with pgfplots.

**Structural validation** (Python script over the .tex source): all 33 environments balanced, all 8 cite keys resolved against bibitems with zero orphan citations and zero unused bibitems, 10 sections, 20 subsections, 7 tables, 2 figures, 786 lines.

**Compilation note for the user:** Local compilation with `pdflatex` on this machine fails because the system TeX Live Basic install is missing several standard packages that `sn-jnl.cls` requires (`cuted.sty`, `threeparttable.sty`, `appendix.sty`, `wrapfig.sty`, and likely more). These are present by default in Overleaf and in MacTeX-full; compile there. The `.tex` source itself is syntactically clean and the previous template successfully compiled in the user's environment with the same dependencies.

## Anti-goal honored

No new data, numbers, references, or experimental claims were invented at any point. Every factual statement in both `claude_paper.md` and `latex/main-article.tex` is traceable to `paper_context.md`.
