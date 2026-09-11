---
frameworks: [wardley-mapping, means-ends-analysis, rumelt-strategy-kernel]
note: Seed combination: Wardley maps value chain shifts, Means-Ends ranks 4 paths against runway, Rumelt provides 90-day execution.
---

# Strategic Decomposition: Catching the AI Wave for Ivan

This decomposition sequence is designed to evaluate Ivan's four potential career paths—(a) Staff/Research Engineer at an AI lab, (b) founding a 1–3 person vertical AI startup, (c) entering an AI research track, and (d) maximizing long-run wealth and leverage—against the reality of the December 2025 AI market captured in the YC Demo Day transcript. 

Ivan's profile combines 10 years at Google and Staff Engineer status at Lyft (LangGraph multi-agent systems, PyTorch, GCP data pipelines, end-to-end execution) with two critical constraints: zero public presence and a strict 6-to-12-month runway if he leaves salary. The frameworks are applied in a strict sequential pipeline:
1. **Wardley Mapping** analyzes the macro shifts in the AI value chain revealed in the transcript, pinpointing where defensibility and willingness-to-pay reside versus what is commoditizing.
2. **Means-Ends Analysis** takes those market realities and tests the four career paths against Ivan's specific skills, credential deficits, and runway constraints to produce a rigorous expected-value ranking.
3. **Rumelt's Strategic Kernel** converts the highest expected-value path into a concrete, risk-mitigated strategy with explicit 90-day milestones and what to stop doing.

---

## 1. Wardley Mapping

### What to Decompose in This Transcript
Apply Wardley Mapping to the AI market landscape described throughout the transcript, positioning components along the vertical axis of user visibility (user need down to compute infrastructure) and the horizontal axis of evolution (Genesis $\rightarrow$ Custom-Built $\rightarrow$ Product/Rental $\rightarrow$ Commodity/Utility).

Specifically examine:
- **Compute and Hardware Layer:** The discussion of AWS purchasing Google TPUs versus pushing Amazon Trainium chips to challenge Nvidia's dominance (lines 68–100). Deconstruct how cloud infrastructure and base compute are evolving into commoditized, capital-intensive utilities.
- **Foundation Models and Tooling:** The maturation of base foundation models and generic agent-building scaffolding. Note Harj Taggar's observation that "infrastructure to build agents" was the wave "two batches ago / a year ago" and has now become table-stakes product/utility (lines 1710–1730).
- **Application and Workflow Layer:** Harj Taggar's breakdown of the shift toward vertical agents and full-stack "AI-native" businesses—such as Fernstone (AI-native insurance brokerage) and Saver (AI-native trust formation) (lines 1734–1748), as well as domain-specialized teams like Cunched (Richard Wang and Philip Ho combining McKinsey finance backgrounds with CS, lines 3950–4110) and Locus (Kurush Dubash, lines 5238–5340).
- **Enterprise Demand:** Paul Graham's insight that Fortune 500 organizations have corporate bureaucrats specifically mandated to "AI-ify" their operations who lack the internal capability to build (lines 5464–5484), contrasted with the failure modes of novelty/rage-bait tooling (e.g., Clad Labs / Chad IDE, lines 2022–2040, 5526–5574).

### What to Look For
- **Evolutionary Traps:** Identify layers undergoing rapid commoditization where an individual engineer without billions in compute cannot build defensibility (e.g., pure foundation model training, raw developer tooling, generic agent scaffolding).
- **High-Surplus Custom Frontier:** Locate the components in Custom-Built / early Product stages where enterprise willingness-to-pay is highest and sales cycles are compressed into "step-function contract growth" (Harj Taggar, lines 1608–1640).
- **Skillset Placement:** Map Ivan's core assets (LangGraph multi-agent orchestration, GCP data pipelines, end-to-end product delivery) against these evolutionary stages to identify where his skills produce immediate commercial leverage.

### What to Hand to the Next Framework
A clear map of the AI ecosystem showing that value has migrated upward from foundation models and generic infrastructure into domain-specific, AI-native vertical execution. This establishes the target operational environments and commercial viability baseline needed to evaluate the four candidate career paths in Means-Ends Analysis.

---

## 2. Means-Ends Analysis

