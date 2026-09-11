# Notes

## Insights
- Seed combination established: Rumelt's Strategic Kernel paired with Means-Ends Analysis. Rumelt strips market fluff to diagnose real defensibility and rank career paths against transcript evidence; Means-Ends Analysis chains recursive operators and sub-goals to bridge Ivan's zero-public-presence baseline to high-leverage outcomes within the 6–12 month runway limit.

## Human steering

- 2026-09-11T08:13:43Z: Lessons from earlier runs (observed in traces; avoid repeating):
  - Proposer (v2, all 3 experiments): read the transcript in 48 chunks and grepped each speaker name (38 greps), hit the recursion limit, experiment lost. Read only the first 150 lines plus at most five mission-driven greps; propose within 25 tool calls.
  - Judge scores are frozen per experiment; do not aim to re-argue the incumbent, aim at concrete deficiencies the judge listed (specificity, transcript grounding, 90-day measurability).
  - Operational: after a langgraph dev restart the pickled checkpointer resurrects old threads; the stale v2 run blocked the v3 run in `pending` for 8 min. Always list threads after a restart and delete strays before starting a new run.
