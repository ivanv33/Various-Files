# depgraph Click-First UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the side-panel/link-mode UI of `depgraph` with the click-first model B from the spec: always-visible DOM labels on every node, a bottom HUD card for the selected node, and hotkeys for every action.

**Architecture:** Pure logic stays in `src/lib/` and is unit-tested in Vitest: label text and DOM helpers (`nodeLabel.ts`), the selection/link-arming reducer (`selection.ts`, replaces `linkMode.ts`), camera math (`camera.ts`), and motion helpers (`effects.ts`). Hooks (`useHotkeys`, `useConfirm`) and the HUD components (`NodeHud`, `StatusPips`, `InlineText`, `Keycap`) are tested in jsdom with `@testing-library/react`. `Graph.tsx` stays WebGL-only glue: it mounts a `CSS2DRenderer` through `extraRenderers` and attaches one label element per node, so Playwright can find and click nodes as ordinary DOM buttons. `page.tsx` owns selection state and wires hotkeys, HUD and graph; it is covered by `e2e/smoke.spec.ts`.

**Tech Stack:** Next.js 16.3 App Router, React 19.2 (`useEffectEvent`), TypeScript, Tailwind v4, react-force-graph-3d ^1.29 + three ^0.186 (`three/examples/jsm/renderers/CSS2DRenderer.js`), Vitest 5 + jsdom + @testing-library/react 16, Playwright 1.63.

Spec: `docs/superpowers/specs/2026-09-28-depgraph-click-first-ui-design.md` (binding testability contract in §4). Previous plan: `docs/superpowers/plans/2026-09-28-depgraph-visualizer.md` (Slices 1–5 are done; this plan continues the numbering at Slice 6).

## Global Constraints

Testability contract, copied verbatim from spec §4:

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

Project rules:

- All commands run from `depgraph/` (the worktree path is `/Users/poplar/repos/Various-Files/.claude/worktrees/career-ai-wave-strategy-539d1d/depgraph`). File paths below are repo-relative.
- Never run `npm run dev` or use port 3000. E2E runs through `npm run test:e2e`, which starts its own server on port 3123 with `PLANS_DIR=e2e/plans` and `workers: 1`. `beforeEach` copies `plans/example.json` to `e2e/plans/example.json`.
- Repo style: single quotes, no semicolons, 2-space indent.
- Tests that need the DOM start with `// @vitest-environment jsdom` and call `cleanup()` in `afterEach`, because Vitest globals are off and RTL does not auto-clean.
- jsdom facts this plan relies on (verified): `autoFocus` focuses on mount; removing a focused input does **not** fire `blur`; `isContentEditable` is `undefined`; `window.matchMedia` is `undefined`; `style.color` normalizes hex to `rgb(...)`, so status is exposed as `data-status` and tested that way.
- `src/hooks/usePlan.ts` is not modified. `apply(mutate)` returns `string[]` errors and is synchronous.
- Playwright `getByLabel`/`getByRole` name matching is substring and case-insensitive by default. Node labels are buttons named by full title (e.g. "Untitled"), so tests use `exact: true` whenever a name could be a substring of a node title or another control's name.
- The full check is `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`. Every slice ends with it and a commit.
- Every commit message starts with `depgraph:` and ends with the trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (pass it as a second `-m`).
- Strict TDD: every behavior starts with a failing test, then a run that shows the expected failure, then minimal code, then a passing run, then a commit. The only exceptions are WebGL-only code in `Graph.tsx`, marked "no unit test possible (WebGL); covered by e2e test X", and pure styling.

---

## File structure

```
depgraph/
  src/lib/nodeLabel.ts            NEW  truncateTitle, createLabelElement, renderLabel, labelFor, syncLabels, shakeLabel
  src/lib/nodeLabel.test.ts       NEW
  src/lib/selection.ts            NEW  selectionStep reducer {selectedId, arming}; NodeSignal/nextSignal
  src/lib/selection.test.ts       NEW
  src/lib/camera.ts               NEW  cameraFor(node) -> {position, lookAt}
  src/lib/camera.test.ts          NEW
  src/lib/effects.ts              NEW  takeNewlyDone, burstFrame, prefersReducedMotion
  src/lib/effects.test.ts         NEW
  src/lib/mutations.ts            MOD  + addNextNode
  src/lib/mutations.test.ts       MOD
  src/lib/linkMode.ts(+test)      DEL  (replaced by selection.ts)
  src/lib/escapeHtml.ts(+test)    DEL  (its only caller, the WebGL hover tooltip, is replaced by DOM labels)
  src/hooks/useHotkeys.ts         NEW  hotkeyName, isTypingTarget, useHotkeys
  src/hooks/useHotkeys.test.tsx   NEW
  src/hooks/useConfirm.ts         NEW  two-step confirm with auto-disarm
  src/hooks/useConfirm.test.tsx   NEW
  src/components/Graph.tsx        MOD  CSS2D labels, torus, arming cursor, flyTo, shake, done burst
  src/components/NodeHud.tsx      NEW  bottom card
  src/components/NodeHud.test.tsx NEW
  src/components/StatusPips.tsx   NEW  radiogroup
  src/components/StatusPips.test.tsx NEW
  src/components/InlineText.tsx   NEW  click-to-edit span
  src/components/InlineText.test.tsx NEW
  src/components/Keycap.tsx       NEW  aria-hidden <kbd> hint
  src/components/Toolbar.tsx      MOD  slim: plan select, count, + Node, New plan
  src/components/Toolbar.test.tsx NEW
  src/components/Toast.tsx        MOD  tone: info (amber) | error (red), top-center
  src/components/Toast.test.tsx   NEW
  src/components/NodePanel.tsx    DEL
  src/app/page.tsx                MOD  selection reducer, hotkeys, HUD, empty state, error shake
  src/app/globals.css             MOD  label, arming, HUD slide-in, shake styles
  e2e/smoke.spec.ts               MOD
  README.md                       MOD  controls section
```

---

# Slice 6 — Always-visible node labels

Outcome: every node shows a DOM label (CSS2D) under its sphere; labels are buttons named by the full title, cut to 24 characters, tinted by status, faded outside the selection's neighborhood, show the id on hover/selection, and select the node on click. The selected node gets a torus ring.

### Task 6.1: `truncateTitle`

**Files:**
- Create: `depgraph/src/lib/nodeLabel.ts`
- Test: `depgraph/src/lib/nodeLabel.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `export const LABEL_MAX = 24`; `export function truncateTitle(title: string, max?: number): string`.

- [ ] **Step 1: Write the failing test**

Create `depgraph/src/lib/nodeLabel.test.ts`:

```ts
// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import { LABEL_MAX, truncateTitle } from './nodeLabel'

describe('truncateTitle', () => {
  it('keeps titles of up to 24 characters', () => {
    expect(LABEL_MAX).toBe(24)
    expect(truncateTitle('Schema + validator')).toBe('Schema + validator')
    expect(truncateTitle('x'.repeat(24))).toBe('x'.repeat(24))
  })

  it('cuts longer titles to 24 characters ending in an ellipsis', () => {
    const out = truncateTitle('Write the migration for the billing tables')
    expect(out).toBe('Write the migration for…')
    expect(Array.from(out)).toHaveLength(24)
  })

  it('drops trailing whitespace before the ellipsis', () => {
    expect(truncateTitle('Write the migration fo xxxxxxxx')).toBe('Write the migration fo…')
  })

  it('counts an emoji as one character', () => {
    expect(truncateTitle('🚀'.repeat(30))).toBe('🚀'.repeat(23) + '…')
  })

  it('accepts a custom max', () => {
    expect(truncateTitle('abcdef', 4)).toBe('abc…')
  })
})
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: FAIL with `Error: Failed to resolve import "./nodeLabel" from "src/lib/nodeLabel.test.ts". Does the file exist?`

- [ ] **Step 3: Write the minimal implementation**

Create `depgraph/src/lib/nodeLabel.ts`:

```ts
export const LABEL_MAX = 24

export function truncateTitle(title: string, max = LABEL_MAX): string {
  const chars = Array.from(title)
  if (chars.length <= max) return title
  return chars.slice(0, max - 1).join('').trimEnd() + '…'
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: PASS, `Tests  5 passed (5)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/nodeLabel.ts src/lib/nodeLabel.test.ts
git commit -m "depgraph: truncateTitle for node labels" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 6.2: Label DOM helpers (`createLabelElement`, `renderLabel`, `labelFor`, `syncLabels`)

**Files:**
- Modify: `depgraph/src/lib/nodeLabel.ts`
- Test: `depgraph/src/lib/nodeLabel.test.ts`

**Interfaces:**
- Consumes: `truncateTitle` (Task 6.1); `Status` from `@/lib/schema`.
- Produces:
  - `export interface LabelView { title: string; status: Status; selected: boolean; dim: boolean }`
  - `export interface LabelNode extends LabelView { id: string }`
  - `export function createLabelElement(id: string, onPick: (id: string) => void): HTMLDivElement`
  - `export function renderLabel(el: HTMLElement, view: LabelView): void`
  - `export function labelFor(labels: Map<string, HTMLDivElement>, id: string, onPick: (id: string) => void): HTMLDivElement`
  - `export function syncLabels(labels: Map<string, HTMLDivElement>, nodes: LabelNode[], onPick: (id: string) => void): void`
  - Label DOM: `div.node-label[data-testid=node-label][data-node-id][role=button][tabindex=0][aria-label][title][data-status][data-selected][data-dim]` containing `span.node-label-title` and `span.node-label-id`.

- [ ] **Step 1: Write the failing tests**

Replace the import line at the top of `depgraph/src/lib/nodeLabel.test.ts` with:

```ts
import { describe, expect, it, vi } from 'vitest'
import { LABEL_MAX, createLabelElement, labelFor, renderLabel, syncLabels, truncateTitle } from './nodeLabel'
```

and append:

```ts
describe('createLabelElement', () => {
  it('is a focusable button tagged with the node id', () => {
    const el = createLabelElement('schema', () => {})
    expect(el.getAttribute('data-testid')).toBe('node-label')
    expect(el.getAttribute('data-node-id')).toBe('schema')
    expect(el.getAttribute('role')).toBe('button')
    expect(el.tabIndex).toBe(0)
    expect(el.querySelector('.node-label-id')?.textContent).toBe('schema')
  })

  it('click and Enter pick the node; pointerdown does not reach the graph container', () => {
    const onPick = vi.fn()
    const graphDown = vi.fn()
    const container = document.createElement('div')
    container.addEventListener('pointerdown', graphDown)
    const el = createLabelElement('schema', onPick)
    container.append(el)
    el.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    el.dispatchEvent(new Event('pointerdown', { bubbles: true }))
    expect(onPick.mock.calls).toEqual([['schema'], ['schema']])
    expect(graphDown).not.toHaveBeenCalled()
  })
})

describe('renderLabel', () => {
  it('shows the cut title, uses the full title as name and tooltip, and exposes status and flags', () => {
    const el = createLabelElement('mig', () => {})
    renderLabel(el, { title: 'Write the migration for the billing tables', status: 'doing', selected: true, dim: false })
    expect(el.getAttribute('aria-label')).toBe('Write the migration for the billing tables')
    expect(el.title).toBe('Write the migration for the billing tables')
    expect(el.querySelector('.node-label-title')?.textContent).toBe('Write the migration for…')
    expect(el.dataset.status).toBe('doing')
    expect(el.dataset.selected).toBe('true')
    expect(el.dataset.dim).toBe('false')
  })

  it('falls back to the id when the title is empty', () => {
    const el = createLabelElement('mig', () => {})
    renderLabel(el, { title: '', status: 'todo', selected: false, dim: true })
    expect(el.getAttribute('aria-label')).toBe('mig')
    expect(el.querySelector('.node-label-title')?.textContent).toBe('mig')
    expect(el.dataset.dim).toBe('true')
  })
})

describe('labelFor / syncLabels', () => {
  const view = { status: 'todo' as const, selected: false, dim: false }

  it('creates one element per id and reuses it', () => {
    const labels = new Map<string, HTMLDivElement>()
    const first = labelFor(labels, 'a', () => {})
    expect(labelFor(labels, 'a', () => {})).toBe(first)
    expect(labels.size).toBe(1)
  })

  it('renders current nodes and removes labels of deleted nodes from the map and the DOM', () => {
    const labels = new Map<string, HTMLDivElement>()
    const overlay = document.createElement('div')
    syncLabels(labels, [{ id: 'a', title: 'A', ...view }, { id: 'b', title: 'B', ...view }], () => {})
    overlay.append(labels.get('a')!, labels.get('b')!)
    syncLabels(labels, [{ id: 'a', title: 'A2', ...view }], () => {})
    expect([...labels.keys()]).toEqual(['a'])
    expect(overlay.children).toHaveLength(1)
    expect(labels.get('a')!.getAttribute('aria-label')).toBe('A2')
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: FAIL, 6 failed / 5 passed, each failure like `TypeError: (0 , __vi_import_0__.createLabelElement) is not a function` (or `labelFor` / `syncLabels`).

- [ ] **Step 3: Write the minimal implementation**

Replace `depgraph/src/lib/nodeLabel.ts` with:

```ts
import type { Status } from '@/lib/schema'

export const LABEL_MAX = 24

export interface LabelView {
  title: string
  status: Status
  selected: boolean
  dim: boolean
}

export interface LabelNode extends LabelView {
  id: string
}

export function truncateTitle(title: string, max = LABEL_MAX): string {
  const chars = Array.from(title)
  if (chars.length <= max) return title
  return chars.slice(0, max - 1).join('').trimEnd() + '…'
}

export function createLabelElement(id: string, onPick: (id: string) => void): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'node-label'
  el.setAttribute('data-testid', 'node-label')
  el.setAttribute('data-node-id', id)
  el.setAttribute('role', 'button')
  el.tabIndex = 0
  const title = document.createElement('span')
  title.className = 'node-label-title'
  const idLine = document.createElement('span')
  idLine.className = 'node-label-id'
  idLine.textContent = id
  el.append(title, idLine)
  // The graph container starts a click on pointerdown; stopping it here keeps a label click from also
  // registering as a background click (which would deselect).
  el.addEventListener('pointerdown', e => e.stopPropagation())
  el.addEventListener('click', e => {
    e.stopPropagation()
    onPick(id)
  })
  el.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onPick(id)
    }
  })
  return el
}

export function renderLabel(el: HTMLElement, view: LabelView): void {
  const name = view.title || el.getAttribute('data-node-id') || ''
  el.setAttribute('aria-label', name)
  el.title = name
  el.dataset.status = view.status
  el.dataset.selected = String(view.selected)
  el.dataset.dim = String(view.dim)
  const title = el.querySelector('.node-label-title')
  if (title) title.textContent = truncateTitle(name)
}

export function labelFor(labels: Map<string, HTMLDivElement>, id: string, onPick: (id: string) => void): HTMLDivElement {
  let el = labels.get(id)
  if (!el) {
    el = createLabelElement(id, onPick)
    labels.set(id, el)
  }
  return el
}

export function syncLabels(labels: Map<string, HTMLDivElement>, nodes: LabelNode[], onPick: (id: string) => void): void {
  const ids = new Set(nodes.map(n => n.id))
  for (const [id, el] of labels) {
    if (!ids.has(id)) {
      el.remove()
      labels.delete(id)
    }
  }
  for (const n of nodes) renderLabel(labelFor(labels, n.id, onPick), n)
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: PASS, `Tests  11 passed (11)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/nodeLabel.ts src/lib/nodeLabel.test.ts
git commit -m "depgraph: node label DOM helpers (create, render, sync)" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 6.3: Mount labels in the graph (e2e), torus, CSS; full check

**Files:**
- Modify: `depgraph/e2e/smoke.spec.ts` (full file below)
- Modify: `depgraph/src/components/Graph.tsx` (full file below)
- Modify: `depgraph/src/app/globals.css` (append)
- Delete: `depgraph/src/lib/escapeHtml.ts`, `depgraph/src/lib/escapeHtml.test.ts`

**Interfaces:**
- Consumes: `labelFor`, `syncLabels` (Task 6.2); `CSS2DObject`, `CSS2DRenderer` from `three/examples/jsm/renderers/CSS2DRenderer.js` (`new CSS2DObject(element: HTMLElement)`, `.center: Vector2`, `.position`); `ForceGraph3D` prop `extraRenderers` (init-only, so it must be a stable array) and `nodeThreeObjectExtend`.
- Produces: `Graph` props unchanged in this slice (`plan`, `selectedId`, `linkMode`, `onSelect`, `onLinkRightClick`). Label DOM contract from Task 6.2 is now live in the page.

- [ ] **Step 1: Write the failing e2e tests**

Replace `depgraph/e2e/smoke.spec.ts` with the file below. It adds the `label()` helper and two tests, and changes test 2's `getByLabel('Title')` to `exact: true`. After this slice the new node's label is a button named "Untitled", which also matches a substring search for "title".

```ts
import { expect, test, type Page } from '@playwright/test'
import { copyFile, mkdir, readFile } from 'node:fs/promises'

const label = (page: Page, id: string) => page.locator(`[data-testid="node-label"][data-node-id="${id}"]`)

test.beforeEach(async () => {
  await mkdir('e2e/plans', { recursive: true })
  await copyFile('plans/example.json', 'e2e/plans/example.json')
})

test('add a node: count increments, file gains the node, survives reload', async ({ page }) => {
  await page.goto('/?plan=example')
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"id": "untitled"')
  await page.reload()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
})

test('edit the new node in the panel, then delete it', async ({ page }) => {
  await page.goto('/?plan=example')
  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-panel')).toBeVisible()
  await page.getByLabel('Title', { exact: true }).fill('Smoke node')
  await page.getByLabel('Status').selectOption('doing')
  await page.getByRole('checkbox', { name: 'schema' }).check()
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"title": "Smoke node"')
  expect(text).toContain('"status": "doing"')
  expect(text).toMatch(/"depends_on": \[\s*"schema"\s*\]/)
  await page.getByRole('button', { name: 'Delete node' }).click()
  await expect(page.getByTestId('node-panel')).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})

test('link mode toggles and hints', async ({ page }) => {
  await page.goto('/?plan=example')
  const btn = page.getByRole('button', { name: 'Link mode' })
  await expect(btn).toHaveAttribute('aria-pressed', 'false')
  await btn.click()
  await expect(btn).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('toast')).toContainText('click the dependency')
  await page.keyboard.press('Escape')
  await expect(btn).toHaveAttribute('aria-pressed', 'false')
})

