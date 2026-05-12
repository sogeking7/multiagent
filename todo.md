# TODO: Humanize `claude_paper.md` — completed

**Goal.** Rewrite the prose of `claude_paper.md` end-to-end so that it reads like a human-authored research paper rather than an AI-generated one, by applying the sentence templates and paragraph skeletons from `humanize-skill/research_paper_sentence_templates.md`.

**What stayed unchanged** (data integrity preserved):

- [x] All numerical results (recall 0.983 / 0.939 / 0.806; precision 0.480 / 0.481 / 0.550; redundancy 0.200 / 1.733 / 0.300; relevance 3.100 / 2.933 / 3.133; tokens; costs).
- [x] All five main-body tables and three appendix tables.
- [x] All eight references — Chen 2025, Dong et al. 2025, Khanzadeh 2025, Phan et al. 2024, Qian et al. 2024, Tran & Kiela 2025, Yang et al. 2024, Zheng et al. 2023.
- [x] Section structure (Abstract, 1–7, Acknowledgments, References, Appendix A–C).
- [x] All verbatim agent prompts and the judge prompt in Appendix A.
- [x] All canonical issues and code snippets in Appendix B.
- [x] All cost numbers in Appendix C.

**What got rewritten** (per-section template plan):

- [x] **Abstract.** Applied 1.1 (topic anchor opener), 1.2 (problem framing), 1.3 (proposal), 1.4 (method), 1.7 (findings), 1.9 (closing generalisation). Removed "compelling assumption", "critical empirical gap persists", "significantly outperforming", "These findings indicate that".
- [x] **§1 Introduction.** Restructured around 2.1 (topic anchor), 2.2 (causation chain), 2.3 (contextual setting), 2.4 (Nonetheless pivot), 2.5 (Meanwhile opportunity), 2.9 (research question framing), 2.16 (contributions opener), 2.17 (numbered contribution sentence), 2.18 (paper roadmap). Removed "rapid and profound transformation", "has emerged", "operates under the widespread assumption", deep-bolded contribution list.
- [x] **§2 Related Work.** Applied 3.1 (broad opener), 3.2 (citation introduction), 3.4 (authors-show-that), 3.5 (article description), 3.7 (advent of), 3.8 (In this landscape), 3.9 (closest work), 3.10 (gap summary), 3.11 (novelty statement). Folded the AI-tic "**Subsection Title:**" bolded heads into prose where the section was short enough.
- [x] **§3 Methodology.** Applied 4.1 (section purpose declaration), 4.3 (why-this-design rationale), 5.1 (dataset overview), 6.4 (justifying design choices). Replaced the clinical "We did X. We did Y. We did Z." cadence with conditional "We did not X because Y; the implications of this are discussed in Section Z." patterns.
- [x] **§4 Results.** Applied 8.1 (results section opener), 8.2 (case-based finding), 8.3 (However-with-caveat), 8.4 (listing observed behaviors), 8.5 (coherence claim). Removed "**The headline finding is unambiguous**", "is striking in its consistency", "**The critical observation is that...**", and the standalone bolded interpretive sentences. Used 12.9 "This shows that..." / "This is the precise behavior that..." pattern to interpret each case study right after its evidence.
- [x] **§5 Discussion.** Applied 9.1 (discussion opener), 9.3 (This is the precise behavior that…), 9.4 (why-the-design-works), 9.5 (comparison with prior systems), 9.6 (practical implications opener). Dropped "Crucially,", "Importantly,", "In essence,", "uniformly falsified", "compelling". Hedged the developer-trust claim explicitly ("we treat this implication as a hypothesis for future work rather than as a result of the present study") since the experiment did not measure trust.
- [x] **§6 Limitations.** Switched from the bolded-heading style (`### 6.1 Sample Size and Statistical Power`) to the italic-label style of template 10.2 (`***Sample size and statistical power.***`). Each item now: italic label → acknowledgement → constructive fix.
- [x] **§7 Conclusion.** Applied 11.1 (opener), 11.3 (evaluation recap), 11.4 (contribution sentence), 11.5 (future work enumeration). Removed "the answer, across 30 samples, zero exceptions, and two distinct multi-agent topologies, is no" rhetorical flourish.
- [x] **Throughout.** Em-dash clarifications used naturally not as a pattern (12.2); concrete numbers anchored in prose at every claim (12.4); hedging via "appears to", "suggests that", "we treat this as an illustration rather than as proof", "in our setting", "we did not measure X directly" (12.5); active "we" for design decisions, passive for what the judge did (12.6); quoted exact agent outputs in case studies (12.7); three-part lists with tail variation, not parallel triplets (12.8).
- [x] **AI-tells removed throughout:** "rapid and profound transformation", "compelling assumption", "headline finding is unambiguous", "striking in its consistency", "uniformly falsified", "critical empirical gap persists", "**[Concept]:** description" pattern in body text (kept in case-study heads only), redundant bolding of single phrases for emphasis, "Crucially,", "Importantly,", "Notably,", "In essence,", "Significantly outperforming".

**Anti-goal honored.** No new claims, numbers, references, or experimental details were invented; every factual statement remains traceable to `paper_context.md`.

**Output.** Rewritten paper saved to `/Users/sogeking7/My Documents/aitu/multi-agent-v2/claude_paper.md`. Length comparable to the original (the data, tables, and appendices that dominate length were preserved); the prose density should now read closer to a human-authored research paper.
