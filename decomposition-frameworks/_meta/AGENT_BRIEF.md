# Agent brief

The orchestrator launches one **framework agent** per slug with Part A, substituting the placeholders. The framework agent launches its children with Parts B to E. Part F is the orchestrator's wave-review prompt. Every prompt refers to `DF` = `<repo>/decomposition-frameworks`. Placeholders: `{{SLUG}}`, `{{NAME}}`, `{{CATEGORY}}`, `{{REPO}}` (absolute repo root).

To relaunch after an interruption: `node DF/_meta/status.mjs`, then send Part A again for every slug not `done`. The agent reads `state.json` and continues from the first step not marked done.

---

## Part A: framework agent

```
You are the framework agent for {{NAME}} (slug {{SLUG}}, category {{CATEGORY}}). You produce this framework's folder and nothing else.

Paths, all absolute:
- Repo root: {{REPO}}
- Library root DF: {{REPO}}/decomposition-frameworks
- Your folder: DF/{{CATEGORY}}/{{SLUG}}   (create it if missing)
- Read fully before anything else, in this order: DF/SPEC.md, DF/_meta/AGENT_BRIEF.md (this brief), your entry in DF/_meta/frameworks.json, DF/_meta/schema.json.
- Corpus: {{REPO}}/tbpn-transcripts/transcripts/*.md (252 episodes, file names start with the date) and {{REPO}}/tbpn-transcripts/extractions/*.json (per-episode structured extractions named by date).

You produce exactly four files in your folder: graph.json, README.md, index.html, state.json (SPEC sections 2, 4, 6, 9).

Ground rules (SPEC 8.6): write only inside your folder; never edit DF/_meta, DF/SPEC.md or other folders (plain `node DF/_meta/status.mjs` is read-only and fine; never pass --write); the only git write you may perform is `bash DF/_meta/commit-framework.sh <your folder> "<subject>" "<body>"`; every fact node quotes the source verbatim (the validator checks); no files beyond the four; scratch work goes to a per-framework subfolder of your session scratchpad (`<scratchpad>/{{SLUG}}/`, because sibling agents share the scratchpad; tell your children the same); use absolute paths in commands. Do not move or park files to make a commit pure: the commit script stages your whole folder, and a readme commit carrying the viz builder's in-progress files (or the reverse) is expected. Use the same model as you for children (do not pass a model override).

Resume rule: if state.json exists, read it first and continue from the first step not marked done. Every step below is safe to repeat.

Procedure (SPEC 8.1):
1. Start. Read the four documents. If any other framework folder under DF has state.json with status "done", read its README.md and graph.json once for house style. Write state.json with status "in_progress", slug, empty steps, updated_at.
2. Research. Recall the framework precisely: origin, its slots and what each forces you to make explicit, the classic textbook use, common misuse. Fetching the Wikipedia page is optional. Mark steps.research done.
3. Scout, as its own step. Launch one child with Part B (Agent tool, subagent_type "general-purpose", run_in_background false). Read its three candidates. Choose one, or relaunch the scout with feedback if none fits. Record tbpn_example {file, date, episode_title} in state.json; mark steps.scout done.
4. Graph. Write graph.json with both examples (kind "classic" with its own source.text of at least 200 characters that the classic facts quote; kind "tbpn" citing the chosen transcript). Keep the registry's slot ids. Run `node DF/_meta/validate.mjs <your folder>` and fix until it prints 0 errors; read every warning and fix or justify it in state.json.notes. Commit: `bash DF/_meta/commit-framework.sh <your folder> "scaffold({{SLUG}}): graph.json and state"`. Mark steps.graph and steps.validate done.
5. Fan out. Launch the README child (Part C) and the viz builder child (Part D) in parallel (both run_in_background true, then wait for both). When the README child reports, confirm README.md exists and commit `readme({{SLUG}}): first draft`. Mark steps.readme done. Note the viz builder's agent id: you will continue it by message in the loop.
6. Viz loop (SPEC 8.4). For n = 1, 2, ... up to 5:
   a. After the builder reports iteration n, commit `viz({{SLUG}}): iteration n` with the builder's summary as the body.
   b. Launch a fresh critic with Part E (run_in_background false). Parse its JSON verdict. Append it (with "iteration": n and "at": ISO time) to state.json.viz_reviews, set viz_iterations = n, and commit `viz-review({{SLUG}}): iteration n <pass|revise>`.
   c. If the verdict is pass: stop the loop. If revise and n < 5: send the builder agent the continuation message in Part D (the blocking issues and suggestions), wait for its report, continue with n + 1. If n = 5 and still revise: write "critic not satisfied after 5 iterations" plus the last verdict into state.json.notes and stop.
   Mark steps.viz done.
7. Reconcile. Read README.md and index.html. Check every example entry in the README against graph.json: node texts, provenance tags, confidences, quotes. Confirm the viz loop changed only layout fields (`jq 'del(.examples[].layout) | del(.examples[].nodes[].pos, .examples[].nodes[].level, .examples[].nodes[].order, .examples[].nodes[].size) | del(.slots[].color, .slots[].shape)'` on the current file and on the scaffold commit's version, `git show <sha>:<path>`, must be identical). Check links resolve (transcript path, sibling paths, wikipedia). Run validate and build once more. Fix small things yourself; send a child back by message for larger ones. Mark steps.reconcile done.
8. Finish. Set state.json status "done", updated_at, and every step done. Commit `Add framework: {{NAME}} ({{SLUG}})` with a body giving the example chosen, node counts per example (fact/derived), and the number of viz iterations. Mark steps.commit done (write state.json before the commit so it is included).

If you are blocked (validator cannot pass, no fitting example after two scout runs, the engine cannot express the layout), record it in state.json.issues and notes, set status "failed" if you cannot finish, and report precisely what is missing.

Final report, exactly this shape:
slug: {{SLUG}}   status: done | failed
tbpn example: <date> <episode title> (<file>)
nodes: classic <n> (<f> fact / <d> derived), tbpn <n> (<f>/<d>)
validate: pass, <k> warnings (<one line on each>)
viz: <n> iterations, final verdict <pass|revise>, scores <d/p/l/f>
commits: <count>, last subject <...>
limitations: <engine limits hit, slots that fit badly, anything the reviewer should look at>
```

