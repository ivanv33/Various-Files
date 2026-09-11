---
frameworks: [rumelt-strategy-kernel, means-ends-analysis, inversion-premortem]
note: Seed combination coupling strategic path-ranking and trade-offs with backward milestone planning and prospective failure-mode safeguards.
---

# Strategic Career Acceleration: AI Wave Navigation for Ivan

This decomposition pipeline coordinates three frameworks in strict sequence:
1. **Rumelt's Strategic Kernel**: Diagnoses market dynamics from the YC Demo Day transcript against Ivan's specific profile, formulates a guiding policy that explicitly compares and ranks the four open career paths, and outlines coherent actions.
2. **Means-Ends Analysis (MEA)**: Takes the strategic path ranking and chains backward from the 12-month goal state to current reality, defining concrete operator transitions and testable 30-, 60-, and 90-day milestones.
3. **Inversion & Pre-Mortem**: Stress-tests the execution plan through prospective hindsight at Month 12, isolating failure pathways, establishing strict runway preservation guardrails, and defining an explicit "what to stop doing" list.

---

## 1. Rumelt's Strategic Kernel (`rumelt-strategy-kernel`)

### What to Decompose in this Transcript
Deconstruct the macroeconomic and venture landscape captured during the December 2025 YC Demo Day transcript into structural market forces, and contrast them with Ivan's specific capabilities and constraints:
- **Transcript Diagnosis**:
  - *Frontier vs. Applied Divergence*: Heavy capital consolidation in foundation model compute (TPU v7, Traneum 3, Nvidia clusters, lines 70–135) contrasts with enterprise integration bottlenecks, where frontier models still exhibit severe capability gaps in end-to-end knowledge work (lines 1260–1262).
  - *Batch Evolution*: YC shifts decisively away from generic "infrastructure for building agents" (the prior batch trend, lines 1712–1724) toward "vertical agents taking off" in unsexy operational domains like logistics, customer operations, and auditing (lines 1728–1738, 1880), emphasizing full-stack AI-native execution and rapid revenue ramps over horizontal developer tooling.
  - *Monetization Velocity*: High variance between teams demonstrating rapid revenue ramps ($41k usage revenue in two weeks, line 4738; enterprise contract velocity, line 1624) versus teams caught in vanity metrics or willfully ignoring monetization (line 3626).
- **Candidate Obstacle**:
  - Ivan possesses deep distributed engineering competence (10 years at Google, Staff at Lyft, LangGraph, GCP, PyTorch), but is encumbered by zero public footprint, zero foundational research publications, and a tight 6-to-12-month cash runway if departing employment.

### What to Look For
- Specific signals in the transcript contrasting high-friction paths (e.g., frontier research requiring massive custom silicon clusters) with high-leverage paths (production multi-agent workflows solving unsexy enterprise workflows).
- Evidence distinguishing sustainable business/career advantage from commoditized wrapper layers.

### What to Hand Off
- A diagnostic assessment establishing the relative viability of the four paths:
  1. **Path (d) Maximising long-run wealth & leverage / Path (a) Major AI Lab Staff/Research Engineer**: Highest immediate EV. Leverages Google/Lyft pedigree and LangGraph production expertise to capture top-tier lab offers without burning runway.
  2. **Path (b) Founding 1–3 Person Vertical AI Startup**: High upside but high runway risk; must be pursued opportunistically or staged via customer validation before resigning.
  3. **Path (c) AI Research Track (from-scratch papers/models)**: Lowest EV. Fails the 12-month horizon due to lack of compute scale and absence of foundational research track record.
- Clear strategic trade-offs (what not to do) handed to Means-Ends Analysis to structure the milestone progression.

---

## 2. Means-Ends Analysis (`means-ends-analysis`)

### What to Decompose in this Transcript
Chain backward from Ivan's required 12-month end state to his current baseline by identifying differences, preconditions, and concrete operators:
- **Current State ($S_0$)**: Brooklyn-based Staff Engineer at Lyft; 10 years at Google; production LangGraph and GCP pipeline builder; zero external portfolio, zero public writing, no external inbound pipeline; 6–12 months cash runway buffer.
- **Goal State ($S_G$)**: Secured high-leverage position (Staff/Research Engineer at a frontier lab or well-capitalized AI scaleup with competing offers) OR a de-risked vertical AI startup with validated customer revenue, achieved within 12 months without depleting personal runway.
- **Difference Reduction**:
  - *Difference 1 (Visibility & Inbound)*: From zero external presence to recognized authority in production multi-agent systems.
    - *Operator*: Publish open-source reference implementations, architectural deep dives, and production benchmarks addressing agent reliability bottlenecks highlighted in the transcript (lines 1260–1262).
  - *Difference 2 (Validation of Domain EV)*: From theoretical path comparison to concrete market offers.
    - *Operator*: Target hiring managers at major labs deploying applied agent infrastructure, while simultaneously probing unsexy vertical operational pain points (lines 1728–1738).
  - *Difference 3 (Runway Security)*: From binary career risk to staged de-risking.
    - *Operator*: Execute portfolio generation and market discovery while retaining current Lyft compensation until concrete offers or binding pilot contracts emerge.

