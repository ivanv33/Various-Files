# Notes

## Insights
- Baseline (Exp 1: Rumelt + Means-Ends Analysis) scored 73/80 with 10/10 on transcript grounding. Tethering every path ranking, tripwire, and milestone to line-numbered transcript quotes (Taggar, Graham, Materiel, Crunch) is strictly required to preserve full grounding.
- Identified blind spots from Exp 1 deductions across the other seven rubric dimensions:
  - Specificity: Customer discovery must name exact operational sub-niches (fund administration, RIA compliance) and explicit buyer titles (VP Operations, CCO, Controller), not generic "financial operators".
  - Actionability & Sequencing: Enterprise pilot-to-cash conversions require realistic timelines (30–45 days, not 15 days) and pricing below discretionary thresholds ($10k–$20k) to bypass procurement freezes.
  - Runway Risk Discipline: Must quantify Ivan's exact monthly liquid burn in Brooklyn NYC (~$12k–$14k/mo) to define a hard dollar runway floor (minimum $75k liquid reserve).
  - Subtractive Focus: Must shed both corporate Lyft meetings/committees and 10-year Google Staff engineering habits (25-page architecture design docs, consensus-seeking, test over-engineering).
  - Frontier Lab Insight: Frontier labs view high-level wrappers (LangGraph) as toy abstractions; open-source artifacts must showcase low-level PyTorch systems, latency/error benchmarks, and GCP streaming data reliability.
  - Comparative Path Ranking: Path (d) must be evaluated against independent liquid wealth vehicles (late-stage pre-IPO unicorns, quant ML infrastructure) rather than collapsed purely into startup equity.
  - Mission Fit: Address geographic friction between NYC enterprise discovery/living costs and YC's mandatory in-person SF batch requirement.
- Triplet strategy (Exp 2: Rumelt + Means-Ends Analysis + Inversion Pre-Mortem): Inversion prospective hindsight ("assume Ivan is broke with zero revenue and zero offers in 12 months") directly dismantles optimism bias and engineers mandatory safeguards for every rubric deduction.

## Human steering

- 2026-09-11T08:13:43Z: Lessons from earlier runs (observed in traces; avoid repeating):
  - Proposer (v2, all 3 experiments): read the transcript in 48 chunks and grepped each speaker name (38 greps), hit the recursion limit, experiment lost. Read only the first 150 lines plus at most five mission-driven greps; propose within 25 tool calls.
  - Judge scores are frozen per experiment; do not aim to re-argue the incumbent, aim at concrete deficiencies the judge listed (specificity, transcript grounding, 90-day measurability).
  - Operational: after a langgraph dev restart the pickled checkpointer resurrects old threads; the stale v2 run blocked the v3 run in `pending` for 8 min. Always list threads after a restart and delete strays before starting a new run.
- 2026-09-11T08:25:14Z: Lessons from earlier runs (observed in traces; avoid repeating):
  - Proposer (v2, all 3 experiments): read the transcript in 48 chunks and grepped each speaker name (38 greps), hit the recursion limit, experiment lost. Read only the first 150 lines plus at most five mission-driven greps; propose within 25 tool calls.
  - Judge scores are frozen per experiment; do not aim to re-argue the incumbent, aim at concrete deficiencies the judge listed (specificity, transcript grounding, 90-day measurability).
  - Operational: after a langgraph dev restart the pickled checkpointer resurrects old threads; the stale v2 run blocked the v3 run in `pending` for 8 min. Always list threads after a restart and delete strays before starting a new run.
  - Decompose (v3 experiment 1) burned about 3.8M tokens: each framework subagent read the whole 6,400-line transcript and then carried it through every later call. From now on the decompose step follows the new decompose.md: four scout subagents each digest one 1,600-line slice into line-numbered quotes, framework subagents work from the digests and verify at most three 80-line windows, the merge reads only the per-framework files. Whole decompose step under 200k tokens; nobody reads the transcript whole, nobody reads a file twice.
- 2026-09-11T08:43:36Z: Lessons from earlier runs (observed in traces; avoid repeating):
  - Proposer (v2, all 3 experiments): read the transcript in 48 chunks and grepped each speaker name (38 greps), hit the recursion limit, experiment lost. Read only the first 150 lines plus at most five mission-driven greps; propose within 25 tool calls.
  - Judge scores are frozen per experiment; do not aim to re-argue the incumbent, aim at concrete deficiencies the judge listed (specificity, transcript grounding, 90-day measurability).
  - Operational: after a langgraph dev restart the pickled checkpointer resurrects old threads; the stale v2 run blocked the v3 run in `pending` for 8 min. Always list threads after a restart and delete strays before starting a new run.
  - Decompose (v3 experiment 1) burned about 3.8M tokens: each framework subagent read the whole 6,400-line transcript and then carried it through every later call. From now on the decompose step follows the new decompose.md: four scout subagents each digest one 1,600-line slice into line-numbered quotes, framework subagents work from the digests and verify at most three 80-line windows, the merge reads only the per-framework files. Whole decompose step under 200k tokens; nobody reads the transcript whole, nobody reads a file twice.
  - Decompose (v3 experiment 2, scout pipeline) still burned 1.12M tokens: the orchestrator read catalog.json and notes.md twice and peeked files before reading them; each scout read its slice in two calls and held it for four to five model turns (a 1,600-line slice is about 40k tokens per turn through read_file); each framework decomposer read all four digests twice and added verification windows. The rule now: the transcript is read only in grep-selected hot windows (at most 1,000 lines total), each scout reads in one turn and writes in the next, one decomposer handles all frameworks from the digests in three turns, and the orchestrator never reads the transcript or the catalog. Do not verify quotes against the transcript; the digests carry line numbers.
