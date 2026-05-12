# Research Paper Sentence Templates

A collection of sentence structures and formulas extracted from a human-written research paper on LLM-Powered Multi-Agent Cross-Venue Recommendation. Use these as scaffolding when you write your own paper — replace the bracketed `[...]` slots with your own content.

---

## 1. ABSTRACT

### 1.1 Opening — Establish the importance of the topic
> **Formula:** `The [decision/issue/problem] is noteworthy to [stakeholders] since it determines [outcomes].`

**Example from paper:**
> "The product assortment decision is noteworthy to coffee shops and small food service establishments since it determines the competitiveness, customer satisfaction, and income."

**Variations:**
- `The [X] is a key [management/design/research] choice in [domain].`
- `The [decision of X] influences [outcome 1], [outcome 2] and [outcome 3].`

---

### 1.2 Current state of practice (the problem)
> **Formula:** `Practically such [decisions/methods] are frequently determined by [intuition/heuristic], without a systematic consideration of [the key factor].`

**Example:**
> "Practically such decisions are frequently determined by intuition or insufficient historical data, without a systematic consideration of the local competitive environment."

---

### 1.3 What the paper proposes
> **Formula:** `The paper suggests a [adjective] [system/framework/method] based on [technique] to [achieve goal].`

**Example:**
> "The paper suggests a multi-agent cross-venue recommendation system based on LLM to optimize the assortment of coffee shop products."

**Variations:**
- `This paper presents a [X] proposed using [Y].`
- `This study fills these gaps by (1) [doing X]; (2) [doing Y]; and (3) [doing Z].`

---

### 1.4 Describe the method/framework
> **Formula:** `The framework uses a combination of [data source 1] and [data source 2]; [description 1], and [description 2].`

**Example:**
> "The framework uses a combination of two heterogeneous data sources; the current assortment of a target venue based on supplier order data, and the observable menu items of nearby coffee shops based on public venue listings."

---

### 1.5 System components
> **Formula:** `The system is implemented as a [architecture] where [N] [components] are involved: [A], [B], [C], and [D], which [function description].`

**Example:**
> "The system is implemented as a multi-agent system where four specialized LLM-based agents are involved: a Nearby Menu Analyst, an Assortment Gap Analyst, a Venue Similarity Analyst, and a Coordinator, which reason over different aspects of the recommendation problem and can communicate through structured messages."

---

### 1.6 Evaluation summary
> **Formula:** `The framework is tested on a [evaluation type] of [N] [subjects] in [location], using [data sources].`

**Example:**
> "The framework is tested on a case-based analysis of 19 coffee shops in Astana, Kazakhstan, using real supplier order data of Marketly and the local venue menus obtained at 2GIS."

---

### 1.7 Findings statement
> **Formula:** `Findings in [N] representative [cases] support the hypothesis that the system generates [adjective] [outputs] that have [property] depending on [variable].`

**Example:**
> "Findings in four representative venues support the hypothesis that the system generates context-sensitive, interpretable recommendations that have a different strategy depending on the characteristics of the venue."

---

### 1.8 Expert evaluation result
> **Formula:** `[N] industry practitioners have performed expert evaluation that indicates that the system is [property] (high-confidence items rated [X]/[Y]).`

**Example:**
> "Three industry practitioners have performed expert evaluation that indicates that the system is calibrated to confidence (high-confidence items rated 4.17/5.0)..."

---

### 1.9 Closing — generalization claim
> **Formula:** `The paper generalizes [paradigm] to [new domain], through [mechanism].`

**Example:**
> "The paper generalizes the multi-agent paradigm based on LLM to B2B product assortment recommendation at the venue level, through coordinated specialist agents."

---

## 2. INTRODUCTION

### 2.1 Topic anchor (first sentence)
> **Formula:** `The issue of [X] is a key management choice in [domain A] and [domain B].`

**Example:**
> "The issue of product assortment is a key management choice in coffee shops and small retail food establishments."

---

### 2.2 Chain of causation
> **Formula:** `The decision of [X] influences [outcome 1], [outcome 2] and [outcome 3].`

**Example:**
> "The decision of the products to be included in the menu influences the customer perception, coverage of the demand and local competitiveness."

---

### 2.3 Contextual market setting
> **Formula:** `In the [adjective] market of [location], where [condition A] and [condition B], [outcomes can directly influence X].`

**Example:**
> "In the rapidly expanding market of coffee shops in Kazakhstan, where a new coffee shop is opened every so often and customer expectations change very fast, assortment choices can directly influence whether a coffee shop will be able to compete..."

---

### 2.4 Contrast with reality — "Nonetheless" pivot
> **Formula:** `Nonetheless, in most [contexts], these are still [decisions] that are not made with [formal method] and are instead made based on [informal alternative].`

**Example:**
> "Nonetheless, in most small businesses, these are still decisions that are not made with formal analysis support and are instead made based on intuition, personal experience, or internal sales records that are limited."