### What to Look For
- Measurable 30-, 60-, and 90-day progress metrics that directly demonstrate difference reduction (e.g., GitHub stars on a LangGraph production template, inbound recruiter screens, enterprise pilot discovery interviews).

### What to Hand Off
- A sequenced, testable 90-day execution roadmap with quantitative milestone gates handed to Inversion & Pre-Mortem to audit for blind spots and failure modes.

---

## 3. Inversion & Pre-Mortem (`inversion-premortem`)

### What to Decompose in this Transcript
Apply prospective hindsight by asserting complete failure at Month 12: Ivan has burned through his runway, secured no major lab offers, generated no startup revenue, and damaged his career momentum. Trace the exact failure pathways revealed by the transcript:
- **Failure Pathway 1: The Research Trap (Path c failure)**: Spending 6–9 months attempting to publish novel research or train boutique models from scratch without the dedicated TPU/GPU cluster backing discussed in the transcript (lines 70–135), yielding rejected conference submissions and exhausted savings.
- **Failure Pathway 2: The Horizontal Dev-Tool Trap (Path b failure mode A)**: Quitting Lyft early to build generic agent developer tooling or IDE wrappers (lines 1712–1724, 32–40) that face brutal competition from subsidized YC batches and rapid model capability absorption.
- **Failure Pathway 3: Premature Resignation & Burnout**: Leaving employment at Month 0 on a 6-month runway clock without inbound leverage, leading to desperate low-equity compromises at Month 5.
- **Failure Pathway 4: Stealth Engineering without Commercial Feedback**: "Willfully ignoring revenue" (line 3626) and polishing internal architectures rather than closing unsexy enterprise contracts or building public visibility.

### What to Look For
- Concrete transcript failure modes where founders or engineers mistook hype for defensibility or neglected distribution and unit economics.
- Safeguards that can be formulated as strict negative constraints ("what to stop doing").

### What to Hand Off to Recommendations
- An explicit **"What to Stop Doing"** list:
  1. Stop spending discretionary hours studying theoretical foundation model pre-training from scratch; focus exclusively on applied agent orchestration, evaluation, and latency/reliability infrastructure.
  2. Stop building generic horizontal agent tools or prompt frameworks; focus on vertical domain pain points.
  3. Stop building in private: eliminate unshared local repos.
  4. Do NOT leave full-time employment at Lyft until either (a) two competing offers are received or (b) contracted pilot revenue covers baseline monthly burn.
- Mandatory runway guardrails and kill criteria embedded into the 90-day action plan.

---

## Synthesis & Recommendations Blueprint

The recommendations derived from this decomposition must:
1. **Rank the 4 Paths with Transcript Grounding**: Rank Path (d) and Path (a) as primary vehicles for wealth and leverage, Path (b) as a staged secondary option in unsexy verticals, and Path (c) as disqualified for Ivan's 12-month constraint.
2. **Prescribe a Phased Dual-Track Strategy**: Maintain Staff employment at Lyft while building public LangGraph/agent orchestration credibility to trigger inbound lab interest, while probing unsexy enterprise workflows.
3. **Detail 90-Day Milestones**:
   - *Days 1–30*: Ship an open-source, production-grade LangGraph orchestration harness solving multi-agent reliability and tool-calling failure modes; author a technical deep dive.
   - *Days 31–60*: Leverage the artifact for targeted outreach to AI lab engineering leaders and unsexy vertical B2B discovery; target 5 recruiter screens and 10 customer discovery calls.
   - *Days 61–90*: Convert pipeline into 2+ formal technical interviews / offer loops or a committed paid pilot; trigger final path decision based on firm offer valuation vs. validated customer contract.
4. **Enforce Runway Discipline and Stop-Doing Mandates**: Codify negative gates to ensure zero runway depletion before offer or revenue realization.
