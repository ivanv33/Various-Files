# depgraph

Local-only viewer/editor for plans as 3D dependency graphs. Source of truth is `plans/<slug>.json`.

    npm install
    npm run dev        # http://127.0.0.1:3000
    npm test           # unit tests
    npm run test:e2e   # playwright smoke (needs: npx playwright install chromium)

Set `PLANS_DIR=/some/dir` to point at another folder of plan files.

File format: `{ "name": string, "nodes": [{ "id", "title", "description", "status": todo|doing|done|blocked, "tags": [], "depends_on": [ids] }] }`.
Arrows point from a dependency to the node that depends on it. Edit the JSON by hand and the browser refreshes; edit in the browser and the file rewrites (sorted, 2-space indent).

Controls (click-first):

- Click a node or its label to select it; click empty space to deselect. Every node's title is always shown; hover or select to see its id.
- The plan is drawn as a top-down tree on a single plane, viewed straight on in 3D: dependencies sit above the tasks that need them, and each row is one dependency depth. Once the layout settles the camera frames the whole tree (roots at the top if it is too tall to fit). Drag with any mouse button to pan and use the wheel to zoom; there is no orbiting, so nothing ever leaves the surface.
- The card at the bottom edits the selection: click the title to rename (Enter saves, Esc reverts), click a status pip, click the description to expand it, `×` on a tag removes it and `+` adds one, "needs:" chips jump to that node (`×` removes the dependency), "unlocks:" chips show what waits on it.
- `+` / **L** arms linking: every node you click next becomes a dependency of the selection, until **Esc**.
- `+next` / **Shift+N** adds a step that depends on the selection. `del` / **Del** (or **Backspace**) asks once, then deletes (disarms after 3 s).
- Hotkeys: **N** add node · **1–4** todo/doing/done/blocked · **F** fly to the selection · **Esc** backs out one step (edit, then linking, then selection). Hotkeys are ignored while typing.
- Right-click an arrow to remove that dependency.

## Caveats

- Saves are last-writer-wins: an external edit to a plan file that lands during the 300 ms save debounce is overwritten by the pending local edit.
- Local only: the API has no origin check, so run it on 127.0.0.1 and do not expose it.