---

### 2.5 "Meanwhile" — the opportunity setup
> **Formula:** `Meanwhile, a [adjective] source of [resource] has been left mostly unexploited: [description].`

**Example:**
> "Meanwhile, a potent source of competitive intelligence has been left mostly unexploited: the visible menus of local coffee shops."

---

### 2.6 Concrete observation pattern
> **Formula:** `In a situation where [observation], this indicates [interpretation]. However, to convert [these observations] into [systematic outputs], it is necessary to have [capability] which most [actors] lack.`

**Example:**
> "In a situation where the competition of a venue is always selling croissants, waffles or breakfast items, this indicates the local demand trends that the venue is failing to meet. However, to convert these handful of observations into systematic, operational recommendations on assortment, it is necessary to have analytical skills which most operators of small business lack."

---

### 2.7 Research Problem framing
> **Formula:** `Although many studies have been conducted on the topic of [field], and more recently, the emergence of [trend], [N] challenges stand out as yet to be addressed to enable [goal] in [domain].`

**Example:**
> "Although many studies have been conducted on the topic of recommender systems, and more recently, the emergence of multi-agent architectures based on the use of the LLM, three challenges stand out as yet to be addressed to enable venue-level optimization of B2B assortment in small food service businesses..."

---

### 2.8 Numbered challenge format
> **Formula:** `**[Challenge Name]:** [Description of current state]. [What is needed instead]. [Why it is hard].`

**Example:**
> "**Heterogeneous Data Integration:** The current range of recommender systems make use of user-item interaction matrices, yet assortment decisions in small venues require the integration of internal supplier order histories with external competitive signals through the observation of nearby venue menus — two qualitatively different data modalities that no previous framework jointly processes."

---

### 2.9 Research question framing
> **Formula:** `Based on this, the main research question guiding this work is: How can [output property] [outcomes] be generated by using [input A] combined with [input B] through [mechanism]?`

**Example:**
> "Based on this, the main research question guiding this work is: *How can context-sensitive, interpretable product assortment recommendations of small food service establishments be generated by using internal supplier data on order history combined with publicly observable competitor menus through autonomous reasoning agents powered by LLM?*"

---

### 2.10 Defining a foundational concept
> **Formula:** `A [concept] is a [category] that [does X], based on [signals], such as [example 1], [example 2] and [example 3].`

**Example:**
> "A recommender system is a computer program that recommends items of interest to users, based on different signals, such as past behavior, item attributes and contextual information."

---

### 2.11 Historical/evolutionary statement
> **Formula:** `Initially introduced to [original domain], [topic] have been widely studied in the field of [domain 1], [domain 2], and [domain 3].`

**Example:**
> "Initially introduced to e-commerce platforms to propose products to individual consumers, recommender systems have been widely studied in the field of content platforms, media services, and retail decision support."

---

### 2.12 "But/However" — distinguishing your work
> **Formula:** `But most of the currently available [systems] are [type X]: they [do Y]. The issue that this paper aims to discuss is fundamentally different. We [do Z], a [new type] task, which has received little coverage in the literature.`

**Example:**
> "But most of the currently available recommender systems are user-item systems: they suggest products to individual consumers based on interaction histories. The issue that this paper aims to discuss is fundamentally different. We suggest products to venues, using cross-venue competitive signals — a B2B supplier-side recommendation task, which has received little coverage in the literature."

---

### 2.13 Defining a paradigm
> **Formula:** `An [paradigm] can be seen as the [act of doing X] — [entity] capable of [verb 1], [verb 2], [verb 3] and [verb 4] with little intervention of [humans/external actors].`

**Example:**
> "An agentic approach can be seen as the designing of AI systems as an autonomous agent — software entity capable of perceiving its environment, reason about its goals, plan its actions and execute them with little intervention of human beings."

---

### 2.14 Contrast statement
> **Formula:** `In contrast to [conventional approach], which [does X], [new approach] use[s] [Y] of [Z] to [achieve goal].`

**Example:**
> "In contrast to conventional machine learning models, which learn statistical patterns of training data, LLM-based agents use the broad world knowledge, reasoning abilities and unstructured information processing capabilities of the language model to make context-sensitive decisions."

---

### 2.15 List of benefits structure
> **Formula:** `This [approach/decomposition] has a number of benefits: it [benefit 1], [benefit 2], and gives [benefit 3].`

**Example:**
> "This decomposition has a number of benefits: it makes it possible to reason in modules over heterogeneous data sources, enhances transparency due to separately inspectable decision components, and gives different agents the ability to bring complementary viewpoints to a challenging problem."

---

### 2.16 Contributions section opener
> **Formula:** `Based on these observations, this paper presents a [type of system] proposed using [technique]. The main contributions are:`

**Example:**
> "Based on these observations, this paper presents a product-assortment optimization multi-agent cross-venue recommendation system proposed using LLM. The main contributions are:..."

---