### What to Decompose in This Transcript
Using Newell and Simon's Means-Ends Analysis, model Ivan's transition from his **Current State** to the **Goal State** across each of the four designated career paths:
- **Current State ($S_0$):** Staff Engineer at Lyft (NYC-based, ex-Google 10 yrs); deep systems mastery in LangGraph, PyTorch, GCP pipelines, product delivery; **Gaps:** zero public presence (no GitHub footprint, technical writing, or conference visibility), zero published research; **Hard Constraint:** 6 to 12 months of runway if leaving salary.
- **Goal State ($S_G$):** Top-tier AI career capture within 12 months, characterized by verified equity/revenue upside, elite technical leverage, and high inbound optionality.

Deconstruct each path by evaluating the distance between $S_0$ and $S_G$, the required operators, and whether operator preconditions can be satisfied within Ivan's 6–12 month runway:
1. **Path (a) — Staff or Research Engineer at a Major AI Lab:**
   - *Preconditions:* Research Engineer roles require proven research pedigree or top-tier conference publications (NeurIPS/ICML); Staff Systems/Inference roles require visible public artifacts of large-scale distributed AI systems or personal referrals.
   - *Feasibility:* Low immediate feasibility for Research Engineer; moderate for Systems Engineer, but blocked by the "zero public presence" gap when applying cold.
2. **Path (b) — Founding a 1–3 Person AI Startup in an Underserved Vertical:**
   - *Preconditions:* Vertical problem selection, rapid agent prototype, direct enterprise validation, and early revenue/LOIs.
   - *Transcript Evidence & Feasibility:* Highly viable. Harj Taggar emphasizes that small teams are securing unprecedented contract sizes in months because big tech incumbents cannot ship AI internally (lines 1608–1620, 1696–1704). Paul Graham confirms that enterprise buyers are actively seeking startups to solve operational bottlenecks (lines 5464–5484). Ivan's LangGraph and GCP pipeline strengths match the exact profile of full-stack AI-native builders (e.g., Fernstone, Saver, Cunched).
3. **Path (c) — AI Research Track (Papers, Open Models):**
   - *Preconditions:* Novel architectural or theoretical breakthroughs, massive GPU compute allocations, and academic review cycles (typically 6–18 months).
   - *Feasibility:* Falsified by constraints. With zero prior research track and a 6–12 month runway, attempting from-scratch academic research has an unacceptably high probability of runway exhaustion before recognition.
4. **Path (d) — Maximizing Long-Run Wealth and Leverage (Competing Offers, Inbound Optionality):**
   - *Preconditions:* Extreme market visibility, proprietary technical leverage, or verifiable commercial traction that induces inbound bidding.
   - *Feasibility:* Cannot be achieved as an isolated, passive path. It functions as a downstream consequence of shipping a high-impact, visible artifact or startup traction.

### What to Look For
- **Precondition Failures:** Eliminate or severely downgrade paths where preconditions cannot be cleared within 12 months without risking total runway ruin (specifically Path c).
- **Compound / Dual-Use Operators:** Identify actions that reduce difference vectors across multiple paths simultaneously—e.g., building a working, open-architecture AI-native vertical system simultaneously creates commercial traction (Path b) and generates the public technical proof required for elite inbound lab offers (Path d and Path a).

### What to Hand to the Next Framework
A definitive comparative ranking of the four paths for Ivan's profile:
1. **Highest Expected Value:** Path (b) — 1–3 person vertical AI startup, or a hybrid Path (b)/(d) execution where shipping an enterprise vertical agent product simultaneously generates business revenue and inbound talent leverage.
2. **Second:** Path (a) — Staff Systems/Inference Engineer at an AI lab (viable only after establishing public technical proof).
3. **Third:** Path (d) — Standalone offer shopping (unviable without prior proof).
4. **Disqualified / Ranked Lowest:** Path (c) — AI research track (preconditions violate the 12-month runway constraint).

Pass this ranked hierarchy and the key precondition bottlenecks to Rumelt's Strategic Kernel.

---

## 3. Rumelt's Strategic Kernel

### What to Decompose in This Transcript
Synthesize the insights from Wardley Mapping and Means-Ends Analysis into Richard Rumelt's three-part strategic core (**Diagnosis**, **Guiding Policy**, and **Coherent Actions**), grounding every decision in transcript evidence.