test('cycle is refused with an error', async ({ page }) => {
  await page.goto('/?plan=example')
  await page.getByRole('button', { name: 'Add node' }).click()
  await page.getByLabel('Title', { exact: true }).fill('Cycle probe')
  await page.getByRole('checkbox').first().check()
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const res = await page.request.put('/api/plans/example', {
    data: {
      name: 'x',
      nodes: [
        { id: 'a', title: 'A', depends_on: ['b'] },
        { id: 'b', title: 'B', depends_on: ['a'] },
      ],
    },
  })
  expect(res.status()).toBe(400)
  expect((await res.json()).errors[0]).toMatch(/^cycle:/)
})

test('all 8 labels are visible on load', async ({ page }) => {
  await page.goto('/?plan=example')
  const labels = page.getByTestId('node-label')
  await expect(labels).toHaveCount(8)
  for (const l of await labels.all()) await expect(l).toBeVisible()
  await expect(page.getByRole('button', { name: 'Schema + validator', exact: true })).toHaveAttribute('data-node-id', 'schema')
  await expect(label(page, 'node-panel')).toHaveAttribute('data-status', 'blocked')
})

test('clicking a label selects the node', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await expect(page.getByTestId('node-panel')).toBeVisible()
  await expect(page.getByRole('textbox', { name: 'Title', exact: true })).toHaveValue('Schema + validator')
  await expect(label(page, 'schema')).toHaveAttribute('data-selected', 'true')
  await expect(label(page, 'store')).toHaveAttribute('data-dim', 'false')
  await expect(label(page, 'watcher')).toHaveAttribute('data-dim', 'true')
})
```

- [ ] **Step 2: Run e2e and watch the new tests fail**

Run: `npm run test:e2e`
Expected: `2 failed`, `4 passed`. Failures:
- `all 8 labels are visible on load`: `expect(locator).toHaveCount(expected)` … `Expected: 8` `Received: 0`.
- `clicking a label selects the node`: `locator.click: Test timeout of 60000ms exceeded` waiting for `locator('[data-testid="node-label"][data-node-id="schema"]')`.

- [ ] **Step 3: Wire labels into `Graph.tsx`** (no unit test possible (WebGL); covered by e2e tests "all 8 labels are visible on load" and "clicking a label selects the node")

Replace `depgraph/src/components/Graph.tsx` with:

```tsx
'use client'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import ForceGraph3D, { type ForceGraphMethods } from 'react-force-graph-3d'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
import { labelFor, syncLabels } from '@/lib/nodeLabel'
import type { Plan, Status } from '@/lib/schema'
import { pulseBlocked, type Pulsable } from '@/lib/pulse'

export const STATUS_COLORS: Record<Status, string> = {
  todo: '#8b95a7',
  doing: '#5ac8fa',
  done: '#3a4152',
  blocked: '#ff6b6b',
}

interface GraphProps {
  plan: Plan
  selectedId: string | null
  linkMode: boolean
  onSelect: (id: string | null) => void
  onLinkRightClick: (dependencyId: string, dependentId: string) => void
}

const idOf = (end: unknown) => (typeof end === 'string' ? end : (end as GraphNode).id)

