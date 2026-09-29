# depgraph

Local-only viewer/editor for plans as 3D dependency graphs. Source of truth is `plans/<slug>.json`.

    npm install
    npm run dev        # http://localhost:3000
    npm test           # unit tests
    npm run test:e2e   # playwright smoke (needs: npx playwright install chromium)

Set `PLANS_DIR=/some/dir` to point at another folder of plan files.

File format: `{ "name": string, "nodes": [{ "id", "title", "description", "status": todo|doing|done|blocked, "tags": [], "depends_on": [ids] }] }`.
Arrows point from a dependency to the node that depends on it. Edit the JSON by hand and the browser refreshes; edit in the browser and the file rewrites (sorted, 2-space indent).

Controls (click-first):

- Click a node or its label to select it; click empty space to deselect. Every node's title is always shown; hover or select to see its id.
- The card at the bottom edits the selection: click the title to rename (Enter saves, Esc reverts), click a status pip, click the description to expand it, `×` on a tag removes it and `+` adds one, "needs:" chips jump to that node (`×` removes the dependency), "unlocks:" chips show what waits on it.
- `+` / **L** arms linking: every node you click next becomes a dependency of the selection, until **Esc**.
- `+next` / **Shift+N** adds a step that depends on the selection. `del` / **Del** asks once, then deletes (disarms after 3 s).
- Hotkeys: **N** add node · **1–4** todo/doing/done/blocked · **F** fly to the selection · **Esc** backs out one step (edit, then linking, then selection). Hotkeys are ignored while typing.
- Right-click an arrow to remove that dependency.
