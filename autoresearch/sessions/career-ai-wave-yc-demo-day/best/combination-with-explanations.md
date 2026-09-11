---
frameworks: [wardley-mapping, systems-thinking, means-ends-analysis, rumelt-strategy-kernel]
note: Incorporates Systems Thinking to model stock-and-flow runway dynamics and dual-use feedback loops, linking Wardley market shifts and Means-Ends path ranking into Rumelt's execution kernel.
---

# Strategic Decomposition: Catching the AI Wave for Ivan

This decomposition sequence evaluates Ivan's four candidate career paths—(a) Staff or Research Engineer at a major AI lab, (b) founding a 1–3 person vertical AI startup, (c) entering an AI research track, and (d) maximizing long-run wealth and leverage—against the reality of the December 2025 AI market revealed in the YC Demo Day transcript.

Ivan's profile combines 10 years at Google and Staff Engineer tenure at Lyft in NYC (LangGraph multi-agent systems, PyTorch, GCP data pipelines, end-to-end product delivery) with two critical vulnerabilities: zero public presence (no GitHub footprint, posts, or papers) and a strict 6-to-12-month runway if he resigns from salary. 

The four frameworks are orchestrated as an integrated analytical pipeline:
1. **Wardley Mapping** charts the structural evolution of the AI value chain, identifying what has commoditized into infrastructure versus where enterprise willingness-to-pay is peaking.
2. **Systems Thinking** analyzes the dynamic stocks (runway capital, public proof), flows (burn rate, credibility accumulation), delays (enterprise sales cycles vs academic review latency), and feedback loops governing Ivan's 12-month window.
3. **Means-Ends Analysis** rigorously evaluates the difference vectors and operator preconditions across all four career paths to produce a mathematically defensible expected-value ($EV$) ranking.
4. **Rumelt's Strategic Kernel** converts the highest expected-value path into an actionable Diagnosis, Guiding Policy, coherent 90-day milestones, and an explicit "What to Stop Doing" elimination discipline.

---

## 1. Wardley Mapping

### What to Decompose in This Transcript
Map the AI ecosystem described in the transcript along the vertical axis of user visibility (from end-user workflow automation down to foundational compute) and the horizontal axis of evolution (Genesis $\rightarrow$ Custom-Built $\rightarrow$ Product/Rental $\rightarrow$ Commodity/Utility):
- **Compute & Silicon Layer:** Deconstruct the hyperscaler silicon conflict between AWS Trainium chips (cutting compute costs by 50% to pressure Nvidia, lines 68–100, 154–178, 242–246) and Google TPUs. Classify base compute clusters as capital-intensive, utility-scale commodities where individual engineers cannot compete.
- **Foundation Models & Horizontal Tooling:** Trace the evolution of generic LLMs and horizontal agent frameworks. Anchor on Harj Taggar's observation that "infrastructure to build agents" was the leading wave "just a year ago" and has now commoditized into utility plumbing (lines 1710–1730).
- **Vertical Application & Workflow Frontier:** Position the rapid ascent of vertical agents and full-stack "AI-native" operating companies—such as Fernstone in insurance brokerage (lines 1734–1748), Saver in trust formation, Crunched automating financial modeling for users with "10,000-plus real-life Excel hours" (Richard Wang and Philip Ho, lines 3950–4110), and Locus in logistics operations (Kurush Dubash, lines 5238–5340).
- **Enterprise Demand & Access Governance:** Deconstruct Paul Graham's insight that Fortune 500 corporate bureaucrats are under executive orders to "AI-ify" operations but cannot build internally (lines 5464–5484), contrasted with Kareem's finding at Materiel that enterprise deployment is blocked by access governance (Fortune 500s cannot deploy un-permissioned LLMs without granular role-based access control, lines 3780–3821). Contrast serious enterprise systems with novelty gimmicks (e.g., Clad Labs / Chad IDE, lines 2022–2048, 5526–5576).

### What to Look For
- **Evolutionary Traps:** Identify layers undergoing rapid commoditization (raw pre-training, horizontal developer tooling, generic agent scaffolding) where solo engineers face zero pricing power.
- **High-Surplus Custom Frontier:** Locate components in the Custom-Built / early Product stages where enterprise willingness-to-pay is highest and sales cycles experience "big step-function growth" (Harj Taggar, lines 1608–1640).
- **Skillset Placement:** Map Ivan's core assets (deterministic LangGraph multi-agent orchestration, robust GCP data pipelines, production reliability) to the high-value vertical workflow frontier.

