# Notes

## Insights
- Strategic landscape: YC Demo Day shows market evolution from horizontal agent infrastructure to applied vertical agents in unsexy operational domains (logistics, customer support, auditing) with rapid monetization velocity.
- Compute disparity: Frontier pretraining requires massive silicon investment (TPUs, Traneums, GPUs), while applied enterprise integration suffers from capability gaps in complex knowledge work—creating prime demand for production agent engineers.
- Path EV Ranking: For a Staff Engineer with 10y Google infra experience and 6–12m runway, Path (c) (from-scratch research) has lowest EV; Path (d) and Path (a) offer maximum immediate wealth/leverage without runway risk; Path (b) (unsexy vertical startup) is viable only if staged via customer discovery before resigning.
- Execution discipline: 90-day planning must chain backward from target inbound/revenue to concrete 30/60/90-day gates; runway discipline requires strict negative constraints ("what to stop doing") and pre-mortem failure prevention.

## Human steering
- 2026-09-11 (seeded before experiment 1 from the v2/v3 sessions on this transcript; obey literally)
- Each experiment must change the framework set: swap at least one framework or try a different pair. Never re-run a set already in experiments.tsv; a repeat is a wasted experiment. v3 kept rumelt-strategy-kernel + means-ends-analysis + inversion-premortem at experiment 3 and then spent five experiments swapping only the third framework, every one tied.
- The judge starts every dimension at the incumbent's frozen score and raises it only where the candidate quotably removes a deficiency the incumbent carries. Read best/score.json: aim the change at the deficiencies it lists, not at restating the incumbent through a different lens.
- Proposer budget: read only experiments.tsv, notes.md, best/combination-with-explanations.md and best/score.json; grep other attempts for their frontmatter only; read the transcript's first 150 lines and at most five greps, never the whole transcript. Stay under 25 tool calls. v3 proposer cost climbed from 393k to 693k tokens per round by re-reading prior attempts.
- Decompose: nobody reads the transcript whole and nobody reads a file twice; grep-selected hot windows only (at most 1,000 transcript lines in total), scouts read in one turn and write in the next, one decomposer handles all frameworks from the digests, no quote verification against the transcript (digests carry line numbers). Goal: the whole step under 200k tokens.
- Recommender: read best/recommendations.md only if you will write something materially different from it; always end the turn by writing the output file, never with a bare reply.
- Mission-specific: the rubric rewards a ranked comparison of the four paths with transcript line evidence, measurable 90-day milestones, runway discipline, and an explicit stop-doing list. Prefer frameworks that surface what the incumbent lacks on those dimensions (see best/score.json deficiencies) over frameworks that produce the same plan.
