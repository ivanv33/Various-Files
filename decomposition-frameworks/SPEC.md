# Decomposition Frameworks: Spec and Agent Contract

Status: approved design, 2026-09-08. This file is the single contract for every agent that works in this folder. Read it fully before writing anything.

## 1. Purpose

Twenty-two decomposition frameworks (STAR, Toulmin, MECE, 5 Whys, Wardley, Systems Thinking, ...) documented as a reference library with one recurring question answered for each: **when we turn text into a knowledge graph using this framework as the schema, which nodes and edges come straight from the data (facts) and which must an LLM derive (reasoning that the data alone does not contain)?**

End goal, stated by the owner: these framework graphs will later be applied to the TBPN transcript corpus in this repo (`tbpn-transcripts/transcripts/`, 252 episodes, plus per-episode LLM extractions in `tbpn-transcripts/extractions/`) to generate ideas and identify business opportunities, underserved markets and startup ideas. Merging all framework graphs into one large graph is a future step, explicitly out of scope now, but nothing here may make it harder (see section 12).

## 2. Deliverables

```
decomposition-frameworks/
  README.md                  root: purpose, provenance rules, index of the 22, idea-bearing slots table, future-merge notes, how to resume
  index.html                 landing page: 22 cards by category, links to each README and graph page, status badges
  SPEC.md                    this file
  _meta/
    frameworks.json          registry of the 22: slug, name, category, blurb, wikipedia URL, slots, relations, layout hint
    schema.json              JSON Schema (2020-12) for graph.json; validate.mjs is the enforcing implementation
    graph-engine.html        Three.js viewer template; each framework's index.html is this template plus embedded data
    build.mjs                node _meta/build.mjs <framework-dir> | --all : embeds graph.json into index.html between markers
    validate.mjs             node _meta/validate.mjs <framework-dir> | --all : schema, provenance rules, quote verification
    status.mjs               node _meta/status.mjs : scans state.json files, prints the resume table; --write refreshes _meta/state.json (orchestrator only)
    build-index.mjs          node _meta/build-index.mjs : regenerates index.html from the registry and states
    snap.mjs                 node _meta/snap.mjs <framework-dir> : headless screenshots of every example and toggle state + legibility metrics (report.json) into _meta/.snaps/<slug>/ (git-ignored); needs `npm install` in _meta once and a Chromium-based browser (Chrome, Brave, Chromium or Edge in /Applications, or CHROME_PATH)
    package.json             puppeteer-core for snap.mjs; node_modules/ is git-ignored
    commit-framework.sh      _meta/commit-framework.sh <framework-dir> "<message>" : commits one folder, retries on index.lock
    AGENT_BRIEF.md           the prompt a framework agent receives; parameterised by slug; used for launch and for resume
    sample/                  a synthetic graph.json used only to prove the engine; not a framework
  01-narrative-and-statement/<slug>/       README.md  graph.json  index.html  state.json
  02-strategic-and-business/<slug>/
  03-engineering-and-cognitive/<slug>/
  04-sensemaking-and-complex-systems/<slug>/
```

Per framework, exactly four files. `graph.json` is the single source of truth: the README's examples and the HTML page are both derived from it and must match it exactly. `index.html` is self-contained (data embedded, Three.js from a pinned CDN URL, no fetch), so it opens from `file://` and from GitHub Pages.

## 3. Provenance model

Every node and every edge carries `provenance`, one of two values:

- `fact`: the content is stated in the source. For the TBPN example the source is one transcript file. For the classic example the source is the short scenario text embedded in the example itself. A fact node must carry `source_quote`, a verbatim span copied from the source (at least 5 words), and `source_ref`, a free-text pointer (speaker, approximate position, or line). If a fact is only paraphrasable (spread over several turns), set `paraphrase: true` and still give `source_ref`; at most 30% of the fact nodes in an example may be paraphrases.
- `derived`: the content is produced by LLM reasoning and is not stated in the source. A derived node must carry `confidence` (0 to 1) and `rationale` (why this inference follows from the facts).

Edges follow the same rule, with a precise criterion: an edge is `fact` only when both endpoints are fact nodes and one speaker's turn states the connection, quoted verbatim in the edge's `source_quote` ("we lost the deal because the demo crashed"). Everything else is `derived` with `confidence`: a link the LLM infers, a link that joins two speakers, a sequence read from narrative order, and any edge that touches a derived node.