---

## Part B: scout (example discovery)

```
You are the scout for the framework {{NAME}} ({{SLUG}}). Your only job is to find the single best moment in the TBPN transcript corpus to demonstrate this framework and hand back verbatim material. You write no files in the repository.

Read: DF/SPEC.md section 8.2, and the {{SLUG}} entry in DF/_meta/frameworks.json (its slots say what the framework needs to see in a source). DF = {{REPO}}/decomposition-frameworks.

Corpus: {{REPO}}/tbpn-transcripts/extractions/*.json, one per episode, keys episode_date, episode_title, companies [{name, type, context, sentiment, sector}], people, topics, key_claims [], technologies. Search these first (grep -il, jq) to shortlist 5 to 10 episodes by keyword and by the kind of situation the framework needs. Then open the transcript files {{REPO}}/tbpn-transcripts/transcripts/<date>_<title>.md (some dates have two files) and read the relevant passages to confirm the structure is really there and to harvest quotes. Transcripts are diarised speech, often one short line per utterance, with transcription errors; that is fine.

What "best" means, in priority order: (1) the framework's structure is genuinely present in what the speakers say (an argument with a contestable warrant for Toulmin, a stated conflict for the Evaporating Cloud, a completed event with an outcome for STAR, a visible bottleneck for TOC, and so on); (2) enough verbatim material to fill most slots with facts (aim for 6 to 10 quotable spans); (3) a business angle: a derived slot can yield an idea, an underserved need or a market shift, because the end goal of this library is idea generation from these transcripts; (4) prefer a moment that is specific and concrete over a general discussion.

Deliver, as your final message and nothing else: three candidates, ranked, each with:
- transcript file path (exact, relative to the repo root), date, episode title
- a two-sentence case for why it fits this framework's structure
- 6 to 10 verbatim quotes copied exactly from the file, each with the speaker if identifiable (or the neighbouring line) and the slot it would fill
- entities involved (companies, people, products, as named in the extractions)
- the idea angle: what a derived slot could surface here
Quotes must be copy-exact. The validator checks them against the file after normalising case, punctuation and whitespace; do not tidy grammar, fix transcription errors, or merge lines that are not adjacent.
```

---

## Part C: README writer

```
You write README.md for the framework {{NAME}} ({{SLUG}}) at DF/{{CATEGORY}}/{{SLUG}}/README.md. DF = {{REPO}}/decomposition-frameworks.

Read first, fully: DF/SPEC.md (sections 3, 6 and 12 matter most), the {{SLUG}} entry in DF/_meta/frameworks.json, and DF/{{CATEGORY}}/{{SLUG}}/graph.json, which is the single source of truth for both examples. If another framework folder under DF has state.json status "done", read its README.md once for house style.

Rules:
- Follow the section template in SPEC section 6 exactly; headings are fixed, prose is yours.
- Every example entry must match graph.json exactly: node texts, [fact] / [derived 0.xx] tags, confidences, quotes. Do not edit graph.json. If you find a defect in it, write the README against the data as it is and list the defect under "graph.json issues" in your final message.
- Links are relative: transcript ../../../tbpn-transcripts/transcripts/<file>; a sibling in the same category ../<slug>/README.md; a framework in another category ../../<category>/<slug>/README.md; the graph ./index.html; the library root ../../README.md.
- One mermaid diagram of the generic slot structure in "The slots".
- 1,500 to 3,000 words of prose; the per-node decomposition entries, quoted source text, the mermaid diagram and code blocks are mandated content and do not count toward the cap. Plain, precise GitHub markdown. No marketing tone, no filler.
- "Building a knowledge graph with this framework" is the heart of the page: per slot, when it is extracted and when it must be inferred and why the inference is worth making; the extraction recipe as a prompt skeleton whose output is graph.json-shaped; failure modes with a guard for each. "Where the opportunity shows up" reads the idea-bearing slot's derived nodes as candidate ideas or underserved needs with their confidence.

Final message: five lines at most: word count, sections present, links checked, graph.json issues if any.
```

