# depgraph

Local-only viewer/editor for plans as 3D dependency graphs. Source of truth is `plans/<slug>.json`.

    npm install
    npm run dev        # http://localhost:3000
    npm test           # unit tests
    npm run test:e2e   # playwright smoke (needs: npx playwright install chromium)

Set `PLANS_DIR=/some/dir` to point at another folder of plan files.

File format: `{ "name": string, "nodes": [{ "id", "title", "description", "status": todo|doing|done|blocked, "tags": [], "depends_on": [ids] }] }`.
Arrows point from a dependency to the node that depends on it. Edit the JSON by hand and the browser refreshes; edit in the browser and the file rewrites (sorted, 2-space indent).

Controls: click node = select/edit · Link mode: click dependency then dependent · right-click an arrow = remove it · Add node / New plan in the toolbar.