Grounding links: an edge with relation `supported_by` runs from a derived node to a fact node and is always `derived` (the judgment that a fact supports an inference is itself an inference). Every derived node should have at least one `supported_by` edge or a direct edge to a fact node; the validator warns when a derived node is not connected to any fact.

The viewer's "hide LLM-derived" toggle shows what the data alone gives you: it hides derived nodes, every edge touching them, and derived edges between fact nodes. What remains visible must still be true to the source.

The framework's own slot structure (for example that Toulmin has a Warrant slot) is schema, not provenance. Provenance is about the content of a specific node.

Edges touching a schema node may themselves be `schema` when the relationship is definitional rather than judged: a step belonging to a PDCA phase, a cause hanging on its Ishikawa category rib. Where the placement is a judgment (which Cynefin domain a situation falls in, which Wardley stage a component sits at) the edge is `derived` with a confidence. The validator accepts `schema` on an edge only when an endpoint is a schema node.

Registry additions: seven relations and one slot were added by framework agents during the build, each for the same reason (every registry relation for that framework originated at a derived node, so facts could not connect to facts); they are marked `added_during_build` in `_meta/frameworks.json` and are part of the schema.

One narrow exception for scaffolding: some frameworks draw their fixed categories as nodes (the six Ishikawa categories, the four Cynefin domains, Wardley's evolution stages, Pólya's and PDCA's phases). Such a slot is marked `structural: true` in the registry, and its nodes carry `provenance: "schema"`. Schema nodes are neither facts nor inferences; they need no quote, confidence or rationale, they are drawn as neutral grey markers, they stay visible when derived items are hidden, and they are excluded from the fact/derived counts. Only slots flagged structural may use `schema`; content never may.

Why binary and not three-way: a "hybrid" class blurs the rule agents apply. When a slot is partly stated and partly inferred, split it: a fact node for the stated part and a derived node for the inferred part, linked by `supported_by`.

Confidence scale, shared by every framework so a later merge can compare it:

| band | meaning |
|---|---|
| 0.90 to 1.00 | the inference is nearly forced by the quoted facts (arithmetic, a direct implication, a restatement the framework requires) |
| 0.70 to 0.85 | a standard reading most careful readers would share: causation or sequence stated adjacently, the general rule an argument needs in order to work |
| 0.50 to 0.65 | plausible but contestable: counterfactuals, generalised needs, links across speakers or across segments |
| below 0.50 | speculative; keep only when the framework requires the slot to be filled, and say so in the rationale |

Where the idea lives: a derived node in the example's `idea_bearing_slot` may carry an `idea` field, one sentence naming the underserved need, market shift or startup idea that node implies. The node's `text` stays framework content (a rebuttal is still a rebuttal, a task is still the actor's task); the idea is the reading of it. Never add nodes whose only content is an idea. Every TBPN example should have at least one node with `idea`; the root README's idea table is generated from them.

Source references: for transcripts, `source_ref` names the speaker when identifiable and the line range in the file as `L<start>-L<end>` (1-based lines of the .md file); for the classic scenario text, `sentence <n>`. `entities` lists every company, person or product the node names, spelled as in `tbpn-transcripts/extractions/`; an empty list is fine when the node names none.

## 4. graph.json

Normative structure is in `_meta/schema.json`; this section explains it.

```jsonc
{
  "framework": { "slug", "name", "category", "wikipedia", "one_liner" },
  "slots": [ { "id", "label", "description", "typical_provenance": "fact|derived|either", "color"?: "#hex", "shape"?: "sphere|box|diamond|cone" } ],
  "relations": [ { "id", "label", "description" } ],          // supported_by is reserved and implicit
  "examples": [
    {
      "id": "classic", "kind": "classic", "title", "summary",
      "source": { "type": "text", "title", "text" },          // the scenario text that fact nodes quote
      "layout": { ... }, "nodes": [ ... ], "edges": [ ... ]
    },
    {
      "id": "tbpn", "kind": "tbpn", "title", "summary",
      "source": { "type": "transcript", "file": "tbpn-transcripts/transcripts/<file>.md", "date": "YYYY-MM-DD", "episode_title", "url"? },
      "why_this_episode": "...",
      "idea_bearing_slot": "<slot id>",                          // where the opportunity/idea surfaces in this framework
      "insights": { "short": "...", "long": "..." },             // the formula, spelled out; short heads the README and the page, long heads the Insights card
      "layout": { ... }, "nodes": [ ... ], "edges": [ ... ]
    }
  ]
}
```

Node fields:

| field | required | notes |
|---|---|---|
| id | yes | unique within the example; short (`n1`, `claim`, `why3`) |
| slot | yes | must match a slot id |
| label | yes | 40 characters or fewer; what the viewer prints next to the node |
| text | yes | the full statement, 1 to 3 sentences |
| provenance | yes | `fact` or `derived`; `schema` only in a slot marked `structural: true` |
| source_quote | fact | verbatim span from the source; validator checks it is present after whitespace and punctuation normalisation |
| source_ref | fact | speaker, position, or line pointer; free text |
| paraphrase | fact, optional | `true` allows a non-verbatim `source_quote`; capped at 30% of fact nodes |
| confidence | derived | 0 to 1 |
| rationale | derived | why the inference follows; at least 20 characters |
| entities | optional | company, person or product names as they appear in `tbpn-transcripts/extractions/`; the hook for future merging |
| idea | derived, optional | one sentence: the underserved need, market shift or startup idea this node implies; normally only in the idea-bearing slot |
| level | layout, optional | tree mode; 0 is the root layer |
| order | layout, optional | ring mode; 0..n-1 around the circle |
| pos | layout, optional | `[x, y]` or `[x, y, z]`, world units, recommended range -50..50 |
| size | optional | multiplier, default 1 |

Edge fields: `id`, `from`, `to`, `relation`, `provenance`, plus `confidence` (derived, required), `source_quote` and `source_ref` (fact, required: the span in which one speaker states the connection; `paraphrase: true` allowed under the same 30% cap, counted together with nodes), and optional `label` (printed on the edge, e.g. loop polarity `+`/`-`) and `rationale`.

Layout object:

```jsonc
{
  "mode": "force | tree | ring | plane",
  "root": "<node id>",            // tree: BFS levels are computed from here when nodes lack level
  "direction": "down | right",    // tree
  "axes":    { "x": { "label", "min", "max", "ticks": [ { "value", "label" } ] }, "y": { ... } },   // plane
  "regions": [ { "label", "x": [x0, x1], "y": [y0, y1], "color": "#hex" } ],                    // plane
  "guides":  [ { "from": [x, y], "to": [x, y], "style": "solid | dashed", "label"? } ],          // plane
  "camera":  { "distance": 160 }  // optional
}
```

Size limits: 8 to 30 nodes per example, at least nodes-1 edges. Bigger graphs are unreadable in the viewer; smaller ones do not show the framework.

## 5. The viewer (graph-engine.html)

Single file. Three.js r0.186 loaded through an import map from jsDelivr (`three` and `three/addons/`). No fetch calls, data is embedded in `<script id="graph-data" type="application/json">` between the markers `<!--__DATA_START__-->` and `<!--__DATA_END__-->`. Framework-specific code may be added between `<!--__EXT_START__-->` and `<!--__EXT_END__-->`; the build never touches that block. The extension block may define `window.__frameworkExtension = (ctx) => { ... }` where `ctx` exposes `{ THREE, scene, graph, example, nodesById, api }` and is called after each example is laid out.

Visual language, fixed by the engine, not by the framework page:

- Node colour = slot. Fact nodes: solid opaque sphere. Derived nodes: translucent sphere plus wireframe halo.
- Fact edges: solid. Derived edges: dashed. `supported_by`: thin dotted, dim, and hidden by default behind a toggle.
- Directed edges get an arrow cone at the target.
- Labels: always-on short labels (CSS2D), full text in the side panel on click.

Controls: orbit (drag), zoom (wheel), pan (right-drag). Hover highlights the node and its edges. Click opens a side panel: slot, provenance badge, full text, and either quote plus reference or rationale plus confidence and the list of supporting facts. Toggles: show LLM-derived (default on), show grounding links (default off), labels, auto-rotate. Example selector switches between the examples. Keyboard: `d` toggles derived, `g` toggles grounding, `r` resets the camera. A stats line shows fact/derived counts for nodes and edges.

Layout modes: `force` (deterministic seeded spring layout in 3D, `pos` pins a node), `tree` (layers by `level` or BFS from `root`, spread along x, `direction` down or right), `ring` (nodes by `order` on a circle, unlisted nodes force-placed inside), `plane` (explicit `pos`, plus axes, regions and guides drawn on z=0). Camera auto-fits the bounding box; `layout.camera.distance` overrides.

URL parameters set the initial state, for deep links and for scripted screenshots: `?example=<index or id>&derived=0|1&grounding=0|1&labels=0|1&rotate=0|1`.

## 6. README.md template (per framework)

Sections in this order. Headings are fixed; prose is the author's.

```
# <Framework name>
> One-line definition. Category: <category name>. Reference: <wikipedia link>. [Open the 3D graph](./index.html) (needs internet for Three.js; on GitHub open via Pages or clone).

## What this graph derived
Two paragraphs, the transcript example first, then the classic: each is that example's `insights.short` verbatim, the formula spelled out: given these facts, applying this method, we derived these things, and the opportunity that falls out. See `_meta/AGENT_BRIEF.md` Part G. The library exists for this paragraph; everything below it is how the paragraph was earned.

## What it decomposes
Two or three paragraphs: what kind of object the framework takes apart, what it forces you to make explicit, what goes wrong without it.

## The slots
Mermaid diagram of the generic structure, then a table: Slot | What goes here | Typical provenance | Why that provenance.

## Example 1: <classic title>
### Source text
The scenario text, verbatim from graph.json source.text, in a blockquote.
### Decomposition
One entry per node in graph.json, grouped by slot, each tagged [fact] or [derived 0.xx]. Facts show the quote. Derived items show the rationale.
### What the LLM added and why it helps
Which derived nodes and edges exist, what reasoning they encode, and what a reader gains that the source text did not give.

## Example 2: from the TBPN transcripts: <title>
Episode title, date, relative link to the transcript file (../../../tbpn-transcripts/transcripts/<file>.md), and why this episode fits this framework (from the scout's evidence).
### Facts (quoted)
One entry per fact node, grouped by slot: id, label, text, the verbatim quote, the source_ref. Fact edges are listed here too with their quoted connective.
### Decomposition
One entry per derived node, grouped by slot: id, label, text, [derived 0.xx], rationale, and the ids of the facts it is supported by. Derived edges are listed after the nodes. Fact nodes are referenced by id, not repeated.
### What the LLM added
### Where the opportunity shows up
Name the idea-bearing slot and list every node that carries an `idea` field: the idea sentence, the node it is read from, its confidence. Read them as candidate ideas or underserved needs.

## Building a knowledge graph with this framework
### Node and edge types
Mapping of slots to node types and relations to edge types, as used in graph.json.
### Fact or derived: rules of thumb
Per slot: when it is normally extracted and when it must be inferred; what to do when a slot is empty in the data.
### Extraction recipe
A prompt skeleton an LLM can run over a transcript chunk to produce graph.json-shaped output for this framework, and the checks to run afterwards.
### Failure modes
How an LLM misapplies this framework (invented facts, over-confident inferences, slot confusion) and the guard for each.

## Related frameworks
Two to four sibling frameworks with relative links, one line each on when to prefer which.
```

Length: 1,500 to 3,000 words of prose. The per-node decomposition entries, the quoted source text, the mermaid diagram and the code blocks are mandated content and do not count toward the cap. Plain GitHub markdown. No content in the README may contradict graph.json; node texts, provenance and confidences must match exactly.

## 7. Registry

`_meta/frameworks.json` lists the 22 frameworks with slug, name, category, blurb, wikipedia URL, the default slot list with typical provenance, default relations, and a layout hint. Agents may refine slot descriptions and add a slot when the framework genuinely needs it, but must keep the registry's slot ids so the frameworks stay comparable. Categories and slugs:

| Category | Slugs |
|---|---|
| 01-narrative-and-statement | star-par, carl, minto-scqa, pyramid-principle, toulmin-model, dialectical-decomposition |
| 02-strategic-and-business | mece, issue-hypothesis-trees, five-whys, ishikawa-fishbone, rumelt-strategy-kernel, theory-of-constraints |
| 03-engineering-and-cognitive | first-principles, functional-decomposition, polya-four-step, means-ends-analysis, inversion-premortem |
| 04-sensemaking-and-complex-systems | cynefin, wardley-mapping, ooda-loop, pdca-deming, systems-thinking |

The registry deliberately contains no suggested transcript examples. Finding the example is the agent's own separate step (section 8, scout).

## 8. Agent protocol

Three levels. The orchestrator (the main session) owns `_meta/`, `SPEC.md`, the root `README.md` and `index.html`. One framework agent per slug owns that slug's folder. Each framework agent runs three children.

### 8.1 Framework agent (parent)

Inputs: slug, absolute repo path, this spec, `_meta/AGENT_BRIEF.md`, its registry entry, `_meta/schema.json`.

Steps, each idempotent so a relaunch continues from the last completed step recorded in `state.json`:

1. **Start.** Read the spec, brief, registry entry and schema. If `state.json` exists, read it and skip completed steps. Write `state.json` with `status: in_progress`.
2. **Research.** Recall the framework precisely: origin, slots, what each slot forces, the classic textbook usage. Fetching the Wikipedia page is optional.
3. **Scout (separate step, own child).** Launch the scout child. It searches the corpus and returns three ranked candidate moments with evidence (section 8.2). The parent chooses one, or relaunches the scout with feedback if none fits. Record the choice in `state.json`.
4. **Graph.** Write `graph.json` with both examples. Run `node _meta/validate.mjs <dir>` and fix until it passes with no errors. Warnings must be read and either fixed or justified in `state.json.notes`.
   Commit: `scaffold(<slug>): graph.json and state`.
5. **Fan out.** Launch the README child and the viz builder child in parallel (sections 8.3, 8.4). They read `graph.json` from disk; do not paste it into their prompts. When the README child finishes, commit `readme(<slug>): first draft`.
6. **Viz loop.** Run the builder-critic loop of section 8.4 until the critic passes or the iteration cap is hit. Every builder iteration and every critic verdict is a commit.
7. **Reconcile.** Read the README and `index.html`. Check every example entry in the README against `graph.json` (texts, provenance, confidences, quotes). Confirm the viz loop changed only layout fields (compare `graph.json` with layout fields stripped against the scaffold commit). Check links resolve (transcript path, sibling framework paths, wikipedia). Run validate and build again. Fix or send the child back with a message.
8. **Finish.** Write `state.json` with `status: done` and every step marked. Commit `Add framework: <Name> (<slug>)`. Report (section 8.5).

### 8.2 Scout child (example discovery)

Goal: find the single best moment in the TBPN corpus for this framework. "Best" means the framework's structure is genuinely present in the source (a completed event for STAR, an argument with contestable warrant for Toulmin, a stated conflict for the Evaporating Cloud, a visible bottleneck for TOC), the speakers give enough verbatim material to fill most slots with facts, and the moment has a business angle where a derived slot can yield an idea, an underserved need or a market shift.

Method: keyword search `tbpn-transcripts/extractions/*.json` (structured: companies, people, topics, key_claims per episode) to shortlist episodes, then read the matching transcript files in `tbpn-transcripts/transcripts/` to confirm and to harvest verbatim quotes. Transcript file names begin with the episode date; extraction files are named by date. Some dates have two episodes.

Output: three candidates, ranked, each with: transcript file, date, episode title, a two-sentence case for why it fits this framework's structure, 6 to 10 verbatim quotes (copied exactly, with speaker or position) with the slot each would fill, the entities involved, and the idea angle. The parent picks one.

### 8.3 README child

Inputs: paths to spec, registry entry, `graph.json`, and the README template (section 6). Writes `README.md` only. Must not edit `graph.json`. If it finds a problem in `graph.json`, it reports it back rather than fixing it.

### 8.4 Viz builder and viz critic (a loop, every step committed)

The page is built by a **viz builder** child and judged by an independent **viz critic** child. The loop runs until the critic passes or five iterations have run. The parent drives it:

1. **Builder iteration n.** The builder sets the `layout` object and the layout fields on nodes (`level`, `order`, `pos`, `size`), slot colours and shapes, and any decor (axes, regions, guides) so the page renders in the framework's native shape. It may write an extension block in `index.html` for a visual the data-driven engine cannot express. It may shorten a node's `label` (40 characters or fewer, meaning preserved; `text` untouched). It may edit only those fields; never a node's text, provenance, quotes, rationale, edges or ids. It runs `node _meta/validate.mjs <dir>`, `node _meta/build.mjs <dir>` and `node _meta/snap.mjs <dir>`, looks at its own screenshots and metrics, fixes what it can see, and reports what it changed and why. On iterations after the first it works from the critic's blocking issues (the parent continues the same builder agent with a message, so it keeps context).
2. **Commit** `viz(<slug>): iteration <n>` with the builder's summary as the body.
3. **Critic iteration n.** A fresh agent every time, given only the rubric below, the spec's viewer section, and the paths. Continue the same builder between iterations when a message tool is available; when it is not, launch a fresh builder and give it the critic's blocking issues plus a one-paragraph summary of what the previous builder already changed. It runs `node _meta/snap.mjs <dir>` itself, reads the screenshots (all examples, default and facts-only and grounding and panel states), `report.json` and `graph.json`, and returns a verdict. It never edits files and never sees the builder's reasoning.
4. **Record and commit.** The parent appends the verdict to `state.json.viz_reviews` and commits `viz-review(<slug>): iteration <n> <pass|revise>`.
5. **Loop or stop.** `pass`: done. `revise` and n < 5: back to step 1 with the blocking issues. n = 5 and still `revise`: stop, record `critic not satisfied after 5 iterations` in `state.json.notes`, include the last verdict in the report; the orchestrator decides.

Critic rubric. Each criterion scored 1 to 5; pass needs every score at 4 or above, no blocking issues, a clean console in `report.json`, and metrics at default view of at most one overlapping label pair per example, zero off-screen labels, zero labels under the cards.

| Criterion | What a 5 looks like |
|---|---|
| Demonstrates the framework | The native shape is recognisable at a glance (a pyramid is a pyramid, a cloud is the five-box cloud, a Wardley map has its two axes) and the slots read in the order the framework prescribes. |
| Shows the fact/derived idea | With derived hidden, what remains is a coherent, source-true skeleton; with derived shown, the LLM's additions are visibly the bridges, causes, qualifiers or leaps the framework exists to surface. The idea-bearing slot is easy to find. |
| Legibility | Labels readable and not colliding at the default camera, nothing clipped or hidden under the legend or the note, edge directions clear, decor (axes, regions, guides) correct and unobtrusive. |
| Fidelity | The page reflects `graph.json` exactly (counts match the stats line), both examples switch cleanly, the panel shows quotes for facts and rationale plus confidence for inferences, no console errors. |

The critic's verdict is JSON: `{ "verdict": "pass" | "revise", "scores": { "demonstrates": n, "provenance": n, "legibility": n, "fidelity": n }, "blocking_issues": ["..."], "suggestions": ["..."], "summary": "..." }`. Blocking issues must be concrete and actionable (which node to move where, which label to shorten, which decor to add), not taste.

### 8.5 Report format

The parent's final message to the orchestrator:

```
slug: <slug>   status: done | failed
tbpn example: <date> <episode title> (<file>)
nodes: classic <n> (<f> fact / <d> derived), tbpn <n> (<f>/<d>)
validate: pass, <k> warnings (<one line on each>)
viz: <n> iterations, final verdict <pass|revise>, scores <demonstrates/provenance/legibility/fidelity>
commits: <count>, last subject <...>
limitations: <engine limits hit, slots that fit badly, anything the reviewer should look at>
```

### 8.6 Rules for every agent

- Write only inside your framework folder. Never edit `_meta/`, `SPEC.md`, other framework folders, or anything outside `decomposition-frameworks/`.
- Never run `git add -A`, `git commit` or any git write command directly. The only allowed git write is `_meta/commit-framework.sh` on your own folder. Reading git is fine.
- Every fact must be a verbatim span from the cited source, or a flagged paraphrase within the cap. No invented quotes. When in doubt, mark it derived.
- Keep node labels to 40 characters; put the substance in `text`.
- Do not add files beyond the four. Scratch work goes to a per-framework subfolder of the session scratchpad (`<scratchpad>/<slug>/`); sibling agents share the scratchpad.
- Do not move or park files to make a commit "pure". The commit script stages the whole folder; a `readme(...)` commit may carry the viz builder's in-progress files and vice versa. That is expected.
- Absolute paths in every command. The repo root is passed in the brief.

## 9. State and resumability

`state.json` per framework, committed with the folder:

```json
{
  "slug": "toulmin-model",
  "status": "pending | in_progress | done | failed",
  "steps": { "research": "done", "scout": "done", "graph": "done", "validate": "done", "readme": "done", "viz": "done", "reconcile": "done", "commit": "done" },
  "tbpn_example": { "file": "...", "date": "2025-..", "episode_title": "..." },
  "viz_iterations": 2,
  "viz_reviews": [ { "iteration": 1, "verdict": "revise", "scores": { "demonstrates": 4, "provenance": 3, "legibility": 2, "fidelity": 5 }, "blocking_issues": ["..."], "at": "2026-09-08T00:00:00Z" } ],
  "updated_at": "2026-09-08T00:00:00Z",
  "notes": "justified warnings, engine limits, anything a resumer needs",
  "issues": []
}
```

`node _meta/status.mjs` scans all 22 folders and prints a table (slug, status, last step, example); the orchestrator runs it with `--write` to refresh `_meta/state.json`. To resume after an interruption: run status, then relaunch a framework agent with `_meta/AGENT_BRIEF.md` for each slug not `done`. The parent's steps are idempotent, so a relaunch continues from the recorded state.

## 10. Git protocol

- Branch: the current feature branch. No PR; the owner merges.
- Framework agents commit only their own folder through `_meta/commit-framework.sh`, which runs `git add -- <dir>` and `git commit -m <msg> -- <dir>` (path-limited commit, so files staged by other agents are not swept in) and retries with backoff when `index.lock` is held by a concurrent agent.
- Commit subjects, in order per framework: `scaffold(<slug>): graph.json and state`, `readme(<slug>): first draft`, `viz(<slug>): iteration <n>`, `viz-review(<slug>): iteration <n> <pass|revise>`, `content(<slug>): <what changed>` for any change to node or edge content after the scaffold (a quote extended, an edge reclassified, a review fix), then the final `Add framework: <Name> (<slug>)` whose body gives the example chosen, the node counts and the number of viz iterations. The reconcile check compares the current `graph.json` against the last `scaffold` or `content` commit with layout fields and labels stripped. The script appends the co-author trailer itself; do not add one by hand.
- The orchestrator commits `_meta/`, `SPEC.md`, the root README and `index.html` in its own commits.

## 11. Validation and review

Automated, `validate.mjs`: structure per schema; slug and category match the folder; slot and relation references resolve; node counts 8..30; fact nodes have quotes present in the source (normalised: lowercase, straight quotes, punctuation stripped, whitespace collapsed) or are flagged paraphrases within the 30% cap; derived nodes have confidence and rationale; fact edges join two fact nodes and quote their connective (verified the same way); derived edges have confidence; `supported_by` runs derived to fact; every derived node connects to a fact (warning); `idea` only on derived nodes, and at least one in the TBPN example's idea-bearing slot (warning); transcript `source_ref` carries a line range (warning); layout fields consistent with the mode; transcript file exists and its date prefix matches `source.date`; `idea_bearing_slot` resolves; labels within 40 characters (warning).

Wave review: after each category wave, a review agent reads every README and graph.json of the wave against this spec and reports violations and weak spots (thin rationale, slot confusion, an example that does not exhibit the framework, prose that contradicts the data). Fixes go back to the same framework agent by message so it keeps its context.

Visual check: `snap.mjs` gives every builder and critic the same headless screenshots and metrics (label overlaps, off-screen labels, labels under cards, console errors), so pages are judged the same way whether or not a browser pane is available. The orchestrator additionally opens a sample of pages per wave in the browser pane.

## 12. Future: merging into one large graph

Out of scope now. Decisions here keep it possible:

- Node ids are unique only within an example; a merged graph namespaces them as `<slug>/<example id>/<node id>`.
- `entities` on nodes use the names from `tbpn-transcripts/extractions/` so entity resolution can join across frameworks and episodes.
- Every TBPN example carries its transcript file and date, so time is a dimension of the merged graph.
- Provenance and confidence are on every node and edge, so a merge can keep the fact/derived boundary intact.
- The root README lists each framework's idea-bearing slot, the raw material for a later cross-framework idea layer (the shared Opportunity node was considered and deferred).

Open questions to settle then: slot equivalence classes across frameworks (which claim-like slots are the same kind of thing), confidence propagation across supported_by chains, storage (property graph vs RDF), and how episode-level facts extracted once are shared by many framework applications.

## 13. Out of scope

Applying the frameworks to the whole corpus, the merge, the idea-ranking pipeline, GitHub Pages configuration, vendoring Three.js, any change outside `decomposition-frameworks/`.