### 2.17 Numbered contribution sentence
> **Formula:** `We [verb: model/design/prove/test] the [problem/system] as [a description] that integrates [A] with [B], and explicitly notates [details].`

**Example:**
> "We model the cross-venue assortment recommendation problem as a multi-source decision problem that integrates internal supplier order information with external competitive signals provided by nearby venues, and explicitly notates candidate space, prevalence, gap importance, and confidence assignment."

---

### 2.18 Paper roadmap
> **Formula:** `The rest of this paper is structured in the following way. Section 2 reviews related work. Section 3 [does X]. Section 4 [does Y]. ... Section [N] concludes.`

**Example:**
> "The rest of this paper is structured in the following way. Section 2 reviews related work. Section 3 formalizes the problem statement. Section 4 describes data collection. Section 5 presents the proposed framework. Section 6 describes the experimental setup. Section 7 presents results and expert evaluation. Section 8 discusses findings and limitations. Section 9 concludes."

---

## 3. RELATED WORK

### 3.1 Section opener (broad statement)
> **Formula:** `[Topic] have been widely explored in areas such as [A], [B], and [C].`

**Example:**
> "Recommender systems have been widely explored in areas such as e-commerce, content providers, and retail decision support."

---

### 3.2 Citation introduction pattern (active voice)
> **Formula:** `A recent survey of the important paradigms in the field of [A], [B], and [C] is presented by [Authors] [N].`

**Example:**
> "A recent survey of the important paradigms in the field of collaborative filtering, content-based recommendation, and hybrid methods is presented by Ibrahim et al. 2025 [1]."

---

### 3.3 Citing what authors argue
> **Formula:** `[Authors] [ref] point out that nowadays, the objectives of [X] are increasingly focused on [Y], as [supporting evidence].`

**Example:**
> "Stalidis et al. point out that nowadays, the objectives of recommendation systems are increasingly focused on retail, as modern recommendation systems are directed at achieving objectives related to retail, such as marketing alignment and sustainable customer engagement [2]."

---

### 3.4 Authors "show that" pattern
> **Formula:** `[Authors] [ref] show that the [systems] must consider [A], [B], [C], and [D], especially when it comes to [context], where the goal is to [X], rather than [Y].`

**Example:**
> "Alhijawi et al. [3] show that the recommender systems must consider diversity, novelty, coverage, and similar objectives, especially when it comes to assortment planning, where the goal is to enrich, rather than repeat the product offering."

---

### 3.5 Article description with implication
> **Formula:** `The article by [Authors] [ref] presents a [approach] to [task], showing an increasing interest in applying [methodology] to [application area].`

**Example:**
> "The article by Eneji et al. [4] presents a hybrid deep learning approach to assess user experience in online food delivery services, showing an increasing interest in applying intelligent systems to food service analytics."

---

### 3.6 Distancing from related work — "They are however based on..."
> **Formula:** `They are however based at the [level/perspective] whereby [recommendations/outputs] are made to [audience] based on [signal]. The [venue/level/setting] that this work addresses, in which [the object of recommendation is X and not Y], is out of the range of this body of literature, and inspires the need to consider a fundamentally different formulation.`

**Example:**
> "They are however based at the user-item level of interaction whereby recommendations are made to individual consumers based on their past behavior. The venue-level B2B context that this work addresses, in which the object of recommendation is a business venue and not an end user, is out of the range of this body of literature, and inspires the need to consider a fundamentally different formulation."

---

### 3.7 "The advent of" trend statement
> **Formula:** `The advent of [trend] has provided a new paradigm of research on [topic]. A detailed survey of existing paradigms, given by [Authors] [ref], includes [N] paradigms: [A], [B], and [C].`

**Example:**
> "The advent of agents driven by LLM has provided a new paradigm of research on recommendations. A detailed survey of existing paradigms, given by Peng et al. [5], includes three paradigms: recommender-oriented, interaction-oriented and simulation-oriented approaches."

---

### 3.8 "In this landscape" — situating individual works
> **Formula:** `In this landscape, [Authors] [ref] proposed [Name], a [type] that can be used to [function] at [venue/conference], showing that [insight].`

**Example:**
> "In this landscape, Wang et al. [6] proposed MACRec, a multi-agent collaboration framework that can be used to perform recommendation tasks at SIGIR 2024, showing that numerous specialized agents are beneficial in performing recommendation tasks."

---

### 3.9 "Closest work" comparison
> **Formula:** `In [domain], closest work to our approach is [Name] [ref] applied to [domain X], where [description] — the closest work to our approach though focused on [different aspect Y] as opposed to [our Z].`

**Example:**
> "In retail, closest work to our approach is SofAgent [10] applied to the furniture retail at Natuzzi, where cooperative agents process inquiries about products — the closest work to our approach though focused on customer facing assistance as opposed to supplier-side assortment decisions."

---

