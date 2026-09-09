# Decomposition Frameworks

Twenty-two decomposition frameworks documented as knowledge-graph schemas. Each one has a folder with a README (the framework, two worked examples, and how to build a knowledge graph with it), a `graph.json` (the examples as data), and a self-contained Three.js page that renders the examples as an interactive graph. Open [`index.html`](./index.html) for the overview, or pick a framework from the table below.

The one question every page answers: **when text is turned into a graph using this framework as the schema, which nodes and edges come straight from the data, and which must an LLM derive?**

## Why

The frameworks will later be run over the TBPN transcript corpus in this repository (`../tbpn-transcripts/`, 252 episodes plus per-episode LLM extractions) to generate ideas and to identify business opportunities, underserved markets and startup ideas. For that to be trustworthy, every graph has to keep the line between evidence and reasoning visible. So every example here is grounded twice: a classic textbook case, and a real moment from the transcripts with quotes that the validator checks against the file.

## Provenance in one paragraph

Every node and every edge is `fact` or `derived`. A fact is stated in the source and carries a verbatim quote and a reference. A derived item is LLM reasoning the source does not contain and carries a confidence and a rationale. Derived nodes point at the facts that support them through `supported_by` edges. Framework scaffolding that is neither (the six Ishikawa categories, the Cynefin domains) is marked `schema` and drawn grey. In every graph page the "LLM-derived" toggle hides the reasoning layer, and what remains must still be true to the source. The full rules are in [SPEC.md](./SPEC.md) section 3.

## The frameworks