#### 1. Diagnosis
Name the critical obstacle: Ivan is an elite systems and multi-agent builder whose market value is artificially suppressed by an "agency and distribution bottleneck." He has no public footprint in an ecosystem where enterprise buyers and top labs require visible proof. Furthermore, his 6–12 month runway clock makes speculative, slow-feedback bets (pure research papers, unvalidated startup ideas) lethal. Meanwhile, the transcript reveals a unique structural arbitrage: enterprises desperately need practical AI-native workflow automation, but incumbent software engineers and big tech companies are paralyzed or skeptical (Harj Taggar, lines 1696–1704; Paul Graham, lines 5464–5484).

#### 2. Guiding Policy
Direct Ivan's multi-agent (LangGraph) and GCP data pipeline skills toward building an AI-native operational platform in an underserved enterprise vertical. Maintain his Lyft Staff salary during an initial 90-day de-risking phase (protecting his 6–12 month runway completely). Use this product as a dual-purpose vehicle:
- If enterprise traction and step-function contracts materialize (as Harj Taggar describes), fully commit to Path (b).
- Simultaneously, publish the underlying architectural blueprints, agent evaluation benchmarks, and systems learnings, converting his private expertise into public credibility to unlock Path (d) and Path (a) inbound opportunities.
- Strictly avoid cosmetic hype, rage bait, and scammy growth hacks (criticized by Paul Graham regarding Clad Labs, lines 5552–5574), anchoring entirely on high-craftsmanship, reliable systems engineering.

#### 3. Coherent Actions (Concrete 90-Day Plan & "What to Stop Doing")
Break the guiding policy into verifiable milestones:
- **Days 1–30 (Customer & Vertical Discovery while at Lyft):**
  - Select 2 underserved verticals (e.g., freight logistics, regulatory compliance, or specialized insurance/finance workflows akin to Fernstone and Cunched).
  - Conduct 15 discovery calls with domain operators and corporate managers holding AI mandates (targeting the "AI-ify" bureaucrats PG identified).
  - *Milestone:* One clearly defined operational bottleneck with confirmed willingness-to-pay.
- **Days 31–60 (LangGraph Agent MVP & Public Systems Benchmarking):**
  - Build a functioning end-to-end multi-agent workflow solving the target bottleneck using LangGraph and GCP.
  - Open-source a sanitized version of the agent evaluation harness and publish an in-depth technical case study on deterministic multi-agent orchestration.
  - *Milestone:* A working deployment-ready MVP and Ivan's first major public technical artifact.
- **Days 61–90 (Pilot Validation & The Runway Decision Gate):**
  - Deploy the MVP in a 30-day paid pilot or signed Letter of Intent (LOI) with at least 1 enterprise customer.
  - Assess traction: If a contract/LOI of $\ge \$25\text{k}$ is secured, transition to full-time founder (Path b) with runway intact. If enterprise sales stall, leverage the published technical artifact to trigger inbound conversations with AI lab recruiters (Path d/a).
  - *Milestone:* Signed contract/LOI or 3 tier-1 AI lab interview loops initiated.
- **What to Stop Doing (Resource Protection):**
  - Stop reading theoretical ML research papers aiming for from-scratch model training (Path c).
  - Stop cold-submitting resumes to AI labs without accompanying public technical artifacts.
  - Stop building generic, horizontal agent tooling or chat wrappers (avoiding the commoditized layers identified in Wardley Mapping).
  - Stop any thought of resigning from Lyft before clearing the Day 90 pilot/contract validation gate.

---

## Synthesis: Feeding Recommendations Toward the Mission

The three frameworks form a closed, reinforcing strategic loop:
1. **Wardley Mapping** filters out commoditized distractions (raw chips, generic LLMs, horizontal agent frameworks) and identifies the profit pool in vertical AI-native applications.
2. **Means-Ends Analysis** eliminates wishful thinking by proving that Path (c) research fails runway constraints, while proving that Path (b) (vertical AI startup) sequenced with Path (d/a) (inbound leverage from public artifacts) is the mathematically superior expected-value path.
3. **Rumelt's Kernel** translates this optimal path into an immediate, risk-free 90-day operational playbook, protecting Ivan's salary, curing his public presence deficit, and positioning him to capture the AI wave within the 12-month window.