### 3.10 Summarizing the gap after related work
> **Formula:** `Although such systems demonstrate the worth of [paradigm] in [problem], none of them have been applied to [your specific setting] where [characteristics] demand qualitatively different patterns of reasoning than those used in [the adjacent setting].`

**Example:**
> "Although such systems demonstrate the worth of multi-agent decomposition in complex recommendation problems, none of them have been applied to supplier-side optimization of assortment where sources of heterogeneous data (internal orders and external competitor signals) demand qualitatively different patterns of reasoning than those used in user-facing conversational systems."

---

### 3.11 Stating your novelty
> **Formula:** `The current work expands the [paradigm] on [technique] to the [new setting] and addresses a gap that the surveyed literature fails to address.`

**Example:**
> "The current work expands the multi-agent paradigm on LLM-powered to the venue-level B2B assortment recommendation environment and addresses a gap that the surveyed literature fails to address."

---

### 3.12 "Nonetheless, this is inverted by our work"
> **Formula:** `Nonetheless, this is inverted by our work: we take [thing X] as [interpretation Y]. This restructuring changes [original signal type] that are [original purpose] to [new purpose].`

**Example:**
> "Nonetheless, this is inverted by our work: we take our observations of nearby venues as the competitive signals of the venues themselves. This restructuring changes location-based signals that are a user-targeting mechanism to a B2B competitive intelligence source."

---

### 3.13 "[Topic] is a well-established concept"
> **Formula:** `Optimization of [X] is already a well-established concept in [field].`

**Example:**
> "Optimization of assortment is already a well-established concept in operations research."

---

### 3.14 Research gap identification
> **Formula:** `The reviewed literature spans [A], [B], [C], and [D] — all actively researched in isolation. However, the intersection of these domains, specifically as applied to [your case], reveals [N] significant gaps that the proposed framework directly addresses:`

**Example:**
> "The reviewed literature spans recommender systems, LLM-powered multi-agent architectures, location-aware recommendation, and assortment optimization — all actively researched in isolation. However, the intersection of these domains, specifically as applied to small food service venues, reveals three significant gaps that the proposed framework directly addresses..."

---

### 3.15 Gap structure
> **Formula:** `Gap [N] — [Title with bold]. [Description of what does not exist or what is missing]. [Why it matters for your problem].`

**Example:**
> "**Gap 1 — Absence of B2B venue-level recommendation frameworks.** Existing recommender systems [1–3, 5, 6, 8, 9] target end-consumer interactions and cannot be directly transferred to venue-level assortment decisions, where the recommendation subject is a business rather than a user and the optimization signal is competitive positioning rather than predicted clicks."

---

## 4. PROBLEM STATEMENT / METHODOLOGY

### 4.1 Section purpose declaration
> **Formula:** `This section formalizes the [problem] as a [type of task] and defines the [mathematical objects] and [operations] underlying the proposed [framework].`

**Example:**
> "This section formalizes the cross-venue assortment recommendation problem as a multi-source decision task and defines the mathematical objects and operations underlying the proposed multi-agent framework."

---

### 4.2 Mathematical notation introduction
> **Formula:** `Let [symbol] denote a [object] that [does X]. The [property] of [symbol] is defined as the set [...]`

**Example:**
> "Let Vt denote a target venue (coffee shop) that purchases food products from a supplier. The current assortment of Vt is defined as the set of products..."

---

### 4.3 "Why" subsection — design rationale
> **Formula:** `The structure of [Equations X–Y] reveals [N] properties motivating [the design decision]. First, [property 1]. Second, [property 2]. Third, [property 3]. These structural distinctions naturally map onto [N components] whose design is detailed in [Section X].`

**Example:**
> "The structure of Equations (3)–(8) reveals three properties motivating a multi-agent decomposition. First, the prevalence and gap signals (Equations (4)–(5)) are derived from the external menu set... Second, the similarity score (Equation (6)) operates on the venue level rather than the product level... Third, the final confidence assignment (Equation (8)) requires a synthesizing function..."

---

## 5. DATA COLLECTION

### 5.1 Dataset overview
> **Formula:** `The empirical basis consists of [N] interrelated datasets ([Table X]), collected in collaboration with [partner], a [description] in [location].`

**Example:**
> "The empirical basis consists of three interrelated datasets (Table 1), collected in collaboration with Marketly, a food product supplier in Astana, Kazakhstan."

---

### 5.2 Data extraction description
> **Formula:** `[Source] sent out [N] [data unit] in [time period], which were used to make [the main dataset]. We used [tool] to [process action] and get [output]. After [cleaning steps], it has [N] records from [M] [entities].`

**Example:**
> "Marketly sent out 31 daily PDF delivery reports in March 2026, which were used to make the main dataset. We used pdfplumber to break down each report and get records for each order and item. After removing duplicates and cleaning up the data, it has 18,288 item-level records from 108 different restaurants and 257 different product names."

---

## 6. PROPOSED FRAMEWORK

