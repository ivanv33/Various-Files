# Decomposition Frameworks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the 22 framework folders (README.md, graph.json, index.html, state.json) plus the root README tables and index.html, through the agent protocol in SPEC.md, with every step committed and resumable.

**Architecture:** The orchestrator (main session) launches one framework agent per slug using `_meta/AGENT_BRIEF.md` Part A; each framework agent runs a scout, a README writer, and a viz builder judged by an independent critic in a loop; each framework commits its own folder through `_meta/commit-framework.sh`. Waves: pilot (2), rest of category 1 (4), everything else (16). A wave review agent (Part F) checks each wave before the next.

**Tech Stack:** Node 26 scripts in `_meta/` (validate, build, snap with puppeteer-core + Brave, status, build-index), Three.js r0.186 from jsDelivr, git on branch `claude/decomposition-frameworks-66ea98`, no PR.

## Global Constraints

- Contract: `decomposition-frameworks/SPEC.md`; prompts: `decomposition-frameworks/_meta/AGENT_BRIEF.md`. Agents may not edit `_meta/`, `SPEC.md`, or other folders.
- Only `_meta/commit-framework.sh` commits framework folders; the orchestrator commits `_meta/`, `SPEC.md`, root `README.md`, `index.html`.
- Every fact quote must verify against the cited transcript (`node _meta/validate.mjs` prints 0 errors).
- Viz loop cap: 5 iterations; pass rule in SPEC 8.4.
- Model for all agents: same as the session (no override).
- Absolute repo root: `/Users/poplar/repos/Various-Files/.claude/worktrees/decomposition-frameworks-66ea98`; `DF` = that path + `/decomposition-frameworks`.

---

### Task 1: Pilot wave (toulmin-model, star-par)

**Files:**
- Create (by agents): `DF/01-narrative-and-statement/toulmin-model/{README.md,graph.json,index.html,state.json}`, same for `star-par`
- Modify (orchestrator, after review): `DF/index.html`, `DF/README.md` (generated tables), `DF/_meta/state.json`

**Interfaces:**
- Consumes: Part A launcher prompt with `{{SLUG}}`, `{{NAME}}`, `{{CATEGORY}}`, `{{REPO}}` substituted.
- Produces: two `done` folders; the first house-style references later agents read.

- [x] **Step 1: Launch both framework agents in the background** (done 2026-09-09, Agent tool, general-purpose, run_in_background true; launcher prompt = identity + placeholder values + "execute Part A exactly").

- [ ] **Step 2: Wait for both completion notifications.** Do not read their transcripts. Meanwhile only touch `_meta/PLAN.md` and memory.

- [ ] **Step 3: Verify mechanically**

```bash
cd /Users/poplar/repos/Various-Files/.claude/worktrees/decomposition-frameworks-66ea98/decomposition-frameworks
node _meta/status.mjs
node _meta/validate.mjs --all
node _meta/snap.mjs 01-narrative-and-statement/toulmin-model && node _meta/snap.mjs 01-narrative-and-statement/star-par
git log --oneline -20
```
Expected: both slugs `done`, `PASS` for both with 0 errors, snap metrics within the pass rule, commit subjects following SPEC 10 (scaffold, readme, viz n, viz-review n, Add framework).

- [ ] **Step 4: Look at the pages.** Read `_meta/.snaps/<slug>/*-default.png` and `*-facts-only.png` for both; open one in the browser pane. Check the README of each (headings per SPEC 6, mermaid, links).

- [ ] **Step 5: Wave review agent.** Launch Part F with the two folders (run_in_background false). For blocking issues, message the framework agent that owns the folder (its context is intact) with the issue list and wait; re-run validate. Repeat until the reviewer reports pass or only nits remain.

- [ ] **Step 6: Decide on brief changes.** If both pilots hit the same flaw, patch `SPEC.md` / `AGENT_BRIEF.md` before Task 2 and commit the patch:

```bash
git add decomposition-frameworks/SPEC.md decomposition-frameworks/_meta/AGENT_BRIEF.md && git commit -m "frameworks: brief adjustments after pilot wave

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 7: Regenerate index and README tables, commit**

```bash
node _meta/build-index.mjs && node _meta/status.mjs >/dev/null
cd .. && git add decomposition-frameworks/index.html decomposition-frameworks/README.md decomposition-frameworks/_meta/state.json && git commit -m "frameworks: index and status after pilot wave

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 2: Rest of category 1 (carl, minto-scqa, pyramid-principle, dialectical-decomposition)

**Files:** as Task 1 for the four slugs.

**Interfaces:** Consumes the (possibly patched) brief; the pilots' folders as house style.

- [ ] **Step 1: Launch the four framework agents** in one response, background, same launcher prompt shape with these values: carl / CARL; minto-scqa / Minto SCQA; pyramid-principle / Pyramid Principle; dialectical-decomposition / Dialectical Decomposition; category 01-narrative-and-statement.
- [ ] **Step 2: Wait for all four notifications.**
- [ ] **Step 3: Verify mechanically** (same commands as Task 1 step 3 with the four folders; `validate --all` covers everything).
- [ ] **Step 4: Wave review agent** with the four folders; route fixes to the owning agents; repeat until pass.
- [ ] **Step 5: Regenerate index and tables, commit** (Task 1 step 7 with subject "frameworks: index and status after wave 1").

### Task 3: Everything else (16 frameworks, launched together)

**Files:** as Task 1 for: mece, issue-hypothesis-trees, five-whys, ishikawa-fishbone, rumelt-strategy-kernel, theory-of-constraints (02-strategic-and-business); first-principles, functional-decomposition, polya-four-step, means-ends-analysis, inversion-premortem (03-engineering-and-cognitive); cynefin, wardley-mapping, ooda-loop, pdca-deming, systems-thinking (04-sensemaking-and-complex-systems).

- [ ] **Step 1: Launch all 16** in one response, background. If the machine shows headless-browser failures in Task 2 (snap timeouts, `requestfailed` in report.json), launch in two batches of 8 instead and say so in the final report.
- [ ] **Step 2: Wait for all notifications.** As each arrives, run `node _meta/validate.mjs <folder>` and note failures; do not launch fixes until the wave is complete unless an agent reports `failed`.
- [ ] **Step 3: Relaunch any `failed` or non-`done` slug** with the Part A launcher (the agent resumes from state.json).
- [ ] **Step 4: Wave review** in three agents, one per category (Part F), in parallel; route fixes; repeat until pass.
- [ ] **Step 5: Regenerate index and tables, commit** ("frameworks: index and status after wave 2").

### Task 4: Finish

- [ ] **Step 1: Full verification**

```bash
node _meta/validate.mjs --all          # expect 22 PASS
node _meta/build.mjs --all             # re-embed with the final engine (extension blocks kept)
for d in 0*/*/; do node _meta/snap.mjs "$d" | head -3; done   # expect console clean everywhere
node _meta/status.mjs                  # expect 22/22 done
node _meta/build-index.mjs
```

- [ ] **Step 2: Browser spot check.** Open `DF/index.html` and four framework pages (one per category) in the browser pane; check links from index to graph and README.
- [ ] **Step 3: Root README final pass.** Rewrite the prose parts of `DF/README.md` where the build changed things (the tables are generated); keep the resume instructions accurate.
- [ ] **Step 4: Final commit**

```bash
cd /Users/poplar/repos/Various-Files/.claude/worktrees/decomposition-frameworks-66ea98
git add decomposition-frameworks/index.html decomposition-frameworks/README.md decomposition-frameworks/_meta/state.json decomposition-frameworks/0*/*/index.html
git commit -m "frameworks: final index, README tables, rebuilt pages

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git status --short   # expect empty
```

- [ ] **Step 5: Report to the owner**: what was built, per-wave review outcomes, frameworks whose critic never passed (if any), total commits, and how to resume or extend.