---

## Part D: viz builder (first launch, then continuation messages)

First launch:

```
You are the viz builder for {{NAME}} ({{SLUG}}). Folder: DF/{{CATEGORY}}/{{SLUG}}; DF = {{REPO}}/decomposition-frameworks.

Read first: DF/SPEC.md sections 4 (layout fields), 5 (the viewer), 8.4 (the loop and the rubric an independent critic will score you on); the {{SLUG}} entry in DF/_meta/frameworks.json (layout_hint); graph.json in your folder.

Your job: make each example render in the framework's native shape, legibly, with the fact/derived contrast doing visible work, so that a reader who hides the LLM-derived nodes sees a coherent source-true skeleton and a reader who shows them sees where the reasoning was added.

You may edit only: in graph.json, each example's `layout` object, the node fields level / order / pos / size, and slot color / shape; in index.html, the block between <!--__EXT_START__--> and <!--__EXT_END__--> (optional; for a visual the data-driven engine cannot express; define window.__frameworkExtension = (ctx) => {...} and add objects to ctx.group so they are removed on example switch). Never change node content, provenance, edges, ids, or anything in DF/_meta.

Work loop: edit -> `node DF/_meta/validate.mjs <folder>` (must print 0 errors) -> `node DF/_meta/build.mjs <folder>` -> `node DF/_meta/snap.mjs <folder>` -> open every PNG in DF/_meta/.snaps/{{SLUG}}/ with the Read tool and read report.json (label overlaps, off-screen labels, labels under cards, console errors) -> fix -> repeat until you would pass the rubric yourself. Guidance: keep coordinates within about -60..60 world units; plane mode wants pos on every node; tree wants layout.root or a level on every node; ring wants order on the cycle nodes; long labels can be shortened only within the 40-character rule and only in the label field, never in text.

Report: the layout mode per example and why it fits the framework, what you changed, the final metrics per example from report.json, and anything the engine could not express.
```

Continuation message after a `revise` verdict (send to the same builder agent):

```
Critic verdict for iteration <n>: revise. Scores: demonstrates <d>, provenance <p>, legibility <l>, fidelity <f>.
Blocking issues:
<list>
Suggestions:
<list>
Address every blocking issue (say explicitly if you disagree with one and why), re-run validate, build and snap, look at the new PNGs, and report what changed.
```

---

## Part E: viz critic (fresh agent every iteration)

```
You are an independent critic of one visualisation page. You never edit files and you have not seen how the page was made.

Judge DF/{{CATEGORY}}/{{SLUG}}/index.html for the framework {{NAME}} ({{SLUG}}); DF = {{REPO}}/decomposition-frameworks. Read: DF/SPEC.md section 8.4 (the rubric and the pass rule) and section 5 (what the viewer is meant to do); DF/{{CATEGORY}}/{{SLUG}}/graph.json (the data, the two examples, idea_bearing_slot); the {{SLUG}} entry in DF/_meta/frameworks.json (blurb, layout_hint).

Procedure: run `node DF/_meta/snap.mjs DF/{{CATEGORY}}/{{SLUG}}` for fresh screenshots, then open every PNG in DF/_meta/.snaps/{{SLUG}}/ with the Read tool (default, facts-only, grounding and panel views for each example) and read report.json. Score the four criteria 1 to 5. Blocking issues must be concrete and actionable (node ids, where to move them, which labels collide, which decor is missing or wrong), not taste. Pass rule: every score at 4 or above, no blocking issues, console clean, and at the default view at most one overlapping label pair per example, zero off-screen labels, zero labels under cards.

Return only the JSON verdict object defined in SPEC 8.4 as your final message: { "verdict": "pass" | "revise", "scores": { "demonstrates": n, "provenance": n, "legibility": n, "fidelity": n }, "blocking_issues": [...], "suggestions": [...], "summary": "..." }.
```

---

## Part F: wave review (orchestrator)

```
Review these framework folders under DF = {{REPO}}/decomposition-frameworks against DF/SPEC.md: <list of category/slug>. Do not edit files.
For each folder read README.md, graph.json, state.json; run `node DF/_meta/validate.mjs <folder>`. Check: README matches graph.json (texts, provenance, confidences, quotes); the section template of SPEC 6 is followed; links resolve; the mermaid diagram exists; the knowledge-graph section has real rules of thumb, a usable extraction recipe and failure modes with guards; the TBPN example actually exhibits the framework's structure (not just its vocabulary); the idea-bearing slot reading is plausible; the classic example is a recognisable textbook case; the viz loop ended in pass (state.json.viz_reviews) and the final page metrics are within the pass rule.
Report per folder: pass, or issues with severity (blocking / should-fix / nit), location, and the fix. Then cross-folder notes: inconsistencies in style, slot usage, or provenance judgments that a reader comparing frameworks would notice.
```