### 6.1 System overview
> **Formula:** `The system implements [a type of architecture] with [N] [components] (Figure X, Table Y). Unlike [alternative type], each [component] is [description] that [function] and produces [output].`

**Example:**
> "The system implements an LLM-powered multi-agent architecture with four specialized agents (Figure 2, Table 2). Unlike pipeline-based systems, each agent is an autonomous language model reasoner that analyzes data through natural language reasoning and produces structured output with explicit argumentation."

---

### 6.2 Architecture layering
> **Formula:** `The framework consists of [N] layers: (1) [layer 1]; (2) [layer 2]; (3) [layer 3]; and (4) [layer 4].`

**Example:**
> "The framework consists of four layers: (1) a data layer storing assortment and nearby menu datasets; (2) an agent layer with four LLM-powered agents; (3) a coordination layer where the Coordinator synthesizes outputs; and (4) a presentation layer implemented in Streamlit."

---

### 6.3 Component description
> **Formula:** `This [component] receives [input] and produces [output], identifying [details]. For [example case], the [component] identified [specific finding].`

**Example:**
> "This agent receives nearby venue menu items and produces an analysis of local market patterns, identifying frequent categories, local norms, and notable items. For Oyan Aiplus, the agent identified *croissant* as a local norm based on presence in 2 of 3 nearby venues."

---

### 6.4 Justifying design choices
> **Formula:** `We did not [tune X] because [reason A] and the task is [characteristic B] rather than [opposite]. The implications of this choice — in particular, [side effect] — are discussed in Section [X].`

**Example:**
> "We did not tune temperature or sampling parameters because the agents' system prompts request strict JSON output and the task is structured rather than open-ended. The implications of this choice — in particular, the run-to-run variance it introduces — are discussed in Section 8.5."

---

## 7. EXPERIMENTAL SETUP

### 7.1 Implementation description
> **Formula:** `The system was implemented in [language] using [framework/API]. Each [component] calls [model] (`model-id`) with a [type of input] that defines [list of fields].`

**Example:**
> "The system was implemented in Python using the Anthropic API. Each agent calls Claude Sonnet (claude-sonnet-4-20250514) with a dedicated system prompt that defines the agent's role, the expected input format, the task description, and the required JSON output schema."

---

### 7.2 Cost / scaling discussion
> **Formula:** `The framework is cheap to set up because each [run/operation] needs [N] [units], which costs about [$X-$Y] per [unit]. This is cost-effective to set up on [scale 1] and at scale with [scale 2].`

**Example:**
> "The framework is cheap to set up because each pipeline run needs four API calls to Claude Sonnet, which costs about 0.02–0.05 per venue analysis. This is cost-effective to set up on individual venues and at scale with a supplier managing a large client portfolio."

---

### 7.3 Subject selection
> **Formula:** `[N] of the [M total] [subjects] were chosen as [target group] because they had [criterion 1] and [criterion 2].`

**Example:**
> "Nineteen of the 108 restaurants were chosen as target venues because they had enough order history and data was available nearby."

---

### 7.4 Evaluation approach declaration
> **Formula:** `We adopt [evaluation method] complemented by [secondary method], evaluating: (1) [aspect 1], (2) [aspect 2], (3) [aspect 3], and (4) [aspect 4].`

**Example:**
> "We adopt case-based evaluation complemented by expert assessment, evaluating: (1) recommendation quality, (2) adaptive reasoning, (3) agent contribution, and (4) interpretability."

---

## 8. RESULTS AND ANALYSIS

### 8.1 Results section opener
> **Formula:** `Table [X] summarizes [outputs] for each case. The system produces qualitatively different [strategies/outputs] depending on [variable].`

**Example:**
> "Table 3 summarizes recommendations and strategies for each case. The system produces qualitatively different strategies depending on venue characteristics."

---

### 8.2 Case-based finding
> **Formula:** `**[Case name] ([metric])** shows that the system can respond in a [adjective] way. [Agent X] didn't find [Y], so the [Component Z] only made [N] [action], both of which were based on [evidence]. This behavior shows that the framework [property], which is something that [alternative method] can't do.`

**Example:**
> "**HP Coffee (162 items)** shows that the system can respond in a proportional way. Agent 2 didn't find any important category gaps, so the Coordinator only made two targeted bakery recommendations, both of which were based on the reference venue I'MCafe... This behavior shows that the framework changes how aggressive its recommendations are based on how full the venue is, which is something that frequency-thresholding methods can't do."

---

### 8.3 "However" with appropriate caveat
> **Formula:** `[Description of finding]. However, since there are only [a few cases / limited data], we see this as an example rather than proof.`

**Example:**
> "This selective deprioritization, which happens even when statistical prevalence supports inclusion, aligns with LLM-powered agents reasoning about venue identity rather than just nearby frequency. However, since there are only a few cases, we see this as an example rather than proof."

---

### 8.4 Listing observed behaviors
> **Formula:** `The system showed [N] types of [property] across the [N] cases: **[type 1]** ([brief description]), **[type 2]** ([description]), and **[type 3]** ([description]).`

