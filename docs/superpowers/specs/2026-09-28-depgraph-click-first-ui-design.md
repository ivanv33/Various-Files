# depgraph: click-first UI redesign

Date: 2026-09-28. Status: owner chose model B. Replaces the client UI parts of the visualizer design spec.

## 1. Interpretation

The graph is the UI. Every node's title is readable without clicking. Selecting, setting status, linking, unlinking, adding and deleting each take one or two clicks, and each has a hotkey. Text is edited inline, one field at a time. Nothing scrolls. It should feel like an RTS unit card, not a form.

## 2. Interaction models

**A. Radial ring.** Clicking a node opens icons around its screen position. Game-like, but the ring follows a moving 3D point, gets clipped at screen edges, has no room for deps, and is a moving target in tests.

**B. Bottom HUD card.** Clicking a node opens a slim card at bottom center:
```
Size runway ✎   ○todo ●doing ○done ○blocked
#finance +   needs: [schema×] [api×] [+L]
▸ description…            [+next] [del]
```
Fixed and testable, with everything visible at once, and deps are added by clicking nodes. The downside is that your eye moves between the node and the card.

**C. Direct manipulation.** Pips sit on the 3D label and modifier-clicks do the rest, with no chrome at all. It feels the purest, but nothing is discoverable and description and tags have nowhere to live.

**Decision: B.** Every control is a fixed DOM element with a stable test id, and hotkeys supply the game feel. A is fragile and C is undiscoverable. DOM labels (below) mean tests never click WebGL pixels.

## 3. Design

**Components**
- Remove `NodePanel.tsx`.
- Add `NodeHud.tsx`, `StatusPips.tsx`, `InlineText.tsx` (a click-to-edit span) and `hooks/useHotkeys.ts` (hotkeys are ignored while an input has focus).
- `Toolbar.tsx` becomes a slim top-left bar: plan select, count, + Node, New plan. The Link-mode toggle is removed.
- `Graph.tsx` gets always-on labels, a selection torus, an armed crosshair and a done-burst. Right-click on an arrow still unlinks.
- `lib/linkMode.ts` and its test are replaced by `lib/selection.ts`, a pure reducer over `{selectedId, arming}` with Vitest tests.

**Click grammar**
- Click a node or its label to select it. Click the background to deselect.
- **L** (or `+L`) arms linking. Each node you click next becomes a dependency of the selection, until Esc.
- **1–4** or a pip click sets the status.
- **N** adds a node, selects it and opens its title for editing. **Shift+N** ("+next") adds a node that depends on the selection.
- **Del** arms the "Confirm delete" button, which disarms after 3 s. A second Del or a click deletes.
- **F** flies the camera to the selection. **Esc** backs out one step: cancel the edit, then disarm, then deselect.

**Always-visible labels**
- Each node has a `CSS2DObject` label, added with `extraRenderers={[new CSS2DRenderer()]}` and `nodeThreeObjectExtend={true}`, 8 px below the sphere.
- Labels are 12 px, tinted with the status color, and cut to 24 characters with an ellipsis. The full title is in `title=`.
- When a node is selected, labels outside its neighborhood fade to 25%. The id shows in smaller text only on hover or selection.
- The overlay uses `pointer-events: none` and each label uses `auto`, so orbiting still works.
- Trade-off against sprites: CSS2D gives crisp DOM text that screen readers and Playwright can query and click. It costs one DOM element per node (fine below a few hundred) and labels are not hidden behind nearer spheres. Texture sprites would be occluded by depth, but they blur and are invisible to tests.

**Dependencies.** "needs:" chips. Clicking a chip selects that node and flies the camera there. × removes the dependency. Read-only "unlocks:" chips show the reverse direction.

**Text.**
- The title is `InlineText`: Enter saves, Esc reverts.
- The description is a one-line preview that expands in place into a 6-row textarea and saves on blur.
- Tags are chips with ×. A `+` chip turns into a small input.

**Feedback.**
- An empty plan shows "Press N or click + Node to place your first step."
- Errors from `apply` (for example a cycle) show a red toast and the target node shakes. Info toasts are amber.
- `SaveIndicator` is unchanged.

**Visual language.**
- Keep the existing dark glass and status colors, and the pulse on blocked nodes.
- The card is 560 px wide and slides up in 120 ms. Buttons show keycap hints.
- Setting a node to done fires a single ring burst on it, skipped under `prefers-reduced-motion`.

## 4. Testability contract

| Control | `data-testid` | Accessible name |
|---|---|---|
| Plan select | `plan-select` | combobox "Plan" |
| Count | `node-count` | — |
| Add node | `add-node` | button "Add node" |
| New plan | `new-plan` | button "New plan" |
| Node label | `node-label` + `data-node-id` | button "<full title>" |
| Card | `node-hud` | region "Selected node" |
| Title | `hud-title` | button "Rename" → textbox "Title" |
| Status | `status-pip-<s>` | radiogroup "Status", radios by status |
| Description | `hud-description` | button "Edit description" → textbox "Description" |
| Tag | `tag-<t>` | button "Remove tag <t>" |
| Add tag | `add-tag` | button "Add tag" → textbox "New tag" |
| Dep chip | `dep-<id>` | button "<title>"; button "Remove dependency <title>" |
| Arm link | `link-button` | button "Add dependency", `aria-pressed` |
| Link hint | `link-hint` | status "Pick what <title> needs" |
| Add next | `add-next` | button "Add next step" |
| Delete | `delete-node` | button "Delete node" → "Confirm delete" |
| Close | `hud-close` | button "Close" |

`toast` and `save-indicator` are unchanged.

**E2E (`e2e/smoke.spec.ts`)**
- Test 1: unchanged.
- Test 2: Title, then "doing", then Add dependency, then click the schema label. Assert the file, then Delete and Confirm.
- Test 3 becomes "Add dependency arms, Esc disarms".
- Test 4: its checkbox step becomes a label click.
- New tests: all 8 labels are visible on load, and hotkeys 1–4 and N work.

## 5. Out of scope

Node finder/search, undo, drag-to-link, multi-select, minimap, sound, touch, persisted positions.