export default function Graph({ plan, selectedId, linkMode, onSelect, onLinkRightClick }: GraphProps) {
  const [cache] = useState(() => new Map<string, GraphNode>())
  const [labels] = useState(() => new Map<string, HTMLDivElement>())
  const [extraRenderers] = useState(() => [new CSS2DRenderer()])
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined)
  const [size, setSize] = useState({ w: 800, h: 600 })
  const pick = useRef(onSelect)

  useEffect(() => {
    pick.current = onSelect
  })
  const onPick = useCallback((id: string) => pick.current(id), [])

  useEffect(() => {
    const update = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])

  const blocked = useRef(new Set<Pulsable>())

  useEffect(() => {
    let raf = 0
    const tick = (t: number) => {
      pulseBlocked(blocked.current, t)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  useEffect(() => {
    const fg = fgRef.current
    if (fg) fg.scene().fog = new THREE.FogExp2(0x05060a, 0.002)
  }, [])

  const structureKey = plan.nodes.map(n => `${n.id}:${n.status}:${n.title}:${n.depends_on.join(',')}`).join('|')
  const data = useMemo(() => {
    return toGraphData(plan, cache)
  }, [structureKey]) // eslint-disable-line react-hooks/exhaustive-deps

  const neighbors = useMemo(() => {
    const set = new Set<string>()
    if (!selectedId) return set
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId) set.add(idOf(l.target))
      if (l.target === selectedId || idOf(l.target) === selectedId) set.add(idOf(l.source))
    }
    return set
  }, [data, selectedId])

  useEffect(() => {
    syncLabels(
      labels,
      plan.nodes.map(n => ({
        id: n.id,
        title: n.title,
        status: n.status,
        selected: n.id === selectedId,
        dim: !!selectedId && n.id !== selectedId && !neighbors.has(n.id),
      })),
      onPick,
    )
  }, [labels, plan, selectedId, neighbors, onPick])

  return (
    <div style={{ cursor: linkMode ? 'crosshair' : 'default' }}>
      <ForceGraph3D<GraphNode, GraphLink>
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#05060a"
        extraRenderers={extraRenderers}
        nodeThreeObject={(n: GraphNode) => {
          const selected = n.id === selectedId
          const dim = !!selectedId && !selected && !neighbors.has(n.id)
          const radius = selected ? 6.5 : 5
          const color = new THREE.Color(STATUS_COLORS[n.status])
          const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: n.status === 'done' ? 0.15 : 0.7, transparent: true, opacity: dim ? 0.18 : 1, roughness: 0.4 })
          const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 24, 24), mat)
          if (n.status === 'blocked') blocked.current.add(mesh as unknown as Pulsable)
          if (selected) {
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x5ac8fa, transparent: true, opacity: 0.85 })
            mesh.add(new THREE.Mesh(new THREE.TorusGeometry(radius + 3, 0.45, 8, 48), ringMat))
          }
          const label = new CSS2DObject(labelFor(labels, n.id, onPick))
          label.center.set(0.5, 0)
          label.position.set(0, -radius, 0)
          mesh.add(label)
          return mesh
        }}
        nodeThreeObjectExtend={false}
        linkColor={() => '#7a8399'}
        linkOpacity={0.5}
        linkWidth={(l: GraphLink) => (selectedId && (idOf(l.source) === selectedId || idOf(l.target) === selectedId) ? 2 : 0.6)}
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={(l: GraphLink) => (selectedId && idOf(l.target) === selectedId ? 2 : 0)}
        onNodeClick={(n: GraphNode) => onSelect(n.id)}
        onBackgroundClick={() => onSelect(null)}
        onLinkRightClick={(l: GraphLink) => onLinkRightClick(idOf(l.source), idOf(l.target))}
      />
    </div>
  )
}
```

Notes for the implementer:
- Labels live in a per-component `Map` and are reused across `nodeThreeObject` re-creations. three-forcegraph removes the old sphere with `scene.remove(mesh)`, which does not fire `removed` on the child `CSS2DObject`, so a fresh element per call would leak duplicate labels. `syncLabels` removes labels for deleted nodes.
- The label is a child of the sphere (`nodeThreeObjectExtend={false}`) rather than an extension of the default sphere. The custom emissive sphere and the blocked pulse need to stay (see "Spec ambiguities resolved").
- `three-render-objects` already gives each extra renderer's overlay `pointer-events: none`. The CSS below sets `pointer-events: auto` per label.
- The `nodeLabel` hover tooltip prop is gone because the label replaces it. That was `escapeHtml`'s only caller.

- [ ] **Step 4: Add label styles**

Append to `depgraph/src/app/globals.css`:

```css
.node-label {
  pointer-events: auto;
  cursor: pointer;
  padding-top: 8px;
  font-size: 12px;
  line-height: 1.25;
  white-space: nowrap;
  text-align: center;
  text-shadow: 0 1px 3px rgb(0 0 0 / 0.9);
  transition: opacity 120ms ease-out;
}
.node-label[data-status='todo'] { color: #c3cad6; }
.node-label[data-status='doing'] { color: #5ac8fa; }
.node-label[data-status='done'] { color: #7d8699; }
.node-label[data-status='blocked'] { color: #ff6b6b; }
.node-label[data-dim='true'] { opacity: 0.25; }
.node-label[data-selected='true'] .node-label-title { font-weight: 600; }
.node-label-id { display: none; font-family: ui-monospace, monospace; font-size: 10px; opacity: 0.6; }
.node-label:hover .node-label-id,
.node-label[data-selected='true'] .node-label-id { display: block; }
.node-label:focus-visible { outline: 2px solid rgb(90 200 250 / 0.7); outline-offset: 2px; border-radius: 4px; }
```

- [ ] **Step 5: Delete the dead tooltip escaper**

```bash
git rm src/lib/escapeHtml.ts src/lib/escapeHtml.test.ts
```

- [ ] **Step 6: Run e2e and watch it pass**

Run: `npm run test:e2e`
Expected: `6 passed`.

- [ ] **Step 7: Full check**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: Vitest `Test Files  11 passed (11)`, 0 failed; tsc prints nothing; eslint prints nothing; Playwright `6 passed`.

- [ ] **Step 8: Commit**

```bash
git add e2e/smoke.spec.ts src/components/Graph.tsx src/app/globals.css
git commit -m "depgraph: always-visible CSS2D node labels, selection torus" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

# Slice 7 — Selection reducer, hotkeys L/Esc, Add dependency

Outcome: `lib/selection.ts` replaces `lib/linkMode.ts`. Selecting a node and pressing **L** or the HUD's `link-button` arms linking; each node clicked next becomes a dependency of the selection; **Esc** backs out one step. A minimal `NodeHud` (title, `link-button`, `link-hint`, `hud-close`) appears; `NodePanel` still handles field edits until Slice 8. The Toolbar loses the Link-mode toggle and gains contract test ids.

### Task 7.1: Selection reducer — select, background, clear

**Files:**
- Create: `depgraph/src/lib/selection.ts`
- Test: `depgraph/src/lib/selection.test.ts`

**Interfaces:**
- Produces:
  - `export interface SelectionState { selectedId: string | null; arming: boolean }`
  - `export type SelectionEvent = { type: 'selectNode'; id: string } | { type: 'background' } | { type: 'armLink' } | { type: 'disarm' } | { type: 'escape' } | { type: 'clear' }`
  - `export type SelectionEffect = { type: 'none' } | { type: 'toast'; message: string } | { type: 'link'; dependencyId: string; dependentId: string }`
  - `export const initialSelection: SelectionState`
  - `export function selectionStep(state: SelectionState, event: SelectionEvent): { state: SelectionState; effect: SelectionEffect }`

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/lib/selection.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { initialSelection, selectionStep, type SelectionState } from './selection'

const none = { type: 'none' }
const selected = (id: string): SelectionState => ({ selectedId: id, arming: false })
const armed = (id: string): SelectionState => ({ selectedId: id, arming: true })

describe('selectionStep: selecting', () => {
  it('selectNode selects the node', () => {
    expect(selectionStep(initialSelection, { type: 'selectNode', id: 'a' })).toEqual({ state: selected('a'), effect: none })
    expect(selectionStep(selected('a'), { type: 'selectNode', id: 'b' })).toEqual({ state: selected('b'), effect: none })
  })

  it('background deselects', () => {
    expect(selectionStep(selected('a'), { type: 'background' })).toEqual({ state: initialSelection, effect: none })
  })

  it('clear resets everything, even while arming', () => {
    expect(selectionStep(armed('a'), { type: 'clear' })).toEqual({ state: initialSelection, effect: none })
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: FAIL with `Error: Failed to resolve import "./selection" from "src/lib/selection.test.ts". Does the file exist?`

- [ ] **Step 3: Write the minimal implementation**

Create `depgraph/src/lib/selection.ts`:

```ts
export interface SelectionState {
  selectedId: string | null
  arming: boolean
}

export type SelectionEvent =
  | { type: 'selectNode'; id: string }
  | { type: 'background' }
  | { type: 'armLink' }
  | { type: 'disarm' }
  | { type: 'escape' }
  | { type: 'clear' }

export type SelectionEffect =
  | { type: 'none' }
  | { type: 'toast'; message: string }
  | { type: 'link'; dependencyId: string; dependentId: string }

export const initialSelection: SelectionState = { selectedId: null, arming: false }

const none: SelectionEffect = { type: 'none' }

export function selectionStep(state: SelectionState, event: SelectionEvent): { state: SelectionState; effect: SelectionEffect } {
  switch (event.type) {
    case 'selectNode':
      return { state: { selectedId: event.id, arming: false }, effect: none }
    case 'background':
    case 'clear':
      return { state: initialSelection, effect: none }
    default:
      return { state, effect: none }
  }
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: PASS, `Tests  3 passed (3)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/selection.ts src/lib/selection.test.ts
git commit -m "depgraph: selection reducer — select, background, clear" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.2: Selection reducer — arming, linking, Esc

**Files:**
- Modify: `depgraph/src/lib/selection.ts`
- Test: `depgraph/src/lib/selection.test.ts`

**Interfaces:**
- Consumes/Produces: same exports as Task 7.1; behavior is now complete for all six events.

- [ ] **Step 1: Write the failing tests**

Append to `depgraph/src/lib/selection.test.ts`:

```ts
describe('selectionStep: linking', () => {
  it('armLink without a selection asks for one', () => {
    expect(selectionStep(initialSelection, { type: 'armLink' })).toEqual({
      state: initialSelection,
      effect: { type: 'toast', message: 'select a node first' },
    })
  })

  it('armLink with a selection arms', () => {
    expect(selectionStep(selected('a'), { type: 'armLink' })).toEqual({ state: armed('a'), effect: none })
  })

  it('while armed, clicking another node makes it a dependency of the selection and stays armed', () => {
    expect(selectionStep(armed('a'), { type: 'selectNode', id: 'b' })).toEqual({
      state: armed('a'),
      effect: { type: 'link', dependencyId: 'b', dependentId: 'a' },
    })
  })

  it('while armed, clicking the selection itself is refused', () => {
    expect(selectionStep(armed('a'), { type: 'selectNode', id: 'a' })).toEqual({
      state: armed('a'),
      effect: { type: 'toast', message: 'a node cannot depend on itself' },
    })
  })

  it('while armed, a background click only disarms', () => {
    expect(selectionStep(armed('a'), { type: 'background' })).toEqual({ state: selected('a'), effect: none })
  })

  it('disarm keeps the selection', () => {
    expect(selectionStep(armed('a'), { type: 'disarm' })).toEqual({ state: selected('a'), effect: none })
  })
})

describe('selectionStep: escape backs out one step', () => {
  it('armed -> selected -> nothing', () => {
    const one = selectionStep(armed('a'), { type: 'escape' })
    expect(one).toEqual({ state: selected('a'), effect: none })
    const two = selectionStep(one.state, { type: 'escape' })
    expect(two).toEqual({ state: initialSelection, effect: none })
    expect(selectionStep(two.state, { type: 'escape' })).toEqual({ state: initialSelection, effect: none })
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: FAIL, 7 failed / 3 passed (the three Task 7.1 tests). Examples: `armLink with a selection arms` → `AssertionError: expected { state: { selectedId: 'a', arming: false }, … } to deeply equal { state: { selectedId: 'a', arming: true }, … }`; `armLink without a selection` and `while armed, clicking another node …` → received `effect: { type: 'none' }`; `while armed, a background click only disarms` → received `state: { selectedId: null, arming: false }`; `escape` and `disarm` fail because the `default` branch leaves `arming: true`.

- [ ] **Step 3: Write the implementation**

Replace the `selectionStep` function in `depgraph/src/lib/selection.ts` with:

```ts
export function selectionStep(state: SelectionState, event: SelectionEvent): { state: SelectionState; effect: SelectionEffect } {
  switch (event.type) {
    case 'selectNode':
      if (state.arming && state.selectedId) {
        if (event.id === state.selectedId) {
          return { state, effect: { type: 'toast', message: 'a node cannot depend on itself' } }
        }
        return { state, effect: { type: 'link', dependencyId: event.id, dependentId: state.selectedId } }
      }
      return { state: { selectedId: event.id, arming: false }, effect: none }
    case 'background':
    case 'escape':
      if (state.arming) return { state: { ...state, arming: false }, effect: none }
      return { state: initialSelection, effect: none }
    case 'armLink':
      if (!state.selectedId) return { state, effect: { type: 'toast', message: 'select a node first' } }
      return { state: { ...state, arming: true }, effect: none }
    case 'disarm':
      return { state: { ...state, arming: false }, effect: none }
    case 'clear':
      return { state: initialSelection, effect: none }
  }
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: PASS, `Tests  10 passed (10)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/selection.ts src/lib/selection.test.ts
git commit -m "depgraph: selection reducer — arm link, link on click, Esc steps back" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.3: `hotkeyName` and `isTypingTarget`

**Files:**
- Create: `depgraph/src/hooks/useHotkeys.ts`
- Test: `depgraph/src/hooks/useHotkeys.test.tsx`

**Interfaces:**
- Produces:
  - `export type HotkeyMap = Partial<Record<string, () => void>>`
  - `export function hotkeyName(e: Pick<KeyboardEvent, 'key' | 'shiftKey' | 'metaKey' | 'ctrlKey' | 'altKey'>): string | null`. Names: `'a'…'z'`, `'shift+a'…'shift+z'`, `'1'…'9'`, `'escape'`, `'delete'` (from `Delete` or `Backspace`). Returns `null` for anything else or when Meta/Ctrl/Alt is held.
  - `export function isTypingTarget(target: EventTarget | null): boolean`, true for input, textarea, select and contenteditable.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/hooks/useHotkeys.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup } from '@testing-library/react'
import { hotkeyName, isTypingTarget } from './useHotkeys'

afterEach(() => {
  cleanup()
  document.body.innerHTML = ''
})

type Mods = Partial<Record<'shiftKey' | 'metaKey' | 'ctrlKey' | 'altKey', boolean>>
const k = (key: string, mods: Mods = {}) =>
  hotkeyName({ key, shiftKey: false, metaKey: false, ctrlKey: false, altKey: false, ...mods })

describe('hotkeyName', () => {
  it('names letters (lower-cased), shifted letters and digits', () => {
    expect(k('l')).toBe('l')
    expect(k('L')).toBe('l')
    expect(k('N', { shiftKey: true })).toBe('shift+n')
    expect(k('1')).toBe('1')
    expect(k('4')).toBe('4')
  })

  it('names Escape and both delete keys', () => {
    expect(k('Escape')).toBe('escape')
    expect(k('Delete')).toBe('delete')
    expect(k('Backspace')).toBe('delete')
  })

  it('ignores other keys and any Meta/Ctrl/Alt chord', () => {
    expect(k('Enter')).toBeNull()
    expect(k('ArrowUp')).toBeNull()
    expect(k('l', { metaKey: true })).toBeNull()
    expect(k('l', { ctrlKey: true })).toBeNull()
    expect(k('l', { altKey: true })).toBeNull()
  })
})

describe('isTypingTarget', () => {
  it('is true for text entry elements and false otherwise', () => {
    const make = (html: string) => {
      document.body.innerHTML = html
      return document.body.firstElementChild
    }
    expect(isTypingTarget(make('<input />'))).toBe(true)
    expect(isTypingTarget(make('<textarea></textarea>'))).toBe(true)
    expect(isTypingTarget(make('<select><option>a</option></select>'))).toBe(true)
    expect(isTypingTarget(make('<div contenteditable="true"><b>x</b></div>')?.firstElementChild ?? null)).toBe(true)
    expect(isTypingTarget(make('<button>x</button>'))).toBe(false)
    expect(isTypingTarget(window)).toBe(false)
    expect(isTypingTarget(null)).toBe(false)
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/hooks/useHotkeys.test.tsx`
Expected: FAIL with `Error: Failed to resolve import "./useHotkeys" from "src/hooks/useHotkeys.test.tsx". Does the file exist?`

- [ ] **Step 3: Write the minimal implementation**

Create `depgraph/src/hooks/useHotkeys.ts`:

```ts
'use client'

export type HotkeyMap = Partial<Record<string, () => void>>

export function hotkeyName(e: Pick<KeyboardEvent, 'key' | 'shiftKey' | 'metaKey' | 'ctrlKey' | 'altKey'>): string | null {
  if (e.metaKey || e.ctrlKey || e.altKey) return null
  if (e.key === 'Escape') return 'escape'
  if (e.key === 'Delete' || e.key === 'Backspace') return 'delete'
  if (/^[1-9]$/.test(e.key)) return e.key
  if (/^[a-z]$/i.test(e.key)) return (e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()
  return null
}

export function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') return true
  // jsdom lacks isContentEditable, so check the attribute on the element or an ancestor.
  return target.closest('[contenteditable]:not([contenteditable="false"])') !== null
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/hooks/useHotkeys.test.tsx`
Expected: PASS, `Tests  4 passed (4)`.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/useHotkeys.ts src/hooks/useHotkeys.test.tsx
git commit -m "depgraph: hotkey naming and typing-target detection" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.4: `useHotkeys` hook

**Files:**
- Modify: `depgraph/src/hooks/useHotkeys.ts`
- Test: `depgraph/src/hooks/useHotkeys.test.tsx`

**Interfaces:**
- Consumes: `hotkeyName`, `isTypingTarget` (Task 7.3).
- Produces: `export function useHotkeys(map: HotkeyMap): void`. It listens for `keydown` on `window`, skips events that are `defaultPrevented` or come from a typing target, calls the bound handler, and calls `preventDefault()`. It always uses the latest `map` (via `useEffectEvent`).

- [ ] **Step 1: Write the failing tests**

In `depgraph/src/hooks/useHotkeys.test.tsx`, change the two import lines to:

```tsx
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, renderHook } from '@testing-library/react'
import { hotkeyName, isTypingTarget, useHotkeys } from './useHotkeys'
```

and append:

```tsx
describe('useHotkeys', () => {
  it('calls the bound handler and prevents the default action', () => {
    const l = vi.fn()
    renderHook(() => useHotkeys({ l }))
    expect(fireEvent.keyDown(window, { key: 'l' })).toBe(false)
    expect(l).toHaveBeenCalledTimes(1)
  })

  it('ignores keys typed into inputs and keys with no binding', () => {
    const l = vi.fn()
    renderHook(() => useHotkeys({ l }))
    const input = document.createElement('input')
    document.body.append(input)
    expect(fireEvent.keyDown(input, { key: 'l' })).toBe(true)
    expect(fireEvent.keyDown(window, { key: 'x' })).toBe(true)
    expect(l).not.toHaveBeenCalled()
  })

  it('uses the latest handlers after a rerender and detaches on unmount', () => {
    const first = vi.fn()
    const second = vi.fn()
    const { rerender, unmount } = renderHook(({ fn }) => useHotkeys({ escape: fn }), { initialProps: { fn: first } })
    rerender({ fn: second })
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(first).not.toHaveBeenCalled()
    expect(second).toHaveBeenCalledTimes(1)
    unmount()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(second).toHaveBeenCalledTimes(1)
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/hooks/useHotkeys.test.tsx`
Expected: FAIL, 3 failed / 4 passed, each like `TypeError: (0 , __vi_import_0__.useHotkeys) is not a function`.

- [ ] **Step 3: Write the implementation**

In `depgraph/src/hooks/useHotkeys.ts`, replace the line `'use client'` with:

```ts
'use client'
import { useEffect, useEffectEvent } from 'react'
```

and append:

```ts
export function useHotkeys(map: HotkeyMap): void {
  const onKey = useEffectEvent((e: KeyboardEvent) => {
    if (e.defaultPrevented || isTypingTarget(e.target)) return
    const name = hotkeyName(e)
    const handler = name ? map[name] : undefined
    if (!handler) return
    e.preventDefault()
    handler()
  })
  useEffect(() => {
    const listener = (e: KeyboardEvent) => onKey(e)
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [])
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/hooks/useHotkeys.test.tsx`
Expected: PASS, `Tests  7 passed (7)`.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/useHotkeys.ts src/hooks/useHotkeys.test.tsx
git commit -m "depgraph: useHotkeys — window keydown, ignored while typing" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.5: Slim `Toolbar` with contract test ids

**Files:**
- Modify: `depgraph/src/components/Toolbar.tsx` (full file below)
- Test: `depgraph/src/components/Toolbar.test.tsx`

**Interfaces:**
- Consumes: `PlanSummary` from `@/lib/store`; `useRouter` from `next/navigation`.
- Produces: `Toolbar` props `{ plans: PlanSummary[]; slug: string; planName: string; nodeCount: number; onAddNode: () => void; onNewPlan: () => void }`. The `linkMode` and `onToggleLinkMode` props are removed. Test ids: `plan-select`, `node-count`, `add-node`, `new-plan`.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/components/Toolbar.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import Toolbar from './Toolbar'

const { push } = vi.hoisted(() => ({ push: vi.fn() }))
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }))

afterEach(() => {
  cleanup()
  push.mockReset()
})

const plans = [
  { slug: 'a', name: 'Plan A', nodeCount: 2 },
  { slug: 'b', name: 'Plan B', nodeCount: 0 },
]

function setup() {
  const onAddNode = vi.fn()
  const onNewPlan = vi.fn()
  render(<Toolbar plans={plans} slug="a" planName="Plan A" nodeCount={2} onAddNode={onAddNode} onNewPlan={onNewPlan} />)
  return { onAddNode, onNewPlan }
}

describe('Toolbar', () => {
  it('exposes the contract controls and no Link-mode toggle', () => {
    setup()
    expect(screen.getByTestId('plan-select')).toBe(screen.getByRole('combobox', { name: 'Plan' }))
    expect(screen.getByTestId('node-count').textContent).toBe('2 nodes')
    expect(screen.getByTestId('add-node')).toBe(screen.getByRole('button', { name: 'Add node' }))
    expect(screen.getByTestId('new-plan')).toBe(screen.getByRole('button', { name: 'New plan' }))
    expect(screen.queryByRole('button', { name: 'Link mode' })).toBeNull()
  })

  it('buttons call their handlers and the select navigates', () => {
    const { onAddNode, onNewPlan } = setup()
    fireEvent.click(screen.getByRole('button', { name: 'Add node' }))
    fireEvent.click(screen.getByRole('button', { name: 'New plan' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Plan' }), { target: { value: 'b' } })
    expect(onAddNode).toHaveBeenCalledTimes(1)
    expect(onNewPlan).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith('/?plan=b')
  })
})
```

- [ ] **Step 2: Run them and watch the contract test fail**

Run: `npx vitest run src/components/Toolbar.test.tsx`
Expected: FAIL, 1 failed / 1 passed. Failure: `TestingLibraryElementError: Unable to find an element by: [data-testid="plan-select"]`. The handler test already passes against the current Toolbar and stays as a regression guard.

- [ ] **Step 3: Write the implementation**

Replace `depgraph/src/components/Toolbar.tsx` with:

```tsx
'use client'
import { useRouter } from 'next/navigation'
import type { PlanSummary } from '@/lib/store'

interface ToolbarProps {
  plans: PlanSummary[]
  slug: string
  planName: string
  nodeCount: number
  onAddNode: () => void
  onNewPlan: () => void
}

const btn = 'inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-medium transition-colors hover:bg-white/10'

export default function Toolbar(p: ToolbarProps) {
  const router = useRouter()
  return (
    <div className="fixed left-4 top-4 z-10 flex items-center gap-2 glass rounded-xl p-2">
      <select
        data-testid="plan-select"
        aria-label="Plan"
        className="rounded-md border border-white/10 bg-black/40 px-2 py-1 text-xs"
        value={p.slug}
        onChange={e => router.push(`/?plan=${e.target.value}`)}
      >
        {p.plans.map(pl => (
          <option key={pl.slug} value={pl.slug}>
            {pl.name}
          </option>
        ))}
      </select>
      <span data-testid="node-count" className="font-mono text-xs text-white/50">
        {p.nodeCount} nodes
      </span>
      <button type="button" data-testid="add-node" aria-label="Add node" className={btn} onClick={p.onAddNode}>
        + Node
      </button>
      <button type="button" data-testid="new-plan" aria-label="New plan" className={btn} onClick={p.onNewPlan}>
        New plan
      </button>
    </div>
  )
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/Toolbar.test.tsx`
Expected: PASS, `Tests  2 passed (2)`. (`npx tsc --noEmit` now fails in `page.tsx` on the removed props. Task 7.7 fixes that before the slice commit, so do not run the full check yet.)

- [ ] **Step 5: Commit**

```bash
git add src/components/Toolbar.tsx src/components/Toolbar.test.tsx
git commit -m "depgraph: slim toolbar with contract test ids, drop link-mode toggle" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.6: `NodeHud` shell (region, Add dependency, hint, Close)

**Files:**
- Create: `depgraph/src/components/NodeHud.tsx`
- Test: `depgraph/src/components/NodeHud.test.tsx`

**Interfaces:**
- Consumes: `PlanNode` from `@/lib/schema`.
- Produces: `export interface NodeHudProps { node: PlanNode; armed: boolean; onToggleLink: () => void; onClose: () => void }`, default export `NodeHud`. Test ids: `node-hud`, `link-button`, `link-hint`, `hud-close`. Slice 8 extends these props.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/components/NodeHud.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import NodeHud, { type NodeHudProps } from './NodeHud'
import type { PlanNode } from '@/lib/schema'

afterEach(cleanup)

const node: PlanNode = { id: 'b', title: 'Beta', description: '', status: 'doing', tags: [], depends_on: [] }

function setup(overrides: Partial<NodeHudProps> = {}) {
  const props: NodeHudProps = { node, armed: false, onToggleLink: vi.fn(), onClose: vi.fn(), ...overrides }
  render(<NodeHud {...props} />)
  return props
}

describe('NodeHud shell', () => {
  it('is the "Selected node" region', () => {
    setup()
    expect(screen.getByRole('region', { name: 'Selected node' })).toBe(screen.getByTestId('node-hud'))
  })

  it('Add dependency is a toggle button', () => {
    const props = setup()
    const arm = screen.getByRole('button', { name: 'Add dependency' })
    expect(arm).toBe(screen.getByTestId('link-button'))
    expect(arm.getAttribute('aria-pressed')).toBe('false')
    expect(screen.queryByTestId('link-hint')).toBeNull()
    fireEvent.click(arm)
    expect(props.onToggleLink).toHaveBeenCalledTimes(1)
  })

  it('while armed, the button is pressed and a status hint names the node', () => {
    setup({ armed: true })
    expect(screen.getByTestId('link-button').getAttribute('aria-pressed')).toBe('true')
    const hint = screen.getByTestId('link-hint')
    expect(hint.getAttribute('role')).toBe('status')
    expect(hint.textContent).toBe('Pick what Beta needs')
  })

  it('Close calls onClose', () => {
    const props = setup()
    fireEvent.click(screen.getByRole('button', { name: 'Close' }))
    expect(screen.getByTestId('hud-close')).toBeTruthy()
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: FAIL with `Error: Failed to resolve import "./NodeHud" from "src/components/NodeHud.test.tsx". Does the file exist?`

- [ ] **Step 3: Write the minimal implementation**

Create `depgraph/src/components/NodeHud.tsx`:

```tsx
'use client'
import type { PlanNode } from '@/lib/schema'

export interface NodeHudProps {
  node: PlanNode
  armed: boolean
  onToggleLink: () => void
  onClose: () => void
}

const chip = 'inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs transition-colors hover:bg-white/10'

export default function NodeHud({ node, armed, onToggleLink, onClose }: NodeHudProps) {
  return (
    <section
      data-testid="node-hud"
      aria-label="Selected node"
      className="glass fixed bottom-4 left-1/2 z-10 flex w-[560px] max-w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-2 rounded-xl p-3"
    >
      <div className="flex items-center gap-3">
        <span className="min-w-0 flex-1 truncate text-sm font-semibold">{node.title}</span>
        <button
          type="button"
          data-testid="link-button"
          aria-label="Add dependency"
          aria-pressed={armed}
          className={`${chip} ${armed ? 'border-sky-400/60 bg-sky-500/20 text-sky-100' : ''}`}
          onClick={onToggleLink}
        >
          +L
        </button>
        <button type="button" data-testid="hud-close" aria-label="Close" className="text-xs text-white/50 hover:text-white" onClick={onClose}>
          ✕
        </button>
      </div>
      {armed && (
        <p role="status" data-testid="link-hint" className="text-xs text-sky-200">
          Pick what {node.title} needs
        </p>
      )}
    </section>
  )
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: PASS, `Tests  4 passed (4)`.

- [ ] **Step 5: Commit**

```bash
git add src/components/NodeHud.tsx src/components/NodeHud.test.tsx
git commit -m "depgraph: NodeHud shell — Add dependency toggle, link hint, close" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 7.7: Wire selection + hotkeys into the page (e2e); delete `linkMode`; full check

**Files:**
- Modify: `depgraph/e2e/smoke.spec.ts` (replace tests 3 and 4)
- Modify: `depgraph/src/app/page.tsx` (full file below)
- Modify: `depgraph/src/components/Graph.tsx` (rename `linkMode` → `arming`)
- Modify: `depgraph/src/app/globals.css` (append)
- Delete: `depgraph/src/lib/linkMode.ts`, `depgraph/src/lib/linkMode.test.ts`

**Interfaces:**
- Consumes: `selectionStep`, `initialSelection`, `SelectionEvent`, `SelectionState` (7.1–7.2); `useHotkeys` (7.4); `Toolbar` props (7.5); `NodeHud` shell props (7.6).
- Produces: `Graph` props become `{ plan: Plan; selectedId: string | null; arming: boolean; onSelect: (id: string | null) => void; onLinkRightClick: (dependencyId: string, dependentId: string) => void }`. The page dispatches `selectionStep` against the normalized state `{ selectedId: activeId, arming: armed }`, where `activeId` is the selection only if that node still exists.

- [ ] **Step 1: Write the failing e2e tests**

In `depgraph/e2e/smoke.spec.ts`, replace the whole `test('link mode toggles and hints', …)` block with:

```ts
test('Add dependency arms, Esc disarms', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'api-routes').click()
  const hud = page.getByTestId('node-hud')
  const arm = page.getByRole('button', { name: 'Add dependency', exact: true })
  await expect(hud).toBeVisible()
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await arm.click()
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('link-hint')).toHaveText('Pick what Write API routes needs')
  await page.keyboard.press('Escape')
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await expect(page.getByTestId('link-hint')).toBeHidden()
  await expect(hud).toBeVisible()
  await page.keyboard.press('l')
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await page.keyboard.press('Escape')
  await page.keyboard.press('Escape')
  await expect(hud).toBeHidden()
})
```

and replace the whole `test('cycle is refused with an error', …)` block with:

```ts
test('cycle is refused with an error', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await page.getByRole('button', { name: 'Add dependency', exact: true }).click()
  await label(page, 'api-routes').click()
  await expect(page.getByTestId('toast')).toContainText('cycle:')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toMatch(/"id": "schema"[\s\S]*?"depends_on": \[\s*"design-spec"\s*\]/)
  const res = await page.request.put('/api/plans/example', {
    data: {
      name: 'x',
      nodes: [
        { id: 'a', title: 'A', depends_on: ['b'] },
        { id: 'b', title: 'B', depends_on: ['a'] },
      ],
    },
  })
  expect(res.status()).toBe(400)
  expect((await res.json()).errors[0]).toMatch(/^cycle:/)
})
```

(In the example plan, `api-routes` already depends on `schema`. Making `schema` need `api-routes` is therefore a cycle, and `apply` must refuse it.)

- [ ] **Step 2: Run e2e and watch them fail**

Run: `npm run test:e2e`
Expected: `2 failed`, `4 passed`.
- `Add dependency arms, Esc disarms`: `expect(locator).toBeVisible()` fails for `getByTestId('node-hud')` (element(s) not found).
- `cycle is refused with an error`: `locator.click: Test timeout of 60000ms exceeded` waiting for `getByRole('button', { name: 'Add dependency', exact: true })`.

- [ ] **Step 3: Rename the Graph prop** (no unit test possible (WebGL); covered by e2e test "cycle is refused with an error")

In `depgraph/src/components/Graph.tsx`:

Replace

```tsx
  linkMode: boolean
```

with

```tsx
  arming: boolean
```

Replace

```tsx
export default function Graph({ plan, selectedId, linkMode, onSelect, onLinkRightClick }: GraphProps) {
```

with

```tsx
export default function Graph({ plan, selectedId, arming, onSelect, onLinkRightClick }: GraphProps) {
```

Replace

```tsx
    <div style={{ cursor: linkMode ? 'crosshair' : 'default' }}>
```

with

```tsx
    <div data-arming={arming} style={{ cursor: arming ? 'crosshair' : 'default' }}>
```

Append to `depgraph/src/app/globals.css`:

```css
[data-arming='true'] .node-label { cursor: crosshair; }
```

- [ ] **Step 4: Rewrite the page**

Replace `depgraph/src/app/page.tsx` with:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import NodePanel from '@/components/NodePanel'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import { initialSelection, selectionStep, type SelectionEvent, type SelectionState } from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
  const toast = useToast()
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') report(apply(p => addDependency(p, effect.dependencyId, effect.dependentId)))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
  })

  const handleAddNode = () => {
    let newId = ''
    const errors = apply(p => {
      const r = addNode(p)
      newId = r.id
      return r.plan
    })
    report(errors)
    if (!errors.length && newId) setSelection({ selectedId: newId, arming: false })
  }

  const handleNewPlan = async () => {
    const name = window.prompt('Plan name')
    if (!name) return
    const res = await fetch('/api/plans', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const body = await res.json()
    if (!res.ok) {
      toast.show((body.errors as string[]).join('; '))
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={activeId}
        arming={armed}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {activeId && !armed && (
        <NodePanel
          key={activeId}
          plan={plan}
          nodeId={activeId}
          onChange={patch => apply(p => updateNode(p, activeId, patch))}
          onDelete={() => {
            report(apply(p => deleteNode(p, activeId)))
            dispatch({ type: 'clear' })
          }}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      {activeNode && (
        <NodeHud node={activeNode} armed={armed} onToggleLink={toggleLink} onClose={() => dispatch({ type: 'clear' })} />
      )}
      <Toast message={toast.message} />
      <SaveIndicator state={saveState} error={saveError} />
    </>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center font-mono text-sm text-white/50">{text}</div>
}

export default function Page() {
  return (
    <Suspense>
      <Workspace />
    </Suspense>
  )
}
```

- [ ] **Step 5: Delete the old link-mode machine**

```bash
git rm src/lib/linkMode.ts src/lib/linkMode.test.ts
```

- [ ] **Step 6: Run e2e and watch it pass**

Run: `npm run test:e2e`
Expected: `6 passed`.

- [ ] **Step 7: Full check**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: Vitest `Test Files  14 passed (14)`, 0 failed; tsc and eslint print nothing; Playwright `6 passed`.

- [ ] **Step 8: Commit**

```bash
git add e2e/smoke.spec.ts src/app/page.tsx src/components/Graph.tsx src/app/globals.css
git commit -m "depgraph: selection reducer drives page — L arms linking, Esc steps back, HUD link button" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

# Slice 8 — The HUD card replaces `NodePanel`

Outcome: the bottom card holds inline title rename, status pips, click-to-expand description, tag chips with ×/+, "needs:" chips (click selects and flies the camera, × removes), read-only "unlocks:" chips, **+L**, two-step delete (disarms after 3 s) and close. `NodePanel.tsx` is deleted.

### Task 8.1: Reducer `focusNode` event and `NodeSignal`

**Files:**
- Modify: `depgraph/src/lib/selection.ts`
- Test: `depgraph/src/lib/selection.test.ts`

**Interfaces:**
- Produces:
  - `SelectionEvent` gains `{ type: 'focusNode'; id: string }`. It selects the node and disarms, even while armed, so clicking a chip never creates a link.
  - `export interface NodeSignal { id: string; seq: number }` is a one-shot request token (camera fly, shake).
  - `export function nextSignal(prev: NodeSignal | null, id: string): NodeSignal`

- [ ] **Step 1: Write the failing tests**

In `depgraph/src/lib/selection.test.ts`, change the import to:

```ts
import { initialSelection, nextSignal, selectionStep, type SelectionState } from './selection'
```

and append:

```ts
describe('selectionStep: focusNode (chip navigation)', () => {
  it('selects the node and disarms instead of linking', () => {
    expect(selectionStep(armed('a'), { type: 'focusNode', id: 'b' })).toEqual({ state: selected('b'), effect: none })
    expect(selectionStep(initialSelection, { type: 'focusNode', id: 'b' })).toEqual({ state: selected('b'), effect: none })
  })
})

describe('nextSignal', () => {
  it('bumps the sequence so the same id can be requested twice', () => {
    const one = nextSignal(null, 'a')
    expect(one).toEqual({ id: 'a', seq: 1 })
    expect(nextSignal(one, 'a')).toEqual({ id: 'a', seq: 2 })
    expect(nextSignal(one, 'b')).toEqual({ id: 'b', seq: 2 })
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: FAIL, 2 failed / 10 passed: `focusNode` → `expected undefined to deeply equal { state: …, effect: … }` (no case matches); `nextSignal` → `TypeError: (0 , __vi_import_0__.nextSignal) is not a function`.

- [ ] **Step 3: Write the implementation**

In `depgraph/src/lib/selection.ts`:

Replace

```ts
  | { type: 'selectNode'; id: string }
```

with

```ts
  | { type: 'selectNode'; id: string }
  | { type: 'focusNode'; id: string }
```

In `selectionStep`, add before `case 'background':`:

```ts
    case 'focusNode':
      return { state: { selectedId: event.id, arming: false }, effect: none }
```

Append to the file:

```ts
export interface NodeSignal {
  id: string
  seq: number
}

export function nextSignal(prev: NodeSignal | null, id: string): NodeSignal {
  return { id, seq: (prev?.seq ?? 0) + 1 }
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/selection.test.ts`
Expected: PASS, `Tests  12 passed (12)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/selection.ts src/lib/selection.test.ts
git commit -m "depgraph: focusNode event and NodeSignal request token" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.2: Camera math `cameraFor`

**Files:**
- Create: `depgraph/src/lib/camera.ts`
- Test: `depgraph/src/lib/camera.test.ts`

**Interfaces:**
- Produces: `export interface Vec3 { x: number; y: number; z: number }`; `export const FLY_DISTANCE = 120`; `export function cameraFor(node: { x?: number; y?: number; z?: number }, distance?: number): { position: Vec3; lookAt: Vec3 }`. The camera sits `distance` away from the node, on the ray from the origin through the node.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/lib/camera.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { FLY_DISTANCE, cameraFor } from './camera'

describe('cameraFor', () => {
  it('looks at the node from FLY_DISTANCE further out along the ray from the origin', () => {
    expect(FLY_DISTANCE).toBe(120)
    expect(cameraFor({ x: 0, y: 0, z: 30 })).toEqual({ position: { x: 0, y: 0, z: 150 }, lookAt: { x: 0, y: 0, z: 30 } })
  })

  it('keeps exactly `distance` between camera and node', () => {
    const { position, lookAt } = cameraFor({ x: 3, y: 4, z: 0 }, 5)
    expect(position).toEqual({ x: 6, y: 8, z: 0 })
    expect(Math.hypot(position.x - lookAt.x, position.y - lookAt.y, position.z - lookAt.z)).toBeCloseTo(5)
  })

  it('treats a node at (or without) coordinates at the origin by looking down +z', () => {
    expect(cameraFor({})).toEqual({ position: { x: 0, y: 0, z: 120 }, lookAt: { x: 0, y: 0, z: 0 } })
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/camera.test.ts`
Expected: FAIL with `Error: Failed to resolve import "./camera" from "src/lib/camera.test.ts". Does the file exist?`

- [ ] **Step 3: Write the implementation**

Create `depgraph/src/lib/camera.ts`:

```ts
export interface Vec3 {
  x: number
  y: number
  z: number
}

export const FLY_DISTANCE = 120

export function cameraFor(node: { x?: number; y?: number; z?: number }, distance = FLY_DISTANCE): { position: Vec3; lookAt: Vec3 } {
  const lookAt = { x: node.x ?? 0, y: node.y ?? 0, z: node.z ?? 0 }
  const r = Math.hypot(lookAt.x, lookAt.y, lookAt.z)
  if (r === 0) return { position: { x: 0, y: 0, z: distance }, lookAt }
  const k = 1 + distance / r
  return { position: { x: lookAt.x * k, y: lookAt.y * k, z: lookAt.z * k }, lookAt }
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/camera.test.ts`
Expected: PASS, `Tests  3 passed (3)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/camera.ts src/lib/camera.test.ts
git commit -m "depgraph: cameraFor — fly-to camera position" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.3: `useConfirm` two-step confirm

**Files:**
- Create: `depgraph/src/hooks/useConfirm.ts`
- Test: `depgraph/src/hooks/useConfirm.test.tsx`

**Interfaces:**
- Produces: `export function useConfirm(ms?: number): { isArmed: (key: string) => boolean; press: (key: string, action: () => void) => void }`. The default `ms` is 3000. The first `press(key)` arms that key. A second `press(key)` runs `action` and disarms. A `press` on another key re-arms for that key. The hook disarms itself after `ms`.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/hooks/useConfirm.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, renderHook } from '@testing-library/react'
import { useConfirm } from './useConfirm'

beforeEach(() => {
  vi.useFakeTimers()
})
afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('useConfirm', () => {
  it('first press arms only that key; second press runs the action once and disarms', () => {
    const { result } = renderHook(() => useConfirm(3000))
    const action = vi.fn()
    act(() => result.current.press('a', action))
    expect(result.current.isArmed('a')).toBe(true)
    expect(result.current.isArmed('b')).toBe(false)
    expect(action).not.toHaveBeenCalled()
    act(() => result.current.press('a', action))
    expect(action).toHaveBeenCalledTimes(1)
    expect(result.current.isArmed('a')).toBe(false)
  })

  it('disarms by itself after 3 s without acting', () => {
    const { result } = renderHook(() => useConfirm())
    const action = vi.fn()
    act(() => result.current.press('a', action))
    act(() => {
      vi.advanceTimersByTime(2999)
    })
    expect(result.current.isArmed('a')).toBe(true)
    act(() => {
      vi.advanceTimersByTime(1)
    })
    expect(result.current.isArmed('a')).toBe(false)
    expect(action).not.toHaveBeenCalled()
  })

  it('pressing another key re-arms for that key without acting', () => {
    const { result } = renderHook(() => useConfirm())
    const action = vi.fn()
    act(() => result.current.press('a', action))
    act(() => result.current.press('b', action))
    expect(result.current.isArmed('a')).toBe(false)
    expect(result.current.isArmed('b')).toBe(true)
    expect(action).not.toHaveBeenCalled()
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/hooks/useConfirm.test.tsx`
Expected: FAIL with `Error: Failed to resolve import "./useConfirm" from "src/hooks/useConfirm.test.tsx". Does the file exist?`

- [ ] **Step 3: Write the implementation**

Create `depgraph/src/hooks/useConfirm.ts`:

```ts
'use client'
import { useEffect, useRef, useState } from 'react'

export function useConfirm(ms = 3000) {
  const [armedKey, setArmedKey] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current)
    },
    [],
  )

  const press = (key: string, action: () => void) => {
    if (timer.current) clearTimeout(timer.current)
    timer.current = null
    if (armedKey === key) {
      setArmedKey(null)
      action()
      return
    }
    setArmedKey(key)
    timer.current = setTimeout(() => setArmedKey(null), ms)
  }

  const isArmed = (key: string) => armedKey === key

  return { isArmed, press }
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/hooks/useConfirm.test.tsx`
Expected: PASS, `Tests  3 passed (3)`.

- [ ] **Step 5: Commit**

```bash
git add src/hooks/useConfirm.ts src/hooks/useConfirm.test.tsx
git commit -m "depgraph: useConfirm — two-step confirm that disarms after 3 s" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.4: `StatusPips` (+ `Keycap`)

**Files:**
- Create: `depgraph/src/components/Keycap.tsx`, `depgraph/src/components/StatusPips.tsx`
- Test: `depgraph/src/components/StatusPips.test.tsx`

**Interfaces:**
- Consumes: `STATUSES`, `Status` from `@/lib/schema`.
- Produces:
  - `Keycap({ children }: { children: ReactNode })`, an `aria-hidden` `<kbd>` hint that never changes accessible names.
  - `StatusPips({ value, onChange }: { value: Status; onChange: (status: Status) => void })`, a radiogroup "Status" with radios named `todo|doing|done|blocked`, test ids `status-pip-<s>` and `aria-checked` on the current status. Clicking the current status is a no-op.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/components/StatusPips.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import StatusPips from './StatusPips'

afterEach(cleanup)

describe('StatusPips', () => {
  it('is a Status radiogroup with one radio per status and the current one checked', () => {
    render(<StatusPips value="doing" onChange={() => {}} />)
    const group = screen.getByRole('radiogroup', { name: 'Status' })
    const radios = within(group).getAllByRole('radio')
    expect(radios.map(r => r.getAttribute('aria-label'))).toEqual(['todo', 'doing', 'done', 'blocked'])
    expect(screen.getByRole('radio', { name: 'doing' })).toBe(screen.getByTestId('status-pip-doing'))
    expect(screen.getByTestId('status-pip-doing').getAttribute('aria-checked')).toBe('true')
    expect(screen.getByTestId('status-pip-todo').getAttribute('aria-checked')).toBe('false')
    expect(screen.getByTestId('status-pip-done').textContent).toContain('3')
  })

  it('clicking another pip reports it; clicking the current one does nothing', () => {
    const onChange = vi.fn()
    render(<StatusPips value="doing" onChange={onChange} />)
    fireEvent.click(screen.getByRole('radio', { name: 'done' }))
    fireEvent.click(screen.getByRole('radio', { name: 'doing' }))
    expect(onChange.mock.calls).toEqual([['done']])
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/components/StatusPips.test.tsx`
Expected: FAIL with `Error: Failed to resolve import "./StatusPips" from "src/components/StatusPips.test.tsx". Does the file exist?`

- [ ] **Step 3: Write the implementation**

Create `depgraph/src/components/Keycap.tsx`:

```tsx
import type { ReactNode } from 'react'

export default function Keycap({ children }: { children: ReactNode }) {
  return (
    <kbd aria-hidden="true" className="rounded border border-white/15 bg-white/5 px-1 font-mono text-[10px] leading-4 text-white/50">
      {children}
    </kbd>
  )
}
```

Create `depgraph/src/components/StatusPips.tsx`:

```tsx
'use client'
import Keycap from '@/components/Keycap'
import { STATUSES, type Status } from '@/lib/schema'

const ON: Record<Status, string> = {
  todo: 'border-slate-300/50 text-slate-200',
  doing: 'border-sky-400/60 text-sky-200',
  done: 'border-slate-400/50 text-slate-300',
  blocked: 'border-red-400/60 text-red-200',
}

export default function StatusPips({ value, onChange }: { value: Status; onChange: (status: Status) => void }) {
  return (
    <div role="radiogroup" aria-label="Status" className="flex items-center gap-1">
      {STATUSES.map((s, i) => {
        const on = s === value
        return (
          <button
            key={s}
            type="button"
            role="radio"
            aria-checked={on}
            aria-label={s}
            data-testid={`status-pip-${s}`}
            className={`inline-flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-[11px] transition-colors ${
              on ? ON[s] : 'border-transparent text-white/40 hover:text-white/70'
            }`}
            onClick={() => {
              if (!on) onChange(s)
            }}
          >
            <span aria-hidden="true">{on ? '●' : '○'}</span>
            <span aria-hidden="true">{s}</span>
            <Keycap>{i + 1}</Keycap>
          </button>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/StatusPips.test.tsx`
Expected: PASS, `Tests  2 passed (2)`.

- [ ] **Step 5: Commit**

```bash
git add src/components/Keycap.tsx src/components/StatusPips.tsx src/components/StatusPips.test.tsx
git commit -m "depgraph: StatusPips radiogroup with keycap hints" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.5: `InlineText` click-to-edit

**Files:**
- Create: `depgraph/src/components/InlineText.tsx`
- Test: `depgraph/src/components/InlineText.test.tsx`

**Interfaces:**
- Produces: `export interface InlineTextProps { value: string; onCommit: (next: string) => void; buttonLabel: string; inputLabel: string; testId: string; placeholder?: string; icon?: string; multiline?: boolean; startEditing?: boolean; className?: string }`, default export `InlineText`.
  - Display mode: a `<button aria-label={buttonLabel}>` that shows `value`, or `placeholder` when `value` is empty, plus an `aria-hidden` `icon` (default `✎`).
  - Edit mode: an `<input>` (or a `<textarea rows=6>` when `multiline`) with `aria-label={inputLabel}`, auto-focused. A single-line input selects its text on focus.
  - Enter commits (single-line only), Esc reverts, blur commits. `onCommit` fires at most once per edit, only when the value changed. Single-line values are trimmed and never committed empty.
  - `data-testid={testId}` sits on the wrapper `<span>` in both modes.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/components/InlineText.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import InlineText, { type InlineTextProps } from './InlineText'

afterEach(cleanup)

function setup(overrides: Partial<InlineTextProps> = {}) {
  const onCommit = vi.fn()
  render(<InlineText value="Alpha" onCommit={onCommit} buttonLabel="Rename" inputLabel="Title" testId="hud-title" {...overrides} />)
  return { onCommit }
}

const open = (name = 'Rename') => fireEvent.click(screen.getByRole('button', { name }))
const box = (name = 'Title') => screen.getByRole('textbox', { name }) as HTMLInputElement

describe('InlineText', () => {
  it('shows the value in a button that opens a focused textbox inside the same test id', () => {
    setup()
    expect(screen.getByRole('button', { name: 'Rename' }).textContent).toContain('Alpha')
    open()
    expect(box().value).toBe('Alpha')
    expect(document.activeElement).toBe(box())
    expect(screen.getByTestId('hud-title').contains(box())).toBe(true)
  })

  it('Enter commits the trimmed value once and closes', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: '  Beta ' } })
    fireEvent.keyDown(box(), { key: 'Enter' })
    expect(onCommit.mock.calls).toEqual([['Beta']])
    expect(screen.queryByRole('textbox', { name: 'Title' })).toBeNull()
  })

  it('Esc reverts without committing', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Beta' } })
    fireEvent.keyDown(box(), { key: 'Escape' })
    expect(onCommit).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Rename' }).textContent).toContain('Alpha')
    open()
    expect(box().value).toBe('Alpha')
  })

  it('blur commits', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Gamma' } })
    fireEvent.blur(box())
    expect(onCommit.mock.calls).toEqual([['Gamma']])
  })

  it('does not commit an empty or unchanged single-line value', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: '   ' } })
    fireEvent.keyDown(box(), { key: 'Enter' })
    open()
    fireEvent.keyDown(box(), { key: 'Enter' })
    expect(onCommit).not.toHaveBeenCalled()
  })

  it('startEditing opens the textbox immediately', () => {
    setup({ startEditing: true })
    expect(document.activeElement).toBe(box())
  })

  it('multiline: shows the placeholder, edits in a 6-row textarea, Enter adds a line, blur saves', () => {
    const { onCommit } = setup({ value: '', multiline: true, buttonLabel: 'Edit description', inputLabel: 'Description', placeholder: '▸ description…', testId: 'hud-description' })
    expect(screen.getByRole('button', { name: 'Edit description' }).textContent).toContain('▸ description…')
    open('Edit description')
    const area = box('Description') as unknown as HTMLTextAreaElement
    expect(area.tagName).toBe('TEXTAREA')
    expect(area.rows).toBe(6)
    fireEvent.change(area, { target: { value: 'line one' } })
    fireEvent.keyDown(area, { key: 'Enter' })
    expect(onCommit).not.toHaveBeenCalled()
    fireEvent.blur(area)
    expect(onCommit.mock.calls).toEqual([['line one']])
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/components/InlineText.test.tsx`
Expected: FAIL with `Error: Failed to resolve import "./InlineText" from "src/components/InlineText.test.tsx". Does the file exist?`

- [ ] **Step 3: Write the implementation**

Create `depgraph/src/components/InlineText.tsx`:

```tsx
'use client'
import { useRef, useState, type KeyboardEvent } from 'react'

export interface InlineTextProps {
  value: string
  onCommit: (next: string) => void
  buttonLabel: string
  inputLabel: string
  testId: string
  placeholder?: string
  icon?: string
  multiline?: boolean
  startEditing?: boolean
  className?: string
}

const field = 'w-full rounded-md border border-sky-400/40 bg-black/40 px-2 py-1 outline-none'

export default function InlineText({
  value,
  onCommit,
  buttonLabel,
  inputLabel,
  testId,
  placeholder = '',
  icon = '✎',
  multiline = false,
  startEditing = false,
  className = '',
}: InlineTextProps) {
  const [editing, setEditing] = useState(startEditing)
  const [draft, setDraft] = useState(value)
  // Set once an edit is committed or cancelled, so a blur that follows Enter/Esc cannot commit again.
  const closed = useRef(false)

  const open = () => {
    closed.current = false
    setDraft(value)
    setEditing(true)
  }

  const commit = () => {
    if (closed.current) return
    closed.current = true
    setEditing(false)
    const next = multiline ? draft : draft.trim()
    if (next !== value && (multiline || next !== '')) onCommit(next)
  }

  const cancel = () => {
    closed.current = true
    setEditing(false)
  }

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      cancel()
    } else if (e.key === 'Enter' && !multiline) {
      e.preventDefault()
      commit()
    }
  }

  return (
    <span data-testid={testId} className={className}>
      {editing ? (
        multiline ? (
          <textarea
            aria-label={inputLabel}
            rows={6}
            autoFocus
            className={field}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onBlur={commit}
            onKeyDown={onKeyDown}
          />
        ) : (
          <input
            aria-label={inputLabel}
            autoFocus
            className={field}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onFocus={e => e.currentTarget.select()}
            onBlur={commit}
            onKeyDown={onKeyDown}
          />
        )
      ) : (
        <button type="button" aria-label={buttonLabel} className="max-w-full truncate text-left hover:text-white" onClick={open}>
          {value || <span className="text-white/40">{placeholder}</span>}
          {icon && (
            <span aria-hidden="true" className="ml-1 text-white/30">
              {icon}
            </span>
          )}
        </button>
      )}
    </span>
  )
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/InlineText.test.tsx`
Expected: PASS, `Tests  7 passed (7)`.

- [ ] **Step 5: Commit**

```bash
git add src/components/InlineText.tsx src/components/InlineText.test.tsx
git commit -m "depgraph: InlineText — click to edit, Enter saves, Esc reverts" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.6: Full `NodeHud` card

**Files:**
- Modify: `depgraph/src/components/NodeHud.tsx` (full file below)
- Test: `depgraph/src/components/NodeHud.test.tsx` (full file below)
- Modify: `depgraph/src/app/globals.css` (append slide-in)

**Interfaces:**
- Consumes: `InlineText` (8.5), `StatusPips`, `Keycap` (8.4); `Plan`, `PlanNode` from `@/lib/schema`.
- Produces:
  - `export type NodePatch = Partial<Omit<PlanNode, 'id'>>`
  - `export interface NodeHudProps { plan: Plan; node: PlanNode; armed: boolean; editTitle: boolean; deleteArmed: boolean; onChange: (patch: NodePatch) => void; onToggleLink: () => void; onFocusNode: (id: string) => void; onRemoveDependency: (dependencyId: string) => void; onDelete: () => void; onClose: () => void }`
  - Test ids: `node-hud`, `hud-title`, `status-pip-<s>`, `hud-description`, `tag-<t>`, `add-tag`, `dep-<id>`, `unlock-<id>`, `link-button`, `link-hint`, `delete-node`, `hud-close`.

- [ ] **Step 1: Write the failing tests**

Replace `depgraph/src/components/NodeHud.test.tsx` with:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import NodeHud, { type NodeHudProps } from './NodeHud'
import type { Plan } from '@/lib/schema'

afterEach(cleanup)

const plan: Plan = {
  name: 'P',
  nodes: [
    { id: 'a', title: 'Alpha', description: '', status: 'todo', tags: [], depends_on: [] },
    { id: 'b', title: 'Beta', description: 'Some words', status: 'doing', tags: ['core'], depends_on: ['a'] },
    { id: 'c', title: 'Gamma', description: '', status: 'todo', tags: [], depends_on: ['b'] },
  ],
}
const beta = plan.nodes[1]

function setup(overrides: Partial<NodeHudProps> = {}) {
  const props: NodeHudProps = {
    plan,
    node: beta,
    armed: false,
    editTitle: false,
    deleteArmed: false,
    onChange: vi.fn(),
    onToggleLink: vi.fn(),
    onFocusNode: vi.fn(),
    onRemoveDependency: vi.fn(),
    onDelete: vi.fn(),
    onClose: vi.fn(),
    ...overrides,
  }
  render(<NodeHud {...props} />)
  return props
}

const button = (name: string) => screen.getByRole('button', { name })

describe('NodeHud', () => {
  it('is the "Selected node" region with a Rename button showing the title', () => {
    setup()
    expect(screen.getByRole('region', { name: 'Selected node' })).toBe(screen.getByTestId('node-hud'))
    expect(button('Rename').textContent).toContain('Beta')
    expect(screen.getByTestId('hud-title').contains(button('Rename'))).toBe(true)
  })

  it('renaming commits the new title', () => {
    const props = setup()
    fireEvent.click(button('Rename'))
    const title = screen.getByRole('textbox', { name: 'Title' })
    fireEvent.change(title, { target: { value: 'Beta 2' } })
    fireEvent.keyDown(title, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledWith({ title: 'Beta 2' })
  })

  it('editTitle opens the title textbox focused', () => {
    setup({ editTitle: true })
    expect(document.activeElement).toBe(screen.getByRole('textbox', { name: 'Title' }))
  })

  it('status pips report the clicked status', () => {
    const props = setup()
    expect(screen.getByRole('radiogroup', { name: 'Status' })).toBeTruthy()
    fireEvent.click(screen.getByRole('radio', { name: 'done' }))
    expect(props.onChange).toHaveBeenCalledWith({ status: 'done' })
  })

  it('tag chips remove their tag; + adds a new, non-duplicate tag', () => {
    const props = setup()
    expect(screen.getByTestId('tag-core')).toBe(button('Remove tag core'))
    fireEvent.click(button('Remove tag core'))
    expect(props.onChange).toHaveBeenCalledWith({ tags: [] })
    expect(screen.getByTestId('add-tag').contains(button('Add tag'))).toBe(true)
    fireEvent.click(button('Add tag'))
    const input = screen.getByRole('textbox', { name: 'New tag' })
    fireEvent.change(input, { target: { value: 'api' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledWith({ tags: ['core', 'api'] })
    fireEvent.click(button('Add tag'))
    const again = screen.getByRole('textbox', { name: 'New tag' })
    fireEvent.change(again, { target: { value: 'core' } })
    fireEvent.keyDown(again, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledTimes(2)
  })

  it('description previews in a button and expands into a 6-row textarea that saves on blur', () => {
    const props = setup()
    expect(button('Edit description').textContent).toContain('Some words')
    expect(screen.getByTestId('hud-description').contains(button('Edit description'))).toBe(true)
    fireEvent.click(button('Edit description'))
    const area = screen.getByRole('textbox', { name: 'Description' }) as HTMLTextAreaElement
    expect(area.rows).toBe(6)
    fireEvent.change(area, { target: { value: 'New words' } })
    fireEvent.blur(area)
    expect(props.onChange).toHaveBeenCalledWith({ description: 'New words' })
  })

  it('needs chips select the dependency or remove it', () => {
    const props = setup()
    const chip = screen.getByTestId('dep-a')
    fireEvent.click(within(chip).getByRole('button', { name: 'Alpha' }))
    expect(props.onFocusNode).toHaveBeenCalledWith('a')
    fireEvent.click(within(chip).getByRole('button', { name: 'Remove dependency Alpha' }))
    expect(props.onRemoveDependency).toHaveBeenCalledWith('a')
  })

  it('unlocks chips list dependents and select them', () => {
    const props = setup()
    const chip = screen.getByTestId('unlock-c')
    expect(chip.textContent).toBe('Gamma')
    fireEvent.click(chip)
    expect(props.onFocusNode).toHaveBeenCalledWith('c')
  })

  it('Add dependency toggles and shows a hint while armed', () => {
    const props = setup()
    expect(button('Add dependency').getAttribute('aria-pressed')).toBe('false')
    fireEvent.click(button('Add dependency'))
    expect(props.onToggleLink).toHaveBeenCalledTimes(1)
    cleanup()
    setup({ armed: true })
    expect(screen.getByTestId('link-button').getAttribute('aria-pressed')).toBe('true')
    expect(screen.getByTestId('link-hint').textContent).toBe('Pick what Beta needs')
  })

  it('delete is two-step: "Delete node", then "Confirm delete"', () => {
    const props = setup()
    expect(screen.getByTestId('delete-node')).toBe(button('Delete node'))
    fireEvent.click(button('Delete node'))
    expect(props.onDelete).toHaveBeenCalledTimes(1)
    cleanup()
    setup({ deleteArmed: true })
    expect(screen.getByTestId('delete-node')).toBe(button('Confirm delete'))
  })

  it('Close calls onClose', () => {
    const props = setup()
    fireEvent.click(screen.getByTestId('hud-close'))
    expect(button('Close')).toBe(screen.getByTestId('hud-close'))
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: FAIL. Most tests fail with `TestingLibraryElementError: Unable to find an accessible element with the role "button" and name "Rename"` (or `"Remove tag core"`, `"Edit description"`, `"Delete node"`) or `Unable to find an element by: [data-testid="dep-a"]`. The Close and Add-dependency tests may already pass.

- [ ] **Step 3: Write the implementation**

Replace `depgraph/src/components/NodeHud.tsx` with:

```tsx
'use client'
import InlineText from '@/components/InlineText'
import Keycap from '@/components/Keycap'
import StatusPips from '@/components/StatusPips'
import type { Plan, PlanNode } from '@/lib/schema'

export type NodePatch = Partial<Omit<PlanNode, 'id'>>

export interface NodeHudProps {
  plan: Plan
  node: PlanNode
  armed: boolean
  editTitle: boolean
  deleteArmed: boolean
  onChange: (patch: NodePatch) => void
  onToggleLink: () => void
  onFocusNode: (id: string) => void
  onRemoveDependency: (dependencyId: string) => void
  onDelete: () => void
  onClose: () => void
}

const chip = 'inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs transition-colors hover:bg-white/10'
const btn = 'inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/5 px-2 py-1 text-xs transition-colors hover:bg-white/10'

export default function NodeHud(p: NodeHudProps) {
  const { node, plan } = p
  const titleOf = (id: string) => plan.nodes.find(n => n.id === id)?.title || id
  const unlocks = plan.nodes.filter(n => n.depends_on.includes(node.id))

  return (
    <section
      data-testid="node-hud"
      aria-label="Selected node"
      className="hud-in glass fixed bottom-4 left-1/2 z-10 flex w-[560px] max-w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-2 rounded-xl p-3"
    >
      <div className="flex items-center gap-3">
        <InlineText
          testId="hud-title"
          buttonLabel="Rename"
          inputLabel="Title"
          value={node.title}
          startEditing={p.editTitle}
          onCommit={title => p.onChange({ title })}
          className="min-w-0 flex-1 text-sm font-semibold"
        />
        <StatusPips value={node.status} onChange={status => p.onChange({ status })} />
        <button type="button" data-testid="hud-close" aria-label="Close" className="inline-flex items-center gap-1 text-xs text-white/50 hover:text-white" onClick={p.onClose}>
          ✕ <Keycap>Esc</Keycap>
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        {node.tags.map(t => (
          <button
            key={t}
            type="button"
            data-testid={`tag-${t}`}
            aria-label={`Remove tag ${t}`}
            className={chip}
            onClick={() => p.onChange({ tags: node.tags.filter(x => x !== t) })}
          >
            #{t} <span aria-hidden="true">×</span>
          </button>
        ))}
        <InlineText
          testId="add-tag"
          buttonLabel="Add tag"
          inputLabel="New tag"
          value=""
          placeholder="+"
          icon=""
          onCommit={t => {
            if (!node.tags.includes(t)) p.onChange({ tags: [...node.tags, t] })
          }}
          className="text-xs"
        />
        <span className="ml-2 text-white/50">needs:</span>
        {node.depends_on.map(id => (
          <span key={id} data-testid={`dep-${id}`} className={chip}>
            <button type="button" className="hover:text-white" onClick={() => p.onFocusNode(id)}>
              {titleOf(id)}
            </button>
            <button type="button" aria-label={`Remove dependency ${titleOf(id)}`} className="text-white/50 hover:text-red-300" onClick={() => p.onRemoveDependency(id)}>
              ×
            </button>
          </span>
        ))}
        <button
          type="button"
          data-testid="link-button"
          aria-label="Add dependency"
          aria-pressed={p.armed}
          className={`${chip} ${p.armed ? 'border-sky-400/60 bg-sky-500/20 text-sky-100' : ''}`}
          onClick={p.onToggleLink}
        >
          + <Keycap>L</Keycap>
        </button>
        {unlocks.length > 0 && <span className="ml-2 text-white/50">unlocks:</span>}
        {unlocks.map(n => (
          <button key={n.id} type="button" data-testid={`unlock-${n.id}`} className={`${chip} text-white/70`} onClick={() => p.onFocusNode(n.id)}>
            {n.title || n.id}
          </button>
        ))}
      </div>

      {p.armed && (
        <p role="status" data-testid="link-hint" className="text-xs text-sky-200">
          Pick what {node.title} needs
        </p>
      )}

      <div className="flex items-center gap-2">
        <InlineText
          testId="hud-description"
          buttonLabel="Edit description"
          inputLabel="Description"
          value={node.description}
          placeholder="▸ description…"
          multiline
          onCommit={description => p.onChange({ description })}
          className="min-w-0 flex-1 text-xs text-white/70"
        />
        <button
          type="button"
          data-testid="delete-node"
          aria-label={p.deleteArmed ? 'Confirm delete' : 'Delete node'}
          className={`${btn} ${p.deleteArmed ? 'border-red-400/60 bg-red-950/60 text-red-100' : 'text-red-200/80'}`}
          onClick={p.onDelete}
        >
          {p.deleteArmed ? 'Confirm delete' : 'del'} <Keycap>Del</Keycap>
        </button>
      </div>
    </section>
  )
}
```

Append to `depgraph/src/app/globals.css`:

```css
@keyframes dg-hud-in {
  from { transform: translateY(12px); opacity: 0; }
  to { transform: none; opacity: 1; }
}
.hud-in { animation: dg-hud-in 120ms ease-out; }
@media (prefers-reduced-motion: reduce) {
  .hud-in { animation: none; }
}
```

(Tailwind v4's `-translate-x-1/2` uses the CSS `translate` property, so animating `transform` does not fight the centering.)

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: PASS, `Tests  11 passed (11)`. (`page.tsx` does not type-check against the new props until Task 8.7, so do not run tsc yet.)

- [ ] **Step 5: Commit**

```bash
git add src/components/NodeHud.tsx src/components/NodeHud.test.tsx src/app/globals.css
git commit -m "depgraph: full HUD card — rename, pips, tags, description, needs/unlocks chips, two-step delete" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 8.7: Page uses the HUD, camera flies to chips, `NodePanel` removed (e2e); full check

**Files:**
- Modify: `depgraph/e2e/smoke.spec.ts` (full file below)
- Modify: `depgraph/src/app/page.tsx` (full file below)
- Modify: `depgraph/src/components/Graph.tsx` (add `flyTo`)
- Delete: `depgraph/src/components/NodePanel.tsx`

**Interfaces:**
- Consumes: `NodeHudProps` (8.6), `useConfirm` (8.3), `cameraFor` (8.2), `NodeSignal`, `nextSignal`, `focusNode` (8.1).
- Produces: `Graph` props gain `flyTo: NodeSignal | null`. The page keeps `editTitleFor: string | null`, so a node created from **+ Node** opens with its title in edit mode.

- [ ] **Step 1: Write the failing e2e tests**

Replace `depgraph/e2e/smoke.spec.ts` with:

```ts
import { expect, test, type Page } from '@playwright/test'
import { copyFile, mkdir, readFile } from 'node:fs/promises'

const label = (page: Page, id: string) => page.locator(`[data-testid="node-label"][data-node-id="${id}"]`)
const planText = () => readFile('e2e/plans/example.json', 'utf8')

test.beforeEach(async () => {
  await mkdir('e2e/plans', { recursive: true })
  await copyFile('plans/example.json', 'e2e/plans/example.json')
})

test('add a node: count increments, file gains the node, survives reload', async ({ page }) => {
  await page.goto('/?plan=example')
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"id": "untitled"')
  await page.reload()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
})

test('edit the new node in the HUD, link it by clicking a label, then delete it', async ({ page }) => {
  await page.goto('/?plan=example')
  await page.getByRole('button', { name: 'Add node', exact: true }).click()
  const hud = page.getByTestId('node-hud')
  await expect(hud).toBeVisible()
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('Smoke node')
  await title.press('Enter')
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Smoke node')
  await page.getByRole('radio', { name: 'doing', exact: true }).click()
  await expect(page.getByTestId('status-pip-doing')).toHaveAttribute('aria-checked', 'true')
  await page.getByRole('button', { name: 'Add dependency', exact: true }).click()
  await label(page, 'schema').click()
  await expect(page.getByTestId('dep-schema')).toBeVisible()
  await expect.poll(planText).toMatch(/"id": "untitled"[\s\S]*?"depends_on": \[\s*"schema"\s*\]/)
  const text = await planText()
  expect(text).toContain('"title": "Smoke node"')
  expect(text).toMatch(/"id": "untitled"[\s\S]*?"status": "doing"/)
  const del = page.getByTestId('delete-node')
  await expect(del).toHaveAccessibleName('Delete node')
  await del.click()
  await expect(del).toHaveAccessibleName('Confirm delete')
  await del.click()
  await expect(hud).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})

test('Add dependency arms, Esc disarms', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'api-routes').click()
  const hud = page.getByTestId('node-hud')
  const arm = page.getByRole('button', { name: 'Add dependency', exact: true })
  await expect(hud).toBeVisible()
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await arm.click()
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('link-hint')).toHaveText('Pick what Write API routes needs')
  await page.keyboard.press('Escape')
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await expect(page.getByTestId('link-hint')).toBeHidden()
  await expect(hud).toBeVisible()
  await page.keyboard.press('l')
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await page.keyboard.press('Escape')
  await page.keyboard.press('Escape')
  await expect(hud).toBeHidden()
})

test('cycle is refused with an error', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await page.getByRole('button', { name: 'Add dependency', exact: true }).click()
  await label(page, 'api-routes').click()
  await expect(page.getByTestId('toast')).toContainText('cycle:')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toMatch(/"id": "schema"[\s\S]*?"depends_on": \[\s*"design-spec"\s*\]/)
  const res = await page.request.put('/api/plans/example', {
    data: {
      name: 'x',
      nodes: [
        { id: 'a', title: 'A', depends_on: ['b'] },
        { id: 'b', title: 'B', depends_on: ['a'] },
      ],
    },
  })
  expect(res.status()).toBe(400)
  expect((await res.json()).errors[0]).toMatch(/^cycle:/)
})

test('all 8 labels are visible on load', async ({ page }) => {
  await page.goto('/?plan=example')
  const labels = page.getByTestId('node-label')
  await expect(labels).toHaveCount(8)
  for (const l of await labels.all()) await expect(l).toBeVisible()
  await expect(page.getByRole('button', { name: 'Schema + validator', exact: true })).toHaveAttribute('data-node-id', 'schema')
  await expect(label(page, 'node-panel')).toHaveAttribute('data-status', 'blocked')
})

test('clicking a label selects the node; a needs chip jumps to the dependency', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await expect(page.getByRole('region', { name: 'Selected node' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Schema + validator')
  await expect(label(page, 'schema')).toHaveAttribute('data-selected', 'true')
  await expect(label(page, 'store')).toHaveAttribute('data-dim', 'false')
  await expect(label(page, 'watcher')).toHaveAttribute('data-dim', 'true')
  await page.getByTestId('dep-design-spec').getByRole('button', { name: 'Approve design spec', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Approve design spec')
  await expect(label(page, 'design-spec')).toHaveAttribute('data-selected', 'true')
})
```

- [ ] **Step 2: Run e2e and watch them fail**

Run: `npm run test:e2e`
Expected: `2 failed`, `4 passed`.
- `edit the new node in the HUD, …`: `expect(locator).toContainText(expected)` times out on `getByRole('button', { name: 'Rename', exact: true })` (element(s) not found). The `Title` textbox still exists in `NodePanel`, so the test gets that far.
- `clicking a label selects the node; a needs chip …`: same failure on `getByRole('button', { name: 'Rename', exact: true })`.

- [ ] **Step 3: Add `flyTo` to `Graph.tsx`** (no unit test possible (WebGL); camera math is unit-tested in `camera.test.ts`; selection side covered by e2e "clicking a label selects the node; a needs chip jumps to the dependency")

In `depgraph/src/components/Graph.tsx`:

Replace

```tsx
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
```

with

```tsx
import { cameraFor } from '@/lib/camera'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
```

Replace

```tsx
import { pulseBlocked, type Pulsable } from '@/lib/pulse'
```

with

```tsx
import { pulseBlocked, type Pulsable } from '@/lib/pulse'
import type { NodeSignal } from '@/lib/selection'
```

Replace

```tsx
  arming: boolean
  onSelect: (id: string | null) => void
```

with

```tsx
  arming: boolean
  flyTo: NodeSignal | null
  onSelect: (id: string | null) => void
```

Replace

```tsx
export default function Graph({ plan, selectedId, arming, onSelect, onLinkRightClick }: GraphProps) {
```

with

```tsx
export default function Graph({ plan, selectedId, arming, flyTo, onSelect, onLinkRightClick }: GraphProps) {
```

Insert directly after the `syncLabels` effect (the `useEffect` whose deps are `[labels, plan, selectedId, neighbors, onPick]`):

```tsx
  useEffect(() => {
    const fg = fgRef.current
    const node = flyTo ? cache.get(flyTo.id) : undefined
    if (!fg || !node) return
    const { position, lookAt } = cameraFor(node)
    fg.cameraPosition(position, lookAt, 800)
  }, [flyTo, cache])
```

- [ ] **Step 4: Rewrite the page**

Replace `depgraph/src/app/page.tsx` with:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useConfirm } from '@/hooks/useConfirm'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan } from '@/lib/schema'
import {
  initialSelection,
  nextSignal,
  selectionStep,
  type NodeSignal,
  type SelectionEvent,
  type SelectionState,
} from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
  const [editTitleFor, setEditTitleFor] = useState<string | null>(null)
  const [fly, setFly] = useState<NodeSignal | null>(null)
  const toast = useToast()
  const confirmDelete = useConfirm(3000)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (state.selectedId !== activeId) setEditTitleFor(null)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') report(apply(p => addDependency(p, effect.dependencyId, effect.dependentId)))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  const focusNode = (id: string) => {
    dispatch({ type: 'focusNode', id })
    setFly(f => nextSignal(f, id))
  }

  const addAndEdit = (make: (p: Plan) => { plan: Plan; id: string }) => {
    let newId = ''
    const errors = apply(p => {
      const r = make(p)
      newId = r.id
      return r.plan
    })
    report(errors)
    if (errors.length || !newId) return
    setSelection({ selectedId: newId, arming: false })
    setEditTitleFor(newId)
  }

  const handleAddNode = () => addAndEdit(p => addNode(p))

  const handleDelete = () => {
    if (!activeId) return
    const id = activeId
    confirmDelete.press(id, () => {
      report(apply(p => deleteNode(p, id)))
      dispatch({ type: 'clear' })
    })
  }

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
  })

  const handleNewPlan = async () => {
    const name = window.prompt('Plan name')
    if (!name) return
    const res = await fetch('/api/plans', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const body = await res.json()
    if (!res.ok) {
      toast.show((body.errors as string[]).join('; '))
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={activeId}
        arming={armed}
        flyTo={fly}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {activeNode && (
        <NodeHud
          key={activeNode.id}
          plan={plan}
          node={activeNode}
          armed={armed}
          editTitle={editTitleFor === activeNode.id}
          deleteArmed={confirmDelete.isArmed(activeNode.id)}
          onChange={patch => report(apply(p => updateNode(p, activeNode.id, patch)))}
          onToggleLink={toggleLink}
          onFocusNode={focusNode}
          onRemoveDependency={dep => report(apply(p => removeDependency(p, dep, activeNode.id)))}
          onDelete={handleDelete}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      <Toast message={toast.message} />
      <SaveIndicator state={saveState} error={saveError} />
    </>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center font-mono text-sm text-white/50">{text}</div>
}

export default function Page() {
  return (
    <Suspense>
      <Workspace />
    </Suspense>
  )
}
```

- [ ] **Step 5: Delete the side panel**

```bash
git rm src/components/NodePanel.tsx
```

- [ ] **Step 6: Run e2e and watch it pass**

Run: `npm run test:e2e`
Expected: `6 passed`.

- [ ] **Step 7: Full check**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: Vitest `Test Files  18 passed (18)`, 0 failed; tsc and eslint print nothing; Playwright `6 passed`.

- [ ] **Step 8: Commit**

```bash
git add e2e/smoke.spec.ts src/app/page.tsx src/components/Graph.tsx
git commit -m "depgraph: HUD card replaces NodePanel; chips fly the camera; two-step delete" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

# Slice 9 — Hotkeys 1–4, N, Shift+N, Del, F; Add next step; empty state

Outcome: **1–4** set status, **N** adds a node with its title open for editing, **Shift+N** / `add-next` adds a node that depends on the selection, **Del** arms delete and a second **Del** confirms, **F** flies to the selection. An empty plan shows "Press N or click + Node to place your first step." Keycap hints appear on the toolbar.

### Task 9.1: `addNextNode` mutation

**Files:**
- Modify: `depgraph/src/lib/mutations.ts`
- Test: `depgraph/src/lib/mutations.test.ts`

**Interfaces:**
- Consumes: `addNode`, `addDependency` (same file).
- Produces: `export function addNextNode(plan: Plan, fromId: string, title?: string): { plan: Plan; id: string }`. The default title is `'Untitled'`, and the new node's `depends_on` is `[fromId]`.

- [ ] **Step 1: Write the failing test**

In `depgraph/src/lib/mutations.test.ts`, add `addNextNode` to the existing import from `'./mutations'` (keep the other names), then append:

```ts
describe('addNextNode', () => {
  it('adds an Untitled node that depends on the given node', () => {
    const base = {
      name: 'P',
      nodes: [{ id: 'a', title: 'A', description: '', status: 'todo' as const, tags: [], depends_on: [] }],
    }
    const { plan, id } = addNextNode(base, 'a')
    expect(id).toBe('untitled')
    expect(plan.nodes).toHaveLength(2)
    expect(plan.nodes.find(n => n.id === id)).toEqual({
      id: 'untitled',
      title: 'Untitled',
      description: '',
      status: 'todo',
      tags: [],
      depends_on: ['a'],
    })
    expect(base.nodes).toHaveLength(1)
  })
})
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npx vitest run src/lib/mutations.test.ts`
Expected: FAIL, 1 failed: `TypeError: (0 , __vi_import_0__.addNextNode) is not a function`.

- [ ] **Step 3: Write the implementation**

Append to `depgraph/src/lib/mutations.ts`:

```ts
export function addNextNode(plan: Plan, fromId: string, title = 'Untitled'): { plan: Plan; id: string } {
  const added = addNode(plan, title)
  return { plan: addDependency(added.plan, fromId, added.id), id: added.id }
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `npx vitest run src/lib/mutations.test.ts`
Expected: PASS, 0 failed.

- [ ] **Step 5: Commit**

```bash
git add src/lib/mutations.ts src/lib/mutations.test.ts
git commit -m "depgraph: addNextNode mutation" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 9.2: HUD `add-next` button

**Files:**
- Modify: `depgraph/src/components/NodeHud.tsx`
- Test: `depgraph/src/components/NodeHud.test.tsx`

**Interfaces:**
- Produces: `NodeHudProps` gains `onAddNext: () => void`. The button has test id `add-next` and name "Add next step", with a `⇧N` keycap.

- [ ] **Step 1: Write the failing test**

In `depgraph/src/components/NodeHud.test.tsx`, inside `setup`, replace

```tsx
    onDelete: vi.fn(),
```

with

```tsx
    onDelete: vi.fn(),
    onAddNext: vi.fn(),
```

and append inside `describe('NodeHud', …)`:

```tsx
  it('Add next step calls onAddNext', () => {
    const props = setup()
    expect(screen.getByTestId('add-next')).toBe(button('Add next step'))
    fireEvent.click(button('Add next step'))
    expect(props.onAddNext).toHaveBeenCalledTimes(1)
  })
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: FAIL, 1 failed: `TestingLibraryElementError: Unable to find an element by: [data-testid="add-next"]`.

- [ ] **Step 3: Write the implementation**

In `depgraph/src/components/NodeHud.tsx`:

Replace

```tsx
  onDelete: () => void
  onClose: () => void
}
```

with

```tsx
  onDelete: () => void
  onAddNext: () => void
  onClose: () => void
}
```

Insert immediately before the `<button` that has `data-testid="delete-node"`:

```tsx
        <button type="button" data-testid="add-next" aria-label="Add next step" className={btn} onClick={p.onAddNext}>
          +next <Keycap>⇧N</Keycap>
        </button>
```

- [ ] **Step 4: Run it and watch it pass**

Run: `npx vitest run src/components/NodeHud.test.tsx`
Expected: PASS, `Tests  12 passed (12)`.

- [ ] **Step 5: Commit**

```bash
git add src/components/NodeHud.tsx src/components/NodeHud.test.tsx
git commit -m "depgraph: HUD Add next step button" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 9.3: Page hotkeys, add-next, empty state, toolbar keycap (e2e); full check

**Files:**
- Modify: `depgraph/e2e/smoke.spec.ts` (imports + two new tests)
- Modify: `depgraph/src/app/page.tsx` (full file below)
- Modify: `depgraph/src/components/Toolbar.tsx` (keycap)

**Interfaces:**
- Consumes: `addNextNode` (9.1), `NodeHudProps.onAddNext` (9.2), `useHotkeys` names `n`, `shift+n`, `1`–`4`, `delete`, `f`, `l`, `escape`.
- Produces: `data-testid="empty-hint"` with the exact text `Press N or click + Node to place your first step.`

- [ ] **Step 1: Write the failing e2e tests**

In `depgraph/e2e/smoke.spec.ts`, replace

```ts
import { copyFile, mkdir, readFile } from 'node:fs/promises'
```

with

```ts
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'
```

and append:

```ts
test('hotkeys 1–4 and N work', async ({ page }) => {
  await writeFile('e2e/plans/empty.json', JSON.stringify({ name: 'Empty', nodes: [] }, null, 2) + '\n')
  await page.goto('/?plan=empty')
  await expect(page.getByTestId('empty-hint')).toHaveText('Press N or click + Node to place your first step.')
  await page.keyboard.press('n')
  await expect(page.getByTestId('node-count')).toHaveText('1 nodes')
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('First step')
  await title.press('Enter')
  await expect(page.getByTestId('empty-hint')).toBeHidden()
  for (const [key, status] of [['2', 'doing'], ['3', 'done'], ['4', 'blocked'], ['1', 'todo'], ['4', 'blocked']] as const) {
    await page.keyboard.press(key)
    await expect(page.getByTestId(`status-pip-${status}`)).toHaveAttribute('aria-checked', 'true')
  }
  await expect.poll(() => readFile('e2e/plans/empty.json', 'utf8')).toContain('"status": "blocked"')
  expect(await readFile('e2e/plans/empty.json', 'utf8')).toContain('"title": "First step"')
})

test('Shift+N adds a next step; Del twice deletes it', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'watcher').click()
  await page.keyboard.press('Shift+N')
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('After watcher')
  await title.press('Enter')
  await expect(page.getByTestId('dep-watcher')).toBeVisible()
  await expect.poll(planText).toMatch(/"id": "untitled"[\s\S]*?"depends_on": \[\s*"watcher"\s*\]/)
  await page.keyboard.press('Delete')
  await expect(page.getByTestId('delete-node')).toHaveAccessibleName('Confirm delete')
  await page.keyboard.press('Delete')
  await expect(page.getByTestId('node-hud')).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})
```

- [ ] **Step 2: Run e2e and watch them fail**

Run: `npm run test:e2e`
Expected: `2 failed`, `6 passed`.
- `hotkeys 1–4 and N work`: `expect(locator).toHaveText(expected)` fails on `getByTestId('empty-hint')` (element(s) not found).
- `Shift+N adds a next step; Del twice deletes it`: `expect(locator).toHaveText(expected)` on `getByTestId('node-count')`, `Expected string: "9 nodes"`, `Received string: "8 nodes"`.

- [ ] **Step 3: Add the toolbar keycap**

In `depgraph/src/components/Toolbar.tsx`, add below the `useRouter` import:

```tsx
import Keycap from '@/components/Keycap'
```

and replace

```tsx
        + Node
```

with

```tsx
        + Node <Keycap>N</Keycap>
```

- [ ] **Step 4: Rewrite the page**

Replace `depgraph/src/app/page.tsx` with:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useConfirm } from '@/hooks/useConfirm'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNextNode, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan, Status } from '@/lib/schema'
import {
  initialSelection,
  nextSignal,
  selectionStep,
  type NodeSignal,
  type SelectionEvent,
  type SelectionState,
} from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
  const [editTitleFor, setEditTitleFor] = useState<string | null>(null)
  const [fly, setFly] = useState<NodeSignal | null>(null)
  const toast = useToast()
  const confirmDelete = useConfirm(3000)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (state.selectedId !== activeId) setEditTitleFor(null)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') report(apply(p => addDependency(p, effect.dependencyId, effect.dependentId)))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  const flyTo = (id: string) => setFly(f => nextSignal(f, id))

  const focusNode = (id: string) => {
    dispatch({ type: 'focusNode', id })
    flyTo(id)
  }

  const addAndEdit = (make: (p: Plan) => { plan: Plan; id: string }) => {
    let newId = ''
    const errors = apply(p => {
      const r = make(p)
      newId = r.id
      return r.plan
    })
    report(errors)
    if (errors.length || !newId) return
    setSelection({ selectedId: newId, arming: false })
    setEditTitleFor(newId)
  }

  const handleAddNode = () => addAndEdit(p => addNode(p))

  const handleAddNext = () => {
    if (!activeId) {
      toast.show('select a node first')
      return
    }
    const from = activeId
    addAndEdit(p => addNextNode(p, from))
  }

  const setStatus = (status: Status) => {
    if (activeId) report(apply(p => updateNode(p, activeId, { status })))
  }

  const handleDelete = () => {
    if (!activeId) return
    const id = activeId
    confirmDelete.press(id, () => {
      report(apply(p => deleteNode(p, id)))
      dispatch({ type: 'clear' })
    })
  }

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
    n: handleAddNode,
    'shift+n': handleAddNext,
    '1': () => setStatus('todo'),
    '2': () => setStatus('doing'),
    '3': () => setStatus('done'),
    '4': () => setStatus('blocked'),
    delete: handleDelete,
    f: () => {
      if (activeId) flyTo(activeId)
    },
  })

  const handleNewPlan = async () => {
    const name = window.prompt('Plan name')
    if (!name) return
    const res = await fetch('/api/plans', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const body = await res.json()
    if (!res.ok) {
      toast.show((body.errors as string[]).join('; '))
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={activeId}
        arming={armed}
        flyTo={fly}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {plan.nodes.length === 0 && (
        <p data-testid="empty-hint" className="pointer-events-none fixed inset-x-0 top-1/2 -translate-y-1/2 text-center text-sm text-white/60">
          Press N or click + Node to place your first step.
        </p>
      )}
      {activeNode && (
        <NodeHud
          key={activeNode.id}
          plan={plan}
          node={activeNode}
          armed={armed}
          editTitle={editTitleFor === activeNode.id}
          deleteArmed={confirmDelete.isArmed(activeNode.id)}
          onChange={patch => report(apply(p => updateNode(p, activeNode.id, patch)))}
          onToggleLink={toggleLink}
          onFocusNode={focusNode}
          onRemoveDependency={dep => report(apply(p => removeDependency(p, dep, activeNode.id)))}
          onDelete={handleDelete}
          onAddNext={handleAddNext}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      <Toast message={toast.message} />
      <SaveIndicator state={saveState} error={saveError} />
    </>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center font-mono text-sm text-white/50">{text}</div>
}

export default function Page() {
  return (
    <Suspense>
      <Workspace />
    </Suspense>
  )
}
```

(**F** only moves the camera. That is WebGL, so no unit test is possible; `cameraFor` is unit-tested and the page wiring is the one line above. It is checked by hand in Slice 10's Task 10.4 Step 5.)

- [ ] **Step 5: Run e2e and watch it pass**

Run: `npm run test:e2e`
Expected: `8 passed`.

- [ ] **Step 6: Full check**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: Vitest `Test Files  18 passed (18)`, 0 failed; tsc and eslint print nothing; Playwright `8 passed`.

- [ ] **Step 7: Commit**

```bash
git add e2e/smoke.spec.ts src/app/page.tsx src/components/Toolbar.tsx
git commit -m "depgraph: hotkeys 1–4, N, Shift+N, Del, F; Add next step; empty-plan hint" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

# Slice 10 — Feedback and motion; README

Outcome: errors from `apply` show a red toast and shake the target node's label; info toasts stay amber. Setting a node to done fires one ring burst, which is skipped under `prefers-reduced-motion`. The README documents the new controls.

### Task 10.1: Toast tone

**Files:**
- Modify: `depgraph/src/components/Toast.tsx` (full file below)
- Test: `depgraph/src/components/Toast.test.tsx`

**Interfaces:**
- Produces:
  - `export type ToastTone = 'info' | 'error'`
  - `useToast(): { message: string | null; tone: ToastTone; show: (message: string, tone?: ToastTone) => void }`, where `tone` defaults to `'info'` and messages clear after 3500 ms.
  - `Toast({ message, tone }: { message: string | null; tone?: ToastTone })` renders `role="status"`, `data-testid="toast"` and `data-tone`, positioned top center so it never covers the HUD.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/components/Toast.test.tsx`:

```tsx
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, render, renderHook, screen } from '@testing-library/react'
import Toast, { useToast } from './Toast'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('Toast', () => {
  it('renders nothing without a message', () => {
    render(<Toast message={null} />)
    expect(screen.queryByTestId('toast')).toBeNull()
  })

  it('exposes its tone, info by default', () => {
    render(<Toast message="hello" />)
    expect(screen.getByTestId('toast').getAttribute('data-tone')).toBe('info')
    cleanup()
    render(<Toast message="cycle: a -> b -> a" tone="error" />)
    const toast = screen.getByRole('status')
    expect(toast.getAttribute('data-tone')).toBe('error')
    expect(toast.textContent).toBe('cycle: a -> b -> a')
  })
})

describe('useToast', () => {
  it('shows info by default, error on request, and clears after 3.5 s', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useToast())
    act(() => result.current.show('hi'))
    expect(result.current).toMatchObject({ message: 'hi', tone: 'info' })
    act(() => result.current.show('bad', 'error'))
    expect(result.current).toMatchObject({ message: 'bad', tone: 'error' })
    act(() => {
      vi.advanceTimersByTime(3500)
    })
    expect(result.current.message).toBeNull()
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/components/Toast.test.tsx`
Expected: FAIL, 2 failed / 1 passed: `exposes its tone …` → `expected null to be 'info'`; `useToast …` → `expected { message: 'hi', show: [Function] } to match object { message: 'hi', tone: 'info' }`.

- [ ] **Step 3: Write the implementation**

Replace `depgraph/src/components/Toast.tsx` with:

```tsx
'use client'
import { useCallback, useRef, useState } from 'react'

export type ToastTone = 'info' | 'error'

export function useToast() {
  const [state, setState] = useState<{ message: string | null; tone: ToastTone }>({ message: null, tone: 'info' })
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const show = useCallback((message: string, tone: ToastTone = 'info') => {
    setState({ message, tone })
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setState(s => ({ ...s, message: null })), 3500)
  }, [])
  return { message: state.message, tone: state.tone, show }
}

export default function Toast({ message, tone = 'info' }: { message: string | null; tone?: ToastTone }) {
  if (!message) return null
  const colors = tone === 'error' ? 'border-red-400/50 text-red-100' : 'border-amber-400/40 text-amber-100'
  return (
    <div
      role="status"
      data-testid="toast"
      data-tone={tone}
      className={`fixed left-1/2 top-4 z-20 -translate-x-1/2 glass rounded-lg px-4 py-2 text-xs ${colors}`}
    >
      {message}
    </div>
  )
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/components/Toast.test.tsx`
Expected: PASS, `Tests  3 passed (3)`.

- [ ] **Step 5: Commit**

```bash
git add src/components/Toast.tsx src/components/Toast.test.tsx
git commit -m "depgraph: toast tone (info amber, error red), top-center" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 10.2: `shakeLabel`

**Files:**
- Modify: `depgraph/src/lib/nodeLabel.ts`
- Test: `depgraph/src/lib/nodeLabel.test.ts`

**Interfaces:**
- Produces: `export const SHAKE_MS = 600`; `export function shakeLabel(el: HTMLElement, ms?: number): void`. It sets `data-shake="true"` for `ms` milliseconds and restarts the timer (and the CSS animation) when called again.

- [ ] **Step 1: Write the failing test**

In `depgraph/src/lib/nodeLabel.test.ts`, replace the two import lines with:

```ts
import { describe, expect, it, vi } from 'vitest'
import { LABEL_MAX, SHAKE_MS, createLabelElement, labelFor, renderLabel, shakeLabel, syncLabels, truncateTitle } from './nodeLabel'
```

and append:

```ts
describe('shakeLabel', () => {
  it('sets data-shake for 600 ms and restarts when repeated', () => {
    vi.useFakeTimers()
    try {
      expect(SHAKE_MS).toBe(600)
      const el = createLabelElement('a', () => {})
      shakeLabel(el)
      expect(el.dataset.shake).toBe('true')
      vi.advanceTimersByTime(400)
      shakeLabel(el)
      vi.advanceTimersByTime(400)
      expect(el.dataset.shake).toBe('true')
      vi.advanceTimersByTime(200)
      expect(el.dataset.shake).toBeUndefined()
    } finally {
      vi.useRealTimers()
    }
  })
})
```

- [ ] **Step 2: Run it and watch it fail**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: FAIL, 1 failed / 11 passed: `expected undefined to be 600`.

- [ ] **Step 3: Write the implementation**

Append to `depgraph/src/lib/nodeLabel.ts`:

```ts
export const SHAKE_MS = 600

const shakeTimers = new WeakMap<HTMLElement, ReturnType<typeof setTimeout>>()

export function shakeLabel(el: HTMLElement, ms = SHAKE_MS): void {
  clearTimeout(shakeTimers.get(el))
  delete el.dataset.shake
  el.getBoundingClientRect() // force a reflow so the CSS animation restarts
  el.dataset.shake = 'true'
  shakeTimers.set(
    el,
    setTimeout(() => {
      delete el.dataset.shake
      shakeTimers.delete(el)
    }, ms),
  )
}
```

- [ ] **Step 4: Run it and watch it pass**

Run: `npx vitest run src/lib/nodeLabel.test.ts`
Expected: PASS, `Tests  12 passed (12)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/nodeLabel.ts src/lib/nodeLabel.test.ts
git commit -m "depgraph: shakeLabel for error feedback" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 10.3: Motion helpers `takeNewlyDone`, `burstFrame`, `prefersReducedMotion`

**Files:**
- Create: `depgraph/src/lib/effects.ts`
- Test: `depgraph/src/lib/effects.test.ts`

**Interfaces:**
- Produces:
  - `export function takeNewlyDone(seen: Map<string, Status>, nodes: ReadonlyArray<Pick<PlanNode, 'id' | 'status'>>): string[]` returns the ids that were already seen with a status other than `done` and are now `done`. It then replaces `seen` with the current statuses. Nodes seen for the first time never burst.
  - `export const BURST_MS = 700`
  - `export function burstFrame(elapsedMs: number, ms?: number): { scale: number; opacity: number; done: boolean }`: `scale` runs 1→4, `opacity` 0.9→0, clamped.
  - `export function prefersReducedMotion(): boolean`, false when `matchMedia` is missing.

- [ ] **Step 1: Write the failing tests**

Create `depgraph/src/lib/effects.test.ts`:

```ts
// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { BURST_MS, burstFrame, prefersReducedMotion, takeNewlyDone } from './effects'
import type { Status } from './schema'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('takeNewlyDone', () => {
  it('reports nodes that just turned done, ignores first sightings, and remembers statuses', () => {
    const seen = new Map<string, Status>()
    expect(takeNewlyDone(seen, [{ id: 'a', status: 'todo' }, { id: 'b', status: 'done' }])).toEqual([])
    expect(
      takeNewlyDone(seen, [
        { id: 'a', status: 'done' },
        { id: 'b', status: 'done' },
        { id: 'c', status: 'done' },
      ]),
    ).toEqual(['a'])
    expect(takeNewlyDone(seen, [{ id: 'a', status: 'done' }])).toEqual([])
    expect([...seen.entries()]).toEqual([['a', 'done']])
  })
})

describe('burstFrame', () => {
  it('grows and fades over BURST_MS, then reports done', () => {
    expect(BURST_MS).toBe(700)
    expect(burstFrame(0)).toEqual({ scale: 1, opacity: 0.9, done: false })
    const mid = burstFrame(350)
    expect(mid.scale).toBeCloseTo(2.5)
    expect(mid.opacity).toBeCloseTo(0.45)
    expect(mid.done).toBe(false)
    expect(burstFrame(700)).toEqual({ scale: 4, opacity: 0, done: true })
    expect(burstFrame(900)).toEqual({ scale: 4, opacity: 0, done: true })
    expect(burstFrame(-5)).toEqual({ scale: 1, opacity: 0.9, done: false })
  })
})

describe('prefersReducedMotion', () => {
  it('reads the media query and defaults to false without matchMedia', () => {
    expect(prefersReducedMotion()).toBe(false)
    vi.stubGlobal('matchMedia', (q: string) => ({ matches: q === '(prefers-reduced-motion: reduce)' }))
    expect(prefersReducedMotion()).toBe(true)
    vi.stubGlobal('matchMedia', () => ({ matches: false }))
    expect(prefersReducedMotion()).toBe(false)
  })
})
```

- [ ] **Step 2: Run them and watch them fail**

Run: `npx vitest run src/lib/effects.test.ts`
Expected: FAIL with `Error: Failed to resolve import "./effects" from "src/lib/effects.test.ts". Does the file exist?`

- [ ] **Step 3: Write the implementation**

Create `depgraph/src/lib/effects.ts`:

```ts
import type { PlanNode, Status } from '@/lib/schema'

export function takeNewlyDone(seen: Map<string, Status>, nodes: ReadonlyArray<Pick<PlanNode, 'id' | 'status'>>): string[] {
  const ids = nodes.filter(n => n.status === 'done' && seen.has(n.id) && seen.get(n.id) !== 'done').map(n => n.id)
  seen.clear()
  for (const n of nodes) seen.set(n.id, n.status)
  return ids
}

export const BURST_MS = 700

export function burstFrame(elapsedMs: number, ms = BURST_MS): { scale: number; opacity: number; done: boolean } {
  const t = Math.min(Math.max(elapsedMs / ms, 0), 1)
  return { scale: 1 + 3 * t, opacity: 0.9 * (1 - t), done: t >= 1 }
}

export function prefersReducedMotion(): boolean {
  return typeof window !== 'undefined' && typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches
}
```

- [ ] **Step 4: Run them and watch them pass**

Run: `npx vitest run src/lib/effects.test.ts`
Expected: PASS, `Tests  3 passed (3)`.

- [ ] **Step 5: Commit**

```bash
git add src/lib/effects.ts src/lib/effects.test.ts
git commit -m "depgraph: motion helpers — newly-done detection, burst frames, reduced-motion check" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

### Task 10.4: Error toasts + shake, done burst, README (e2e); full check

**Files:**
- Modify: `depgraph/e2e/smoke.spec.ts` (one assertion in the cycle test)
- Modify: `depgraph/src/app/page.tsx` (full file below)
- Modify: `depgraph/src/components/Graph.tsx` (full file below)
- Modify: `depgraph/src/app/globals.css` (append)
- Modify: `depgraph/README.md` (controls section)

**Interfaces:**
- Consumes: `useToast().show(message, tone)` (10.1), `shakeLabel` (10.2), `takeNewlyDone`, `burstFrame`, `prefersReducedMotion` (10.3), `nextSignal` (8.1).
- Produces: final `Graph` props `{ plan: Plan; selectedId: string | null; arming: boolean; flyTo: NodeSignal | null; shake: NodeSignal | null; onSelect: (id: string | null) => void; onLinkRightClick: (dependencyId: string, dependentId: string) => void }`. The page's `attempt(targetId: string | null, mutate: (p: Plan) => Plan): boolean` replaces `report(apply(...))`.

- [ ] **Step 1: Write the failing e2e assertion**

In `depgraph/e2e/smoke.spec.ts`, inside `test('cycle is refused with an error', …)`, replace

```ts
  await expect(page.getByTestId('toast')).toContainText('cycle:')
```

with

```ts
  await expect(page.getByTestId('toast')).toContainText('cycle:')
  await expect(page.getByTestId('toast')).toHaveAttribute('data-tone', 'error')
```

- [ ] **Step 2: Run e2e and watch it fail**

Run: `npm run test:e2e`
Expected: `1 failed`, `7 passed`. `cycle is refused with an error`: `expect(locator).toHaveAttribute(expected)` on `getByTestId('toast')`, `Expected string: "error"`, `Received string: "info"`.

- [ ] **Step 3: Rewrite `Graph.tsx` with shake and done burst** (no unit test possible (WebGL); pure parts are covered by `nodeLabel.test.ts` and `effects.test.ts`, integration by e2e "cycle is refused with an error" and "hotkeys 1–4 and N work", which sets done)

Replace `depgraph/src/components/Graph.tsx` with:

```tsx
'use client'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import ForceGraph3D, { type ForceGraphMethods } from 'react-force-graph-3d'
import { cameraFor } from '@/lib/camera'
import { burstFrame, prefersReducedMotion, takeNewlyDone } from '@/lib/effects'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
import { labelFor, shakeLabel, syncLabels } from '@/lib/nodeLabel'
import type { Plan, Status } from '@/lib/schema'
import { pulseBlocked, type Pulsable } from '@/lib/pulse'
import type { NodeSignal } from '@/lib/selection'

export const STATUS_COLORS: Record<Status, string> = {
  todo: '#8b95a7',
  doing: '#5ac8fa',
  done: '#3a4152',
  blocked: '#ff6b6b',
}

interface GraphProps {
  plan: Plan
  selectedId: string | null
  arming: boolean
  flyTo: NodeSignal | null
  shake: NodeSignal | null
  onSelect: (id: string | null) => void
  onLinkRightClick: (dependencyId: string, dependentId: string) => void
}

const idOf = (end: unknown) => (typeof end === 'string' ? end : (end as GraphNode).id)

export default function Graph({ plan, selectedId, arming, flyTo, shake, onSelect, onLinkRightClick }: GraphProps) {
  const [cache] = useState(() => new Map<string, GraphNode>())
  const [labels] = useState(() => new Map<string, HTMLDivElement>())
  const [seenStatus] = useState(() => new Map<string, Status>())
  const [extraRenderers] = useState(() => [new CSS2DRenderer()])
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined)
  const [size, setSize] = useState({ w: 800, h: 600 })
  const pick = useRef(onSelect)

  useEffect(() => {
    pick.current = onSelect
  })
  const onPick = useCallback((id: string) => pick.current(id), [])

  useEffect(() => {
    const update = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])

  const blocked = useRef(new Set<Pulsable>())

  useEffect(() => {
    let raf = 0
    const tick = (t: number) => {
      pulseBlocked(blocked.current, t)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  useEffect(() => {
    const fg = fgRef.current
    if (fg) fg.scene().fog = new THREE.FogExp2(0x05060a, 0.002)
  }, [])

  const structureKey = plan.nodes.map(n => `${n.id}:${n.status}:${n.title}:${n.depends_on.join(',')}`).join('|')
  const data = useMemo(() => {
    return toGraphData(plan, cache)
  }, [structureKey]) // eslint-disable-line react-hooks/exhaustive-deps

  const neighbors = useMemo(() => {
    const set = new Set<string>()
    if (!selectedId) return set
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId) set.add(idOf(l.target))
      if (l.target === selectedId || idOf(l.target) === selectedId) set.add(idOf(l.source))
    }
    return set
  }, [data, selectedId])

  useEffect(() => {
    syncLabels(
      labels,
      plan.nodes.map(n => ({
        id: n.id,
        title: n.title,
        status: n.status,
        selected: n.id === selectedId,
        dim: !!selectedId && n.id !== selectedId && !neighbors.has(n.id),
      })),
      onPick,
    )
  }, [labels, plan, selectedId, neighbors, onPick])

  useEffect(() => {
    const fg = fgRef.current
    const node = flyTo ? cache.get(flyTo.id) : undefined
    if (!fg || !node) return
    const { position, lookAt } = cameraFor(node)
    fg.cameraPosition(position, lookAt, 800)
  }, [flyTo, cache])

  useEffect(() => {
    const el = shake ? labels.get(shake.id) : undefined
    if (el) shakeLabel(el)
  }, [shake, labels])

  useEffect(() => {
    const ids = takeNewlyDone(seenStatus, plan.nodes)
    const fg = fgRef.current
    if (!fg || ids.length === 0 || prefersReducedMotion()) return
    const scene = fg.scene()
    const camera = fg.camera()
    const rings = ids.flatMap(id => {
      const node = cache.get(id)
      if (!node) return []
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(7, 8.5, 48),
        new THREE.MeshBasicMaterial({ color: 0xcfe8ff, transparent: true, opacity: 0.9, side: THREE.DoubleSide }),
      )
      ring.position.set(node.x ?? 0, node.y ?? 0, node.z ?? 0)
      ring.quaternion.copy(camera.quaternion)
      scene.add(ring)
      return [ring]
    })
    const start = performance.now()
    // No cleanup: the burst is one-shot and removes itself. Under StrictMode the effect re-runs,
    // and a cleanup would cancel the ring on the first run while the second run sees no change.
    const tick = (t: number) => {
      const f = burstFrame(t - start)
      for (const r of rings) {
        r.scale.setScalar(f.scale)
        r.material.opacity = f.opacity
      }
      if (!f.done) {
        requestAnimationFrame(tick)
        return
      }
      for (const r of rings) {
        scene.remove(r)
        r.geometry.dispose()
        r.material.dispose()
      }
    }
    requestAnimationFrame(tick)
  }, [plan, seenStatus, cache])

  return (
    <div data-arming={arming} style={{ cursor: arming ? 'crosshair' : 'default' }}>
      <ForceGraph3D<GraphNode, GraphLink>
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#05060a"
        extraRenderers={extraRenderers}
        nodeThreeObject={(n: GraphNode) => {
          const selected = n.id === selectedId
          const dim = !!selectedId && !selected && !neighbors.has(n.id)
          const radius = selected ? 6.5 : 5
          const color = new THREE.Color(STATUS_COLORS[n.status])
          const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: n.status === 'done' ? 0.15 : 0.7, transparent: true, opacity: dim ? 0.18 : 1, roughness: 0.4 })
          const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 24, 24), mat)
          if (n.status === 'blocked') blocked.current.add(mesh as unknown as Pulsable)
          if (selected) {
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x5ac8fa, transparent: true, opacity: 0.85 })
            mesh.add(new THREE.Mesh(new THREE.TorusGeometry(radius + 3, 0.45, 8, 48), ringMat))
          }
          const label = new CSS2DObject(labelFor(labels, n.id, onPick))
          label.center.set(0.5, 0)
          label.position.set(0, -radius, 0)
          mesh.add(label)
          return mesh
        }}
        nodeThreeObjectExtend={false}
        linkColor={() => '#7a8399'}
        linkOpacity={0.5}
        linkWidth={(l: GraphLink) => (selectedId && (idOf(l.source) === selectedId || idOf(l.target) === selectedId) ? 2 : 0.6)}
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={(l: GraphLink) => (selectedId && idOf(l.target) === selectedId ? 2 : 0)}
        onNodeClick={(n: GraphNode) => onSelect(n.id)}
        onBackgroundClick={() => onSelect(null)}
        onLinkRightClick={(l: GraphLink) => onLinkRightClick(idOf(l.source), idOf(l.target))}
      />
    </div>
  )
}
```

Append to `depgraph/src/app/globals.css`:

```css
@keyframes dg-shake {
  0%, 100% { translate: 0 0; }
  20%, 60% { translate: -4px 0; }
  40%, 80% { translate: 4px 0; }
}
.node-label[data-shake='true'] .node-label-title {
  display: inline-block;
  color: #ff8a8a;
  animation: dg-shake 400ms ease-in-out;
}
@media (prefers-reduced-motion: reduce) {
  .node-label[data-shake='true'] .node-label-title { animation: none; }
}
```

- [ ] **Step 4: Rewrite the page with `attempt`**

Replace `depgraph/src/app/page.tsx` with:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useConfirm } from '@/hooks/useConfirm'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNextNode, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan, Status } from '@/lib/schema'
import {
  initialSelection,
  nextSignal,
  selectionStep,
  type NodeSignal,
  type SelectionEvent,
  type SelectionState,
} from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
  const [editTitleFor, setEditTitleFor] = useState<string | null>(null)
  const [fly, setFly] = useState<NodeSignal | null>(null)
  const [shake, setShake] = useState<NodeSignal | null>(null)
  const toast = useToast()
  const confirmDelete = useConfirm(3000)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  // Apply a mutation. On refusal, show a red toast and shake the node it targeted.
  const attempt = (targetId: string | null, mutate: (p: Plan) => Plan): boolean => {
    const errors = apply(mutate)
    if (errors.length === 0) return true
    toast.show(errors.join('; '), 'error')
    if (targetId) setShake(s => nextSignal(s, targetId))
    return false
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (state.selectedId !== activeId) setEditTitleFor(null)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') attempt(effect.dependencyId, p => addDependency(p, effect.dependencyId, effect.dependentId))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  const flyTo = (id: string) => setFly(f => nextSignal(f, id))

  const focusNode = (id: string) => {
    dispatch({ type: 'focusNode', id })
    flyTo(id)
  }

  const addAndEdit = (make: (p: Plan) => { plan: Plan; id: string }) => {
    let newId = ''
    const ok = attempt(null, p => {
      const r = make(p)
      newId = r.id
      return r.plan
    })
    if (!ok || !newId) return
    setSelection({ selectedId: newId, arming: false })
    setEditTitleFor(newId)
  }

  const handleAddNode = () => addAndEdit(p => addNode(p))

  const handleAddNext = () => {
    if (!activeId) {
      toast.show('select a node first')
      return
    }
    const from = activeId
    addAndEdit(p => addNextNode(p, from))
  }

  const setStatus = (status: Status) => {
    if (activeId) attempt(activeId, p => updateNode(p, activeId, { status }))
  }

  const handleDelete = () => {
    if (!activeId) return
    const id = activeId
    confirmDelete.press(id, () => {
      if (attempt(id, p => deleteNode(p, id))) dispatch({ type: 'clear' })
    })
  }

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
    n: handleAddNode,
    'shift+n': handleAddNext,
    '1': () => setStatus('todo'),
    '2': () => setStatus('doing'),
    '3': () => setStatus('done'),
    '4': () => setStatus('blocked'),
    delete: handleDelete,
    f: () => {
      if (activeId) flyTo(activeId)
    },
  })

  const handleNewPlan = async () => {
    const name = window.prompt('Plan name')
    if (!name) return
    const res = await fetch('/api/plans', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const body = await res.json()
    if (!res.ok) {
      toast.show((body.errors as string[]).join('; '), 'error')
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={activeId}
        arming={armed}
        flyTo={fly}
        shake={shake}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => attempt(dependent, p => removeDependency(p, dep, dependent))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {plan.nodes.length === 0 && (
        <p data-testid="empty-hint" className="pointer-events-none fixed inset-x-0 top-1/2 -translate-y-1/2 text-center text-sm text-white/60">
          Press N or click + Node to place your first step.
        </p>
      )}
      {activeNode && (
        <NodeHud
          key={activeNode.id}
          plan={plan}
          node={activeNode}
          armed={armed}
          editTitle={editTitleFor === activeNode.id}
          deleteArmed={confirmDelete.isArmed(activeNode.id)}
          onChange={patch => attempt(activeNode.id, p => updateNode(p, activeNode.id, patch))}
          onToggleLink={toggleLink}
          onFocusNode={focusNode}
          onRemoveDependency={dep => attempt(activeNode.id, p => removeDependency(p, dep, activeNode.id))}
          onDelete={handleDelete}
          onAddNext={handleAddNext}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      <Toast message={toast.message} tone={toast.tone} />
      <SaveIndicator state={saveState} error={saveError} />
    </>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center font-mono text-sm text-white/50">{text}</div>
}

export default function Page() {
  return (
    <Suspense>
      <Workspace />
    </Suspense>
  )
}
```

- [ ] **Step 5: Update the README controls**

In `depgraph/README.md`, replace the line that starts with `Controls: click node = select/edit` with:

```markdown
Controls (click-first):

- Click a node or its label to select it; click empty space to deselect. Every node's title is always shown; hover or select to see its id.
- The card at the bottom edits the selection: click the title to rename (Enter saves, Esc reverts), click a status pip, click the description to expand it, `×` on a tag removes it and `+` adds one, "needs:" chips jump to that node (`×` removes the dependency), "unlocks:" chips show what waits on it.
- `+` / **L** arms linking: every node you click next becomes a dependency of the selection, until **Esc**.
- `+next` / **Shift+N** adds a step that depends on the selection. `del` / **Del** asks once, then deletes (disarms after 3 s).
- Hotkeys: **N** add node · **1–4** todo/doing/done/blocked · **F** fly to the selection · **Esc** backs out one step (edit, then linking, then selection). Hotkeys are ignored while typing.
- Right-click an arrow to remove that dependency.
```

- [ ] **Step 6: Run e2e and watch it pass**

Run: `npm run test:e2e`
Expected: `8 passed`.

- [ ] **Step 7: Full check, plus a short manual look at the WebGL-only parts**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: Vitest `Test Files  20 passed (20)`, 0 failed; tsc and eslint print nothing; Playwright `8 passed`.

Manual check of the untestable WebGL bits: run `npx playwright test -g "hotkeys 1–4 and N work" --headed` and watch that a ring bursts when **3** sets done. Everything else in this slice is asserted by tests.

- [ ] **Step 8: Commit**

```bash
git add e2e/smoke.spec.ts src/app/page.tsx src/components/Graph.tsx src/app/globals.css README.md
git commit -m "depgraph: red error toast + label shake, done ring burst (reduced-motion aware), README controls" -m "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Spec coverage map

| Spec item | Task |
|---|---|
| Remove `NodePanel.tsx` | 8.7 |
| `NodeHud.tsx`, `StatusPips.tsx`, `InlineText.tsx`, `hooks/useHotkeys.ts` (ignored while typing) | 7.6/8.6, 8.4, 8.5, 7.3–7.4 |
| Slim Toolbar (plan select, count, + Node, New plan; no Link-mode toggle) | 7.5, 9.3 (keycap) |
| Graph: always-on labels, selection torus, armed crosshair, done-burst; right-click unlinks | 6.3, 6.3, 7.7, 10.4; kept in every Graph version |
| `lib/selection.ts` replaces `lib/linkMode.ts` (+test) | 7.1, 7.2, 8.1, 7.7 (delete) |
| Click node/label selects; background deselects | 6.2/6.3, 7.1, 7.7 |
| L / `+L` arms; each clicked node becomes a dependency until Esc | 7.2, 7.7, 8.6 |
| 1–4 or pip click sets status | 8.4, 9.3 |
| N adds, selects, opens title; Shift+N "+next" depends on selection | 8.7 (`editTitleFor`), 9.1–9.3 |
| Del arms "Confirm delete", disarms after 3 s; second Del or click deletes | 8.3, 8.6, 9.3 |
| F flies camera; Esc backs out one step (edit → disarm → deselect) | 8.2, 9.3; 8.5 (edit), 7.2 |
| CSS2D label via `extraRenderers` 8 px below sphere, 12 px, status tint, 24-char ellipsis, full title in `title=`, fade to 25% outside neighborhood, id on hover/selection, overlay `pointer-events: none` / label `auto` | 6.1–6.3 |
| needs chips (click selects + flies; × removes), read-only unlocks chips | 8.1, 8.2, 8.6, 8.7 |
| Title InlineText (Enter saves, Esc reverts); description preview → 6-row textarea, saves on blur; tag chips × and `+` input | 8.5, 8.6 |
| Empty-plan message | 9.3 |
| Error: red toast + target node shakes; info toasts amber | 10.1, 10.2, 10.4 |
| `SaveIndicator` unchanged | untouched |
| Card 560 px, slides up 120 ms, keycap hints | 8.6 (CSS), 8.4 (`Keycap`), 9.2, 9.3 |
| Done ring burst skipped under reduced motion | 10.3, 10.4 |
| Testability contract table | Global Constraints; asserted in 7.5, 7.6, 8.4–8.6, 9.2 and e2e |
| E2E: test 1 unchanged; test 2 HUD flow; test 3 "Add dependency arms, Esc disarms"; test 4 label click; all 8 labels visible; hotkeys 1–4 and N | 8.7, 7.7, 7.7, 6.3, 9.3 |

## Spec ambiguities resolved

1. **`nodeThreeObjectExtend={true}` vs the custom sphere.** With `extend=true`, three-forcegraph draws its default Lambert sphere and adds our object as a child. We would then either lose the emissive status sphere and the blocked pulse (`pulse.ts` needs `emissiveIntensity`), or draw two spheres. The label is instead a `CSS2DObject` child of our own sphere with `nodeThreeObjectExtend={false}`. The spec's intent (a label attached to the node, 8 px below, via `extraRenderers`) is unchanged.
2. **Label reuse.** three-forcegraph re-creates node objects on every prop change and removes the old sphere with `scene.remove`, which does not fire `removed` on child `CSS2DObject`s. Label elements are therefore cached per node id (`labelFor`) and removed only when the node leaves the plan (`syncLabels`).
3. **Label click vs background click.** The graph container arms its click on `pointerdown` and fires on `pointerup` in the capture phase. A label click would therefore also deselect. The label stops `pointerdown` propagation.
4. **"Tinted with the status color" for done.** The done sphere color `#3a4152` is unreadable as text on the dark background, so done labels use `#7d8699`. Other statuses use their sphere colors (todo is lightened to `#c3cad6`). Status is exposed as `data-status` and styled in CSS, because jsdom normalizes inline colors.
5. **Background click while armed** only disarms (one step back, like Esc) and keeps the selection. **Clicking the selection itself while armed** gives an info toast "a node cannot depend on itself". **L without a selection** gives "select a node first".
6. **Chip clicks while armed** use a new `focusNode` event that selects and disarms, so navigation never creates a link.
7. **Del key** also accepts `Backspace`, because Mac keyboards send `Backspace` from the key labelled "delete". Hotkeys are ignored in input, textarea, select and contenteditable, and when Meta, Ctrl or Alt is held.
8. **Which node shakes.** For a refused link it is the clicked node (the would-be dependency). For field edits, status, delete and chip removal it is the selected node. For an arrow right-click it is the dependent.
9. **Test 4** ("its checkbox step becomes a label click"): the label click is now the step that attempts the cycle (select `schema`, Add dependency, click the `api-routes` label). The test asserts the error toast and an unchanged file, then keeps the original API assertion.
10. **Accessible names and keycaps.** The contract names are set with `aria-label`, and keycap hints are `aria-hidden`, so hints never change a control's name. The `link-hint` (role status) and the toast (role status) are both live regions, so tests address them by test id.
11. **Toast position** moves to top center so it never covers the bottom HUD.
12. **Extra test ids** beyond the contract: `unlock-<id>` for "unlocks:" chips and `empty-hint` for the empty-plan message.
13. **Slicing.** The suggested Slice 9 is split into Slice 9 (hotkeys, add-next, empty state) and Slice 10 (feedback/motion, README). The Toolbar clean-up moves into Slice 7, because deleting `linkMode.ts` leaves the Link-mode toggle with nothing behind it. A minimal `NodeHud` ships in Slice 7 so `link-button` and `link-hint` exist before the full card, and `NodePanel` coexists with it for one slice.