**Example:**
> "The system showed three types of adaptive reasoning across the four cases: **brand-awareness** (deprioritizing items conflicting with venue identity for Punto), **cultural context** (prioritizing Eastern European items for Chudo Coffee), and **proportional response** (selective enhancement for HP Coffee versus critical gap filling for Oyan Aiplus)."

---

### 8.5 Coherence claim
> **Formula:** `All [N] strategies emerged from the same underlying framework with no per-[subject] parameter tuning, which is consistent with the role of the [theoretical term] in [Equation X].`

**Example:**
> "All four strategies emerged from the same underlying framework with no per-venue parameter tuning, which is consistent with the role of the contextual identity term in Equation (8)."

---

### 8.6 Calibration finding
> **Formula:** `A clear alignment was observed between [system measure] and [external measure] ([Table X]): [tier 1] received a mean rating of [a], [tier 2] [b], and [tier 3] [c]. This [pattern] indicates [interpretation].`

**Example:**
> "A clear alignment was observed between system confidence and expert ratings (Table 5): high-confidence items received a mean rating of 4.17, medium-confidence 3.25, and low-confidence 2.42. This monotonic decrease indicates well-calibrated confidence assessment."

---

## 9. DISCUSSION

### 9.1 Discussion opener — addressing claims
> **Formula:** `The experimental outcomes directly corroborate the proposed solutions for each [gap/hypothesis] identified in Section [X].`

**Example:**
> "The experimental outcomes directly corroborate the proposed solutions for each research gap identified in Section 2."

---

### 9.2 Addressing each claim/gap
> **Formula:** `**Addressing [Gap X] ([Title]):** The framework [did Y] without relying on [unavailable resource], which is [property] in this setting. [Evidence statement]. These results suggest that [interpretation], supporting [conclusion]. To prove that [a stronger claim], it needs to be tested on a larger scale.`

**Example:**
> "**Addressing Gap 1 (Absence of B2B venue-level recommendation):** The framework produced ranked recommendations for all 19 target venues without relying on user–item interaction data, which is structurally unavailable in this setting. Expert evaluation indicates that recommendations were perceived as appropriate at the venue level... These results suggest that LLM-powered agents can substitute for the missing user-interaction signal traditionally required by recommender systems in this case-study setting..."

---

### 9.3 "This is the precise behavior that..."
> **Formula:** `This is the precise behavior that [alternative method 1] or [alternative method 2] would fail to produce.`

**Example:**
> "This is the precise behavior that purely internal demand models or purely external prevalence-thresholding methods would fail to produce."

---

### 9.4 Why-the-design-works subsection
> **Formula:** `[N] structural properties of the proposed architecture explain its effectiveness. *[Property 1].* [Explanation]. *[Property 2].* [Explanation]. *[Property 3].* [Explanation].`

**Example:**
> "Three structural properties of the proposed architecture explain its effectiveness. *Decomposed reasoning over heterogeneous evidence.* The mathematical structure of Equations (3)–(8) cleanly separates external market signals... *Transparency through agent-level inspectability.* Because each agent produces structured intermediate outputs, the reasoning chain leading to a final recommendation is fully traceable..."

---

### 9.5 Comparison with existing systems
> **Formula:** `Compared to [System A] [ref], which operates on [their setting] in a [their paradigm], our framework addresses [our setting] over [our data type] with [our distinguishing feature].`

**Example:**
> "Compared to MACRec [6], which operates on user–item interaction datasets in a recommender-oriented paradigm, our framework addresses venue-level B2B decisions over heterogeneous data sources with no user-interaction signal available."

---

### 9.6 Practical implications opener
> **Formula:** `The suggested framework will have a practical use to [N] groups of stakeholders. In the case of [group 1] the system offers [benefit]. In the case of [group 2], the framework facilitates [benefit]. In the case of [group 3], the approach shows that [insight].`

**Example:**
> "The suggested framework will have a practical use to three groups of stakeholders. In the case of small food service operators the system offers actionable recommendations on assortment based on observable competitive evidence... In the case of the suppliers of food products (such as Marketly), the framework facilitates value added advisory services..."

---

## 10. LIMITATIONS

### 10.1 Limitations opener
> **Formula:** `Several limitations should be acknowledged.`

**Example:**
> "Several limitations should be acknowledged."

---

### 10.2 Each limitation
> **Formula:** `***[Limitation type].*** [Description of the limitation]. [What would fix it / future work direction].`

**Example:**
> "***Dataset scale.*** The nearby menu dataset was manually collected from public 2GIS listings and may be incomplete. Semi-automated collection through web scraping or partner data agreements would allow the framework to scale to larger venue populations."

---

### 10.3 Acknowledging a missing component
> **Formula:** `We did not [quantify/perform] [X] in the present study; doing so — for instance, by [concrete method] — is a useful direction for future work.`