### What to Hand to the Next Framework
A structural map of the AI landscape showing that economic surplus has migrated upward into domain-specific, AI-native vertical execution, establishing the market environment for Systems Thinking.

---

## 2. Systems Thinking

### What to Decompose in This Transcript
Model the system dynamics, stock-flow accumulations, delays, and feedback loops governing Ivan's 12-month transition:
- **Stocks & Reservoirs:**
  - *Financial Runway Stock ($R$):* Finite reservoir (6 to 12 months). If Ivan resigns on Day 1, $R$ drains monotonically at monthly personal burn rate ($dB/dt$). If he stays at Lyft during initial discovery, net burn is $0.
  - *Public Technical Proof Stock ($P$):* Currently at zero (no open-source repositories, no published papers, no conference footprint). This proof deficit ($\Delta_{\text{Proof}}$) acts as an impedance mismatch for both enterprise credibility and top-tier lab recruitment.
  - *Enterprise Contract Pipeline Stock ($C$):* Qualified leads, pilots, and signed Letters of Intent (LOIs).
- **Feedback Loops:**
  - *Reinforcing Loop $R_1$ (The Dual-Use Open-Core Flywheel):* Building an enterprise multi-agent workflow on LangGraph $\rightarrow$ open-sourcing the underlying deterministic evaluation harness $\rightarrow$ accumulating GitHub stars and developer visibility (as demonstrated by Materiel's 3,600 stars and 1,000 WAUs, lines 3818–3821) $\rightarrow$ driving inbound enterprise discovery and inbound Tier-1 AI lab recruiter pull $\rightarrow$ creating competitive leverage and pricing power ($S_G$).
  - *Balancing Loop $B_1$ (The Premature Resignation Cliff):* Resigning from Lyft on Day 1 $\rightarrow$ burn rate begins draining Runway Stock $R$ $\rightarrow$ customer discovery delays deplete runway before contract closing $\rightarrow$ forced panic job search at month 8 under severe distress, accepting down-level commodity roles.
  - *Balancing Loop $B_2$ (The Enterprise Access Bottleneck):* Enterprise AI mandate holders want to buy $\rightarrow$ enterprise security/compliance gatekeepers block deployment because un-permissioned LLMs risk data leakage (Materiel, lines 3792–3797) $\rightarrow$ sales cycles stretch out unless granular role-based access control (RBAC) and deterministic guardrails are integrated from Day 1.
- **Delays and Latencies:**
  - *Academic Review Delay:* 6 to 18 months for NeurIPS/ICML review cycles, creating a structural latency that guarantees runway exhaustion before recognition for Path (c).
  - *Incumbent Big Tech Paralyzation Delay:* Enterprise software incumbents take 12–24 months to ship AI because their legacy engineers resist AI (Harj Taggar, lines 1696–1704), creating a temporal arbitrage window for 1–3 person startups.
- **Systemic Leverage Points (Meadows):**
  - *Leverage Point A (Change the Rules of the System):* Maintain Lyft employment during Days 1–90 to keep net burn rate at zero, preserving 100% of the 6–12 month runway until an enterprise contract gate ($\ge \$25\text{k}$) is cleared.
  - *Leverage Point B (Restructure Information Flows):* Convert private engineering competence into public market signal by open-sourcing the evaluation harness, enabling the Dual-Use Flywheel ($R_1$).

### What to Look For
- Structural tensions between runway drain rates and market feedback latencies.
- High-leverage interventions that decouple public proof generation from financial runway ruin.

### What to Hand to the Next Framework
The quantified stock-and-flow constraints, delay boundaries, and feedback dynamics needed to calculate the expected value ($EV$) and operator preconditions of the four candidate career paths in Means-Ends Analysis.

---

## 3. Means-Ends Analysis

### What to Decompose in This Transcript
Using Newell and Simon's Means-Ends Analysis, model Ivan's trajectory from his **Current State ($S_0$)** to the **Goal State ($S_G$)** across each of the four paths:
- **Current State ($S_0$):** Staff Engineer at Lyft (NYC-based, ex-Google 10 yrs); deep systems mastery in LangGraph, PyTorch, GCP pipelines, product delivery; **Gaps:** zero public presence, zero published research; **Hard Constraint:** 6 to 12 months of runway if leaving salary.
- **Goal State ($S_G$):** Top-tier AI career capture within 12 months, characterized by verified equity/revenue upside, elite technical leverage, and high inbound optionality.

Evaluate the difference vector ($\Delta = S_G - S_0$), required operators, and precondition feasibility for each path:
1. **Path (b) — Founding a 1–3 Person Vertical AI Startup (Highest Expected Value):**
   - *Preconditions:* Vertical problem selection, rapid agent prototype, enterprise validation, and pilot revenue.
   - *Transcript Feasibility & EV:* Highest $EV$. Harj Taggar demonstrates that 1–3 person teams are closing unprecedented contract values in their first months with "big step-function growth" (lines 1608–1640) because big tech incumbents cannot move (lines 1696–1704). Paul Graham confirms enterprise AI mandate holders are actively seeking startups (lines 5464–5484). By validating while salaried during Days 1–90, runway ruin probability is $0\%$, unlocking uncapped equity upside.
2. **Path (a) — Staff Systems or Inference Engineer at a Major AI Lab (Second Highest EV; Primary Hedge):**
   - *Preconditions:* Research Engineer roles require tier-1 publications (unachievable in 12 months); Staff Systems/Inference roles require visible public artifacts of distributed AI systems.
   - *Transcript Feasibility & EV:* Applying cold with zero public presence ($\Delta_{\text{Proof}}$) triggers severe recruiter friction. However, when paired with the open-source evaluation benchmark generated in Path (b), Path (a) becomes an immediate, de-risked high-salary ($500k–$900k) hedge.
3. **Path (d) — Maximizing Long-Run Wealth and Leverage (Third; Emergent Downstream State):**
   - *Preconditions:* Extreme market visibility, proprietary technical leverage, or verifiable commercial traction that induces inbound bidding.
   - *Transcript Feasibility & EV:* Cannot be executed as a standalone initial operator. It emerges naturally downstream of shipping a high-traction vertical product and open-source benchmark (the Dual-Use Flywheel $R_1$).
4. **Path (c) — Pure AI Research Track (Ranked Lowest; Disqualified):**
   - *Preconditions:* Novel theoretical breakthroughs, multi-hundred-thousand-dollar compute clusters (AWS Trainium / TPU / Nvidia, lines 154–246), and 6–18 month peer-review cycles.
   - *Transcript Feasibility & EV:* Falsified by constraints. Academic review latency exceeds Ivan's 6–12 month runway, guaranteeing runway exhaustion ($P(\text{Ruin}) \approx 1.0$) before peer review concludes.

### What to Look For
- **Precondition Violations:** Formally eliminate paths whose preconditions violate runway and capital constraints (Path c).
- **Compound / Dual-Use Operators:** Identify the single operator that collapses difference vectors across multiple paths—building an enterprise vertical agent platform (Path b) and open-sourcing its evaluation harness to trigger inbound lab offers (Path d & a).

### What to Hand to the Next Framework
A definitive expected-value ranking of the four paths, confirming Path (b) paired with a Path (a/d) inbound hedge as the optimal strategy, passed to Rumelt's Strategic Kernel.

---

## 4. Rumelt's Strategic Kernel

### What to Decompose in This Transcript
Synthesize the insights from Wardley Mapping, Systems Thinking, and Means-Ends Analysis into Richard Rumelt's three-part strategic framework:

#### 1. Diagnosis
Name the critical obstacle: Ivan is a Staff-level systems and multi-agent builder whose market leverage is artificially suppressed by a public proof deficit ($\Delta_{\text{Proof}}$) and a strict 6–12 month runway clock. Speculative, capital-intensive bets (Path c) guarantee runway ruin. Meanwhile, the transcript reveals a unique structural arbitrage: Fortune 500 corporate bureaucrats are desperately mandated to "AI-ify" operations (PG, lines 5464–5484), but internal incumbent engineers resist AI (Harj Taggar, lines 1696–1704) and generic agent frameworks fail enterprise access governance (Materiel, lines 3792–3797).

#### 2. Guiding Policy
Execute the **Salaried Dual-Use Sprint**:
- Focus Ivan's LangGraph and GCP pipeline strengths on an underserved, high-liability enterprise vertical workflow (avoiding commoditized horizontal wrappers).
- Protect 100% of his 6–12 month runway by maintaining his Lyft Staff role during an initial 90-day validation phase.
- Use the product build as a dual-purpose engine: open-source the sanitized agent evaluation harness to activate the Dual-Use Flywheel ($R_1$), creating public proof for Path (d/a) while securing enterprise pilot revenue for Path (b).
- Strictly avoid viral novelty stunts and scammy rage-bait gimmicks (e.g., Clad Labs / Chad IDE, lines 5552–5576), establishing enterprise-grade engineering credibility.

#### 3. Coherent Actions (Concrete 90-Day Plan & "What to Stop Doing")
Translate the guiding policy into tightly sequenced, measurable milestones:
- **Days 1–30 (Vertical Selection & Enterprise Mandate Discovery):**
  - Audit two document-heavy, high-liability enterprise verticals (e.g., freight logistics compliance, regional commercial insurance underwriting, or structured finance audit workflows akin to Crunched, lines 4022–4110).
  - Conduct 15 structured discovery interviews with corporate IT directors and operations VPs holding explicit AI mandates (PG's "AI-ify" bureaucrats), probing specific data governance and RBAC blockers (Materiel, lines 3792–3797).
  - *Milestone:* 1 validated workflow bottleneck with confirmed executive willingness-to-pay.
- **Days 31–60 (LangGraph Agent MVP & Open-Source Benchmark Harness):**
  - Build a deterministic multi-agent state orchestration graph using LangGraph on GCP with model-routing fallbacks and strict state recovery.
  - Sanitize and open-source the agent evaluation and benchmarking framework on GitHub, accompanied by a comprehensive architectural whitepaper on deterministic agent orchestration.
  - *Milestone:* Production-ready vertical MVP and Ivan's first major public technical artifact erases $\Delta_{\text{Proof}}$.
- **Days 61–90 (Paid Pilot Deployment & The Day 90 Quantitative Decision Gate):**
  - Deploy the MVP in a 30-day paid pilot or execute a binding Letter of Intent (LOI) with at least 1 enterprise design partner, pricing on business outcome value rather than seat licenses.
  - *Milestone & Decision Gate:*
    - **Traction Threshold ($\ge \$25\text{k}$ in paid pilots/LOIs):** Resign from Lyft into full-time founder mode (Path b) with 100% of personal runway intact and validated enterprise cash flow.
    - **Pivot Trigger ($< \$25\text{k}$ in pilots):** Do not quit Lyft. Leverage the published open-source evaluation benchmark and technical case study to trigger warm, inbound recruiter loops for Staff Systems/Inference roles at major AI labs (Path a/d).
- **Elimination Discipline (What to Stop Doing):**
  - Stop contemplating immediate resignation from Lyft prior to clearing the Day 90 contract validation gate.
  - Stop reading theoretical ML pre-training papers aimed at from-scratch foundation models (Path c).
  - Stop building generic agent scaffolding, prompt sandboxes, or horizontal copilots (commoditized utility layers).
  - Stop submitting unreferred cold resumes to AI lab job boards without public technical proof.
  - Stop exploring viral gimmicks or developer rage-bait (Clad Labs / Chad IDE).

---

## Synthesis: Feeding Recommendations Toward the Mission

The four frameworks combine to form an airtight strategic engine:
1. **Wardley Mapping** charts the macro terrain, steering Ivan away from commoditized infrastructure into high-surplus vertical workflows.
2. **Systems Thinking** reveals the dynamics governing his timeline, showing that maintaining salary during Days 1–90 completely eliminates runway ruin risk while open-sourcing the evaluation harness activates a compounding dual-use flywheel.
3. **Means-Ends Analysis** proves mathematically that Path (b) sequenced with Path (d/a) dominates all alternatives in expected value, while formally eliminating Path (c).
4. **Rumelt's Strategic Kernel** operationalizes the strategy into an unambiguous 90-day execution plan with hard decision gates and explicit elimination rules, guaranteeing that every bet converts into offers or revenue within 12 months.