<!-- FRAMEWORK_TABLE_START -->
| Category | Framework | What it does | Graph | Status | TBPN example |
|---|---|---|---|---|---|
| Narrative | [STAR / PAR](01-narrative-and-statement/star-par/README.md) | Dissects past events into Situation (context), Task (objective), Action (execution), and Result (outcome). Enforces causal attribution and clarifies personal agency. | [graph](01-narrative-and-statement/star-par/index.html) | missing |  |
| Narrative | [CARL](01-narrative-and-statement/carl/README.md) | Extends STAR into Context, Action, Result, and Learning. Extracts double-loop systemic rules to prevent repeat failures. | [graph](01-narrative-and-statement/carl/index.html) | missing |  |
| Narrative | [Minto SCQA](01-narrative-and-statement/minto-scqa/README.md) | Structures problem statements into Situation (stable baseline), Complication (disruption), Question (core inquiry), and Answer (solution). Aligns stakeholders before pitching solutions. | [graph](01-narrative-and-statement/minto-scqa/index.html) | missing |  |
| Narrative | [Pyramid Principle](01-narrative-and-statement/pyramid-principle/README.md) | Structures communication top-down. States the governing conclusion first, supported by mutually exclusive, logically grouped pillars to reduce working memory load. | [graph](01-narrative-and-statement/pyramid-principle/index.html) | missing |  |
| Narrative | [Toulmin Model](01-narrative-and-statement/toulmin-model/README.md) | Deconstructs arguments into Claim (assertion), Grounds (evidence), Warrant (logical bridge), Backing (proof of rule), Qualifier (certainty bounds), and Rebuttal (disqualifying conditions). Exposes hidden assumptions. | [graph](01-narrative-and-statement/toulmin-model/index.html) | missing |  |
| Narrative | [Dialectical Decomposition](01-narrative-and-statement/dialectical-decomposition/README.md) | Pitches an orthodoxy (Thesis) against its critique (Antithesis) to isolate the core tension and derive an integrated higher-order solution (Synthesis). Eliminates false dichotomies. | [graph](01-narrative-and-statement/dialectical-decomposition/index.html) | missing |  |
| Strategic | [MECE Principle](02-strategic-and-business/mece/README.md) | Partitions a problem into branches that are Mutually Exclusive (no overlaps) and Collectively Exhaustive (no blind spots). Prevents duplicate effort and omission. | [graph](02-strategic-and-business/mece/index.html) | missing |  |
| Strategic | [Issue & Hypothesis Trees](02-strategic-and-business/issue-hypothesis-trees/README.md) | Hierarchical decision maps that break problems into testable branches. Hypothesis trees define specific falsification conditions to avoid aimless data gathering. | [graph](02-strategic-and-business/issue-hypothesis-trees/index.html) | missing |  |
| Strategic | [5 Whys](02-strategic-and-business/five-whys/README.md) | Traces a single failure through five sequential causal layers to uncover institutional and systemic flaws rather than stopping at human error. | [graph](02-strategic-and-business/five-whys/index.html) | missing |  |
| Strategic | [Ishikawa (Fishbone) Diagram](02-strategic-and-business/ishikawa-fishbone/README.md) | Categorizes root causes across six universal vectors: Methods, Machines, Materials, Measurements, Milieu, and Manpower. Prevents technical monoculture bias. | [graph](02-strategic-and-business/ishikawa-fishbone/index.html) | missing |  |
| Strategic | [Rumelt's Strategic Kernel](02-strategic-and-business/rumelt-strategy-kernel/README.md) | Strips buzzwords from strategy to define a Diagnosis (the critical obstacle), a Guiding Policy (the trade-offs and overall direction), and Coherent Actions (mutually reinforcing resource commitments). | [graph](02-strategic-and-business/rumelt-strategy-kernel/index.html) | missing |  |
| Strategic | [Theory of Constraints & Evaporating Cloud](02-strategic-and-business/theory-of-constraints/README.md) | Identifies the single operational bottleneck dictating systemic throughput. The Evaporating Cloud diagram resolves chronic trade-offs by identifying and breaking invalid assumptions. | [graph](02-strategic-and-business/theory-of-constraints/index.html) | missing |  |
| Engineering | [First Principles Thinking](03-engineering-and-cognitive/first-principles/README.md) | Strips away industry precedent and analogy to isolate fundamental physical or mathematical truths, rebuilding solutions upward from fundamental limits. | [graph](03-engineering-and-cognitive/first-principles/index.html) | missing |  |
| Engineering | [Functional Decomposition](03-engineering-and-cognitive/functional-decomposition/README.md) | Treats systems as hierarchical black boxes with strict inputs, outputs, and interface contracts. Minimizes coupling and isolates blast radiuses. | [graph](03-engineering-and-cognitive/functional-decomposition/index.html) | missing |  |
| Engineering | [Pólya's 4-Step Method](03-engineering-and-cognitive/polya-four-step/README.md) | Understand (data/unknowns), Plan (analogous/simpler cases), Carry Out (verifiable steps), and Look Back (generalizing the heuristic). Prevents premature coding or calculating. | [graph](03-engineering-and-cognitive/polya-four-step/index.html) | missing |  |
| Engineering | [Means-Ends Analysis](03-engineering-and-cognitive/means-ends-analysis/README.md) | Continuously evaluates the distance between the current state and goal state, recursively chaining operators and creating sub-goals to remove preconditions. | [graph](03-engineering-and-cognitive/means-ends-analysis/index.html) | missing |  |
| Engineering | [Inversion & Pre-Mortem](03-engineering-and-cognitive/inversion-premortem/README.md) | Assumes complete future failure (prospective hindsight), lists every pathway to disaster, and engineers mandatory safeguards in advance. Overcomes optimism bias. | [graph](03-engineering-and-cognitive/inversion-premortem/index.html) | missing |  |
| Sensemaking | [Cynefin Framework](04-sensemaking-and-complex-systems/cynefin/README.md) | Categorizes environments to match decision protocols: Clear (Sense-Categorize-Respond), Complicated (Sense-Analyze-Respond), Complex (Probe-Sense-Respond), and Chaotic (Act-Sense-Respond). Prevents applying rigid blueprints to emergent spaces. | [graph](04-sensemaking-and-complex-systems/cynefin/index.html) | missing |  |
| Sensemaking | [Wardley Mapping](04-sensemaking-and-complex-systems/wardley-mapping/README.md) | Maps user needs vertically by visibility and horizontally along an evolution axis (Genesis -> Custom -> Product -> Utility). Exposes custom components that should be commoditized utilities. | [graph](04-sensemaking-and-complex-systems/wardley-mapping/index.html) | missing |  |
| Sensemaking | [OODA Loop](04-sensemaking-and-complex-systems/ooda-loop/README.md) | Observe, Orient, Decide, Act. Focuses on Orientation (mental models, cultural conditioning) to execute decision cycles faster than an adversary or shifting market. | [graph](04-sensemaking-and-complex-systems/ooda-loop/index.html) | missing |  |
| Sensemaking | [PDCA / Deming Cycle](04-sensemaking-and-complex-systems/pdca-deming/README.md) | Plan (hypothesis), Do (contained pilot), Check (statistical measurement), and Act (standardize or pivot). Prevents unverified global rollouts. | [graph](04-sensemaking-and-complex-systems/pdca-deming/index.html) | missing |  |
| Sensemaking | [Systems Thinking](04-sensemaking-and-complex-systems/systems-thinking/README.md) | Analyzes dynamics via Stocks (reservoirs), Flows (rates of change), and Feedback Loops (balancing vs. reinforcing). Targets systemic leverage points (information flows, rules, goals) rather than tweaking surface parameters. | [graph](04-sensemaking-and-complex-systems/systems-thinking/index.html) | missing |  |
<!-- FRAMEWORK_TABLE_END -->

## Where the idea shows up

Each framework has one slot where, applied to a transcript, the opportunity or the underserved need surfaces. This table is the raw material for a later cross-framework idea layer; a shared Opportunity node type was considered and deferred (see SPEC section 12).

<!-- IDEA_SLOTS_START -->
| Framework | Idea-bearing slot | TBPN example | Derived nodes in that slot (confidence) |
|---|---|---|---|
| [STAR / PAR](01-narrative-and-statement/star-par/README.md) | | | |
| [CARL](01-narrative-and-statement/carl/README.md) | | | |
| [Minto SCQA](01-narrative-and-statement/minto-scqa/README.md) | | | |
| [Pyramid Principle](01-narrative-and-statement/pyramid-principle/README.md) | | | |
| [Toulmin Model](01-narrative-and-statement/toulmin-model/README.md) | | | |
| [Dialectical Decomposition](01-narrative-and-statement/dialectical-decomposition/README.md) | | | |
| [MECE Principle](02-strategic-and-business/mece/README.md) | | | |
| [Issue & Hypothesis Trees](02-strategic-and-business/issue-hypothesis-trees/README.md) | | | |
| [5 Whys](02-strategic-and-business/five-whys/README.md) | | | |
| [Ishikawa (Fishbone) Diagram](02-strategic-and-business/ishikawa-fishbone/README.md) | | | |
| [Rumelt's Strategic Kernel](02-strategic-and-business/rumelt-strategy-kernel/README.md) | | | |
| [Theory of Constraints & Evaporating Cloud](02-strategic-and-business/theory-of-constraints/README.md) | | | |
| [First Principles Thinking](03-engineering-and-cognitive/first-principles/README.md) | | | |
| [Functional Decomposition](03-engineering-and-cognitive/functional-decomposition/README.md) | | | |
| [Pólya's 4-Step Method](03-engineering-and-cognitive/polya-four-step/README.md) | | | |
| [Means-Ends Analysis](03-engineering-and-cognitive/means-ends-analysis/README.md) | | | |
| [Inversion & Pre-Mortem](03-engineering-and-cognitive/inversion-premortem/README.md) | | | |
| [Cynefin Framework](04-sensemaking-and-complex-systems/cynefin/README.md) | | | |
| [Wardley Mapping](04-sensemaking-and-complex-systems/wardley-mapping/README.md) | | | |
| [OODA Loop](04-sensemaking-and-complex-systems/ooda-loop/README.md) | | | |
| [PDCA / Deming Cycle](04-sensemaking-and-complex-systems/pdca-deming/README.md) | | | |
| [Systems Thinking](04-sensemaking-and-complex-systems/systems-thinking/README.md) | | | |
<!-- IDEA_SLOTS_END -->

## Viewing

- `index.html` and every framework page open from the file system. The graph pages load Three.js from jsDelivr, so they need internet access; the graph data is embedded in each page.
- On GitHub the README links work directly; the graph pages need GitHub Pages or a local clone.
- In a graph page: drag to orbit, wheel to zoom, right-drag to pan, hover for a summary, click a node for its quote or rationale. Keys: `d` toggles derived nodes, `g` toggles grounding links, `r` resets the view. URL parameters set the initial state: `?example=1&derived=0&grounding=1`.

## Rebuilding

```bash
node _meta/validate.mjs --all      # schema, provenance rules, quotes verified against the transcripts
node _meta/build.mjs --all         # re-embed every graph.json into its index.html (engine changes propagate)
node _meta/build-index.mjs         # regenerate index.html and the tables in this README
node _meta/status.mjs              # progress table (--write refreshes _meta/state.json)
node _meta/snap.mjs <framework-dir> # headless screenshots and legibility metrics (needs `npm install` in _meta once and Chrome, Brave, Chromium or Edge)
```

## How it was built, and how to resume

The build is agent-driven and every step is committed. One framework agent per slug runs a scout (finds the transcript moment), writes the graph, then a README writer and a viz builder in parallel; the viz builder is judged by an independent critic in a loop until the critic passes; then the folder is reconciled and committed. Each framework's `state.json` records which steps are done. To resume after an interruption, run `node _meta/status.mjs` and relaunch `_meta/AGENT_BRIEF.md` Part A for any slug that is not `done`. The full contract is [SPEC.md](./SPEC.md).

## Future: one large graph

Out of scope now, kept possible by design: node ids namespace as `<slug>/<example>/<node>`, `entities` use the names from the transcript extractions, every TBPN example carries its file and date, and provenance and confidence sit on every node and edge. The open questions are listed in SPEC section 12.