**Example:**
> "We did not quantify this variance in the present study; doing so — for instance, by running each venue k times and reporting the agreement rate of top-N recommendations — is a useful direction for future work."

---

### 10.4 Defending a missing baseline
> **Formula:** `The present study does not include a [missing element]. We outline below the [design] that future work should implement; the design is included here so that subsequent studies can replicate the setup directly.`

**Example:**
> "The present study does not include a quantitative comparison against alternative recommendation strategies. We outline below the baseline comparison design that future work should implement; the design is included here so that subsequent studies can replicate the setup directly."

---

### 10.5 Baseline / ablation enumeration
> **Formula:** `**[Label] — [Baseline Name].** [Description]. This baseline isolates the contribution of [aspect X] over [aspect Y].`

**Example:**
> "**B1 – Frequency thresholding.** A rule-based recommender that returns all candidate items appearing in at least τ nearby venues (e.g., τ = 2 for the present dataset), ranked by raw prevalence (Equation (4)). This baseline isolates the contribution of LLM reasoning over the prevalence signal alone."

---

### 10.6 Treating designs as contributions
> **Formula:** `We treat both designs as contributions in their own right: they specify a concrete protocol that can be applied not only to the present framework but also to comparable [systems] in adjacent domains.`

**Example:**
> "We treat both designs as contributions in their own right: they specify a concrete protocol that can be applied not only to the present framework but also to comparable multi-agent recommendation systems in adjacent domains."

---

## 11. CONCLUSION

### 11.1 Conclusion opener — what was proposed
> **Formula:** `This paper proposed an [adjective] [system/framework] for [task] in [domain]. The framework combines [data 1] and [data 2] through [N] [components] that [verb 1] and [verb 2].`

**Example:**
> "This paper proposed an LLM-powered multi-agent cross-venue recommendation framework for product assortment optimization in coffee shops. The framework combines internal supplier order data and publicly observable nearby venue menus through four specialized LLM agents that reason autonomously and communicate through structured protocols."

---

### 11.2 Formalization recap
> **Formula:** `We formalized the [problem] with explicit mathematical notation for [A], [B], [C], and [D], and showed how this structure naturally maps onto [N] specialized [components].`

**Example:**
> "We formalized the cross-venue assortment recommendation problem with explicit mathematical notation for candidate space, prevalence, gap importance, and confidence assignment, and showed how this structure naturally maps onto four specialized agents."

---

### 11.3 Evaluation recap
> **Formula:** `Case-based evaluation across [N] representative [subjects] showed [adjective] recommendations accounting for [property 1], [property 2], and [property 3]. Expert evaluation supports the alignment of [the system measure] with [external measure] ([details]) and indicates that [secondary finding].`

**Example:**
> "Case-based evaluation across four representative venues showed adaptive, context-sensitive recommendations accounting for venue identity, local market norms, and cultural preferences. Expert evaluation supports the alignment of the system's confidence calibration with professional judgment (high-confidence items: 4.17/5.0) and indicates that explanation quality is highly interpretable (5.0/5.0)."

---

### 11.4 Contribution sentence
> **Formula:** `The contribution of this work lies in framing [problem] as a [type of task] and providing an initial empirical study within [context] — a setting that has received limited attention in prior [field] research.`

**Example:**
> "The contribution of this work lies in framing venue-level B2B assortment optimization as a multi-agent LLM reasoning task and providing an initial empirical study within a single supplier context — a setting that has received limited attention in prior multi-agent recommendation research."

---

### 11.5 Future work enumeration
> **Formula:** `Future work includes: (1) [direction 1]; (2) [direction 2]; (3) [direction 3]; ... (N) [direction N].`

**Example:**
> "Future work includes: (1) executing the baseline comparison and ablation study designs described in Section 8.5, which are the most important next steps to strengthen the empirical claims of the present framework; (2) quantifying run-to-run variance through repeated execution and reporting top-N stability; (3) incorporating temporal purchase patterns and demand forecasting; (4) integrating profitability-aware ranking..."

---

## 12. RECURRING HUMAN-WRITING SIGNATURES

These devices appear throughout the paper and give the writing its human texture. Use them liberally.

### 12.1 The "Nonetheless / Meanwhile / However" pivot
After a positive statement of an existing practice or system, pivot to its limitation:
- `Nonetheless, in most [contexts], [the practice falls short because...].`
- `Meanwhile, [an underexploited resource] has been left unaddressed: [...].`
- `However, [doing X with this resource] requires [skill/method] which [actors] lack.`

### 12.2 The em-dash clarification
Used to refine or qualify a statement mid-sentence:
- `[concept] — [a precise alternative phrasing] — [continuation]`
- Example: "two qualitatively different data modalities — that no previous framework jointly processes."

### 12.3 The "i.e." / "e.g." technical clarification
- `[broad statement], i.e. [precise restatement].`
- `[output property], e.g., [concrete examples].`

