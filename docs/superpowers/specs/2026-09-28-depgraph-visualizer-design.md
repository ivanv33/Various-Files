# Dependency Graph Plan Visualizer — Design

Date: 2026-09-28
Status: approved by owner (this conversation)

## Purpose

A local-only web app for viewing and editing a plan or project as a 3D
dependency graph. The graph is the editing surface; the source of truth is a
JSON file on disk. Editing in the browser rewrites the file; editing the file
(by hand, by Claude, by a script) refreshes the browser.

## Non-goals

- No deployment (not Vercel, not hosted). Runs via `npm run dev` only.
- No auth, no multi-user, no realtime collaboration.
- No Jira-like fields (owner, estimates, dates). Task-lite only.
- Node positions are not persisted; layout is recomputed on each load.

## Location and stack

- Folder: `depgraph/` at the repo root.
- Next.js (App Router, TypeScript), React, `react-force-graph-3d`
  (three.js under the hood), Tailwind for the overlay UI.
- Plans live in `depgraph/plans/<name>.json`, git-tracked.
- Tests: Vitest for pure logic and file layer; one Playwright smoke test.

## Data schema

File `depgraph/plans/<slug>.json`:

```json
{
  "name": "AI wave strategy",
  "nodes": [
    {
      "id": "runway",
      "title": "Size 6-12mo runway",
      "description": "Markdown text. Optional, default \"\".",
      "status": "done",
      "tags": ["finance"],
      "depends_on": []
    }
  ]
}
```

Rules:
- `id`: `^[a-z0-9][a-z0-9-]*$`, unique within a file. Generated from the
  title on create (slugified, de-duplicated with `-2`, `-3`). Never renamed
  by the UI.
- `status`: one of `todo | doing | done | blocked`. Default `todo`.
- `tags`: string array, default `[]`.
- `depends_on`: array of node ids in the same file. Edges are derived from
  this field; there is no separate edge list. Edge direction in the graph:
  dependency -> dependent (arrow points at the node that waits).
- Validator rejects: duplicate ids, unknown ids in `depends_on`,
  self-dependency, any cycle, bad status, bad id format.
- On save the whole file is rewritten: nodes sorted by id, `depends_on`
  sorted, 2-space indent, trailing newline. Deterministic output keeps git
  diffs minimal.

## Server (Next.js route handlers)

- `GET /api/plans` -> `[{ slug, name, nodeCount }]` from `plans/*.json`.
- `GET /api/plans/[slug]` -> the plan JSON. 404 if missing.
- `PUT /api/plans/[slug]` body: full plan. Validates; on failure returns 400
  with `{ errors: string[] }` and writes nothing. On success writes
  atomically (write `<slug>.json.tmp`, then rename) and returns the
  normalized plan.
- `POST /api/plans` body `{ name }` -> creates an empty plan at
  `<slugified-name>.json`, 409 if exists.
- `GET /api/plans/[slug]/events` -> Server-Sent Events stream. A
  `chokidar` watcher on `plans/` emits `changed` when the file is modified on
  disk by anything other than the app's own last write (compared by content
  hash). The client refetches on `changed`.
- Slug parameter is validated against the id regex before touching the
  filesystem (no path traversal).

## Client

Single page, `/` with `?plan=<slug>` in the URL (defaults to the first plan).

- **Scene**: full-viewport `ForceGraph3D`. Node sphere size constant;
  color by status: todo neutral, doing accent, done dimmed, blocked warning
  with a slow pulse. Directional arrows on links. Hover shows title label.
  Click selects; selected node and its direct neighbors are highlighted,
  everything else fades.
- **Side panel** (glass overlay, right side) for the selected node: title,
  description (textarea, markdown stored raw), status segmented control,
  tags (chip input), dependencies (searchable multi-select of other nodes).
  Every field change debounces 300 ms then saves the whole plan via PUT.
  Delete node button (removes the node and strips its id from every
  `depends_on`).
- **Toolbar** (top-left): plan switcher, "New plan", "Add node" (creates
  `untitled-N`, selects it, focuses the title field), "Link mode" toggle.
- **Link mode**: click node A then node B => A is added to B's
  `depends_on`. If the validator refuses (cycle), show the error toast and
  do nothing. Right-click a link => remove that dependency.
- **Save state indicator** (bottom-right): saving / saved / error text.
  Errors from the server are shown verbatim.
- **External change**: on SSE `changed`, refetch and replace the plan while
  keeping the current selection if the id still exists.

## Module boundaries

- `lib/schema.ts`: types, `validatePlan(plan) -> string[]`, `normalizePlan`.
  Pure, no IO. Cycle detection via DFS.
- `lib/store.ts`: `listPlans`, `readPlan`, `writePlan`, `createPlan`, plus
  the watcher. Only module that touches `fs`.
- `app/api/**`: thin handlers over `lib/store.ts`.
- `components/Graph.tsx`: rendering only; receives plan + selection +
  callbacks.
- `components/NodePanel.tsx`, `components/Toolbar.tsx`,
  `components/SaveIndicator.tsx`.
- `hooks/usePlan.ts`: fetch, optimistic local state, debounced save, SSE
  subscription. Single owner of plan state on the client.

## Visual direction

Dark, near-black background with subtle depth fog. Status colors as emissive
glow rather than flat fills. UI overlays are translucent panels with thin
borders, monospace for ids and a humanist sans for titles. No default
component-library look. Applied via the frontend-design skill during the
UI tasks.

## Testing

- Vitest: `validatePlan` (each rule, including a 3-node cycle),
  `normalizePlan` determinism, slug generation, `store` round-trip in a temp
  dir, atomic write leaves no `.tmp` on success.
- Playwright smoke: start dev server against a fixture plans dir, open the
  page, add a node, reload, node persists.

## Sample data

`plans/example.json` ships with ~8 nodes across all four statuses so the
first run is not empty.