### 12.4 Concrete numbers within prose
Always anchor abstract claims with concrete data:
- `[N] [items] were [extracted/processed] from [M] [sources].`
- `[outcome was rated] [X]/[Y].`
- `(high-confidence items rated [4.17/5.0])`

### 12.5 Hedging language for honest claims
- `appears to be`
- `suggests that`
- `indicates that`
- `consistent with`
- `we see this as an example rather than proof`

### 12.6 "We" for author actions
Active voice with "we" for design decisions:
- `We model [X] as [Y].`
- `We design and implement [...]`
- `We prove by case-based analysis [...]`
- `We test the system by [...]`

### 12.7 Naming and quoting from the system
Quote actual outputs to make claims concrete:
- `The Coordinator put two croissant types at the top of the list (both high confidence).`
- `The Gap Analyst assigned low importance to cheesecakes, reasoning that the item "doesn't align with Punto's Asian-fusion concept."`

### 12.8 Lists with parallel grammar
Three-part lists are common, but with concrete tail variation:
- `[adjective 1], [adjective 2], and [adjective 3]`
- `(1) [action 1]; (2) [action 2]; and (3) [action 3]`

### 12.9 "This [behavior/result/case] shows / illustrates / demonstrates that..."
Immediately interpret each piece of evidence:
- `This case provides direct evidence that the framework integrates [A] and [B] together, rather than collapsing onto either alone.`
- `This emergent adaptivity is a direct consequence of LLM-based agents reasoning over [X], rather than applying fixed decision rules.`

### 12.10 Contrasting framing in adjacent sentences
Set up X then explicitly invert it:
- `[Their work] is [property X]. The setting that this work addresses, in which [property NOT-X], is out of the range of this body of literature.`

---

## 13. QUICK-REFERENCE PARAGRAPH SKELETONS

### 13.1 The "problem motivation" paragraph
1. State the topic and why it matters: *"The issue of [X] is a key choice in [domain]."*
2. List what it influences: *"The decision of [X] influences [a], [b] and [c]."*
3. Anchor in concrete setting: *"In [the rapidly expanding market of Y]..."*
4. Pivot to current practice: *"Nonetheless, in most [cases], these decisions are made by [informal method]..."*
5. Identify untapped resource: *"Meanwhile, a potent source of [X] has been left unexploited: [...]"*

### 13.2 The "gap identification" paragraph
1. Acknowledge prior work: *"Although many studies have been conducted on [field], and more recently the emergence of [trend]..."*
2. State the unresolved challenge count: *"...three challenges stand out as yet to be addressed..."*
3. Numbered/bolded list of gaps, each with: title — current state — why it fails.

### 13.3 The "contributions" paragraph
1. Bridge: *"Based on these observations, this paper presents [...]."*
2. Numbered list of contributions, each starting with a verb (We model / design / prove / test).
3. Roadmap: *"The rest of this paper is structured in the following way..."*

### 13.4 The "addressing a research gap" paragraph (Discussion)
1. Bold label: *"**Addressing Gap N ([Title]):**"*
2. State what the framework did: *"The framework produced [outcome] without relying on [absent resource]..."*
3. Cite evidence: *"Expert evaluation indicates that [...]."*
4. Interpret: *"These results suggest that [...]."*
5. Hedge the strength of the claim: *"To prove [a stronger claim], it needs to be tested on a larger scale."*

### 13.5 The "limitation" paragraph
1. Italic label: *"***[Limitation type].***"*
2. Acknowledge: *"The [aspect X] was [limited by Y] and may be incomplete."*
3. Constructive fix: *"[Concrete method Z] would allow [the framework] to [improve/scale]."*

---

## 14. WORDS AND PHRASES THAT APPEAR REPEATEDLY

These connectors give the paper its natural-sounding cadence. Reuse them.

**Transitions and pivots:**
- Nonetheless / Meanwhile / However / But / Notably / Practically / Initially / In contrast / In this landscape

**Citing literature:**
- presents / proposes / shows / points out / argues / suggests / provides / surveys / gives an extensive overview of

**Stating implications:**
- This [X] indicates that... / This shows that... / This implies... / These observations imply that... / The key point is that...

**Hedging:**
- appears to / seems to / may / suggests / likely / consistent with / supports the hypothesis that

**Distinguishing your work:**
- is fundamentally different / is inverted by our work / expands [X] to [Y] / addresses a gap that the surveyed literature fails to address

**Concretizing:**
- For example, ... / i.e., ... / e.g., ... / such as ... / namely, ...

---

## How to use this file

1. When you start writing a section, find the matching template in this file.
2. Copy the formula, then fill the bracketed slots with your own content.
3. Mix templates — most paper paragraphs are 3–5 of these chained together.
4. Lean on the "human-writing signatures" in Section 12 to avoid the flat, evenly-paced cadence that makes AI-written prose easy to spot.
5. Always anchor abstract claims with concrete numbers and named entities from your own work.
