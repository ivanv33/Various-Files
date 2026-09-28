# Dependency Graph Plan Visualizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A local-only Next.js app that renders a plan stored as `depgraph/plans/<slug>.json` as an editable 3D dependency graph, writing every edit back to the file and refreshing when the file changes on disk.

**Architecture:** Pure logic (`lib/schema.ts`, `lib/mutations.ts`, `lib/graphData.ts`) is shared by server and client and fully unit-tested. `lib/store.ts` is the only module that touches the filesystem; thin Next.js route handlers wrap it, plus one Server-Sent Events route fed by a chokidar watcher. The client has a single state owner (`hooks/usePlan.ts`) that validates locally, saves with a 300 ms debounce, and refetches on SSE `changed`. `react-force-graph-3d` (three.js) renders the scene.

**Tech Stack:** Next.js 16.3 (App Router, TypeScript, Tailwind v4), React 19, react-force-graph-3d 1.29, three, chokidar 5, Vitest 5, Playwright.

Spec: `docs/superpowers/specs/2026-09-28-depgraph-visualizer-design.md`

## Global Constraints

- App lives in `depgraph/` at the repo root. All commands below run from `depgraph/` unless stated.
- Plans dir defaults to `depgraph/plans/`; overridable with env `PLANS_DIR` (absolute or relative to cwd).
- Node id regex: `^[a-z0-9][a-z0-9-]*$`. Statuses: `todo | doing | done | blocked`.
- Saved files: nodes sorted by id, `depends_on` sorted, 2-space indent, trailing newline.
- Edge direction: dependency -> dependent (arrow points at the node that waits).
- No deployment, no auth. `npm run dev` only.
- Never rename an id from the UI.
- Commit after every task with the message shown. Commit messages end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

---

## File structure

```
depgraph/
  package.json, tsconfig.json, next.config.ts, vitest.config.ts, playwright.config.ts
  plans/example.json                       sample plan (git-tracked)
  src/lib/schema.ts                        types, validatePlan, normalizePlan, serializePlan, slugify, uniqueId
  src/lib/schema.test.ts
  src/lib/mutations.ts                     pure plan edits: addNode, updateNode, deleteNode, addDependency, removeDependency
  src/lib/mutations.test.ts
  src/lib/graphData.ts                     plan -> {nodes, links} for force-graph, with object cache
  src/lib/graphData.test.ts
  src/lib/store.ts                         fs: listPlans, readPlan, writePlan, createPlan, lastWrittenHash
  src/lib/store.test.ts
  src/lib/watcher.ts                       chokidar singleton -> subscribe(slug listener)
  src/lib/watcher.test.ts
  src/app/api/plans/route.ts               GET list, POST create
  src/app/api/plans/[slug]/route.ts        GET one, PUT replace
  src/app/api/plans/[slug]/events/route.ts SSE
  src/app/api/plans/route.test.ts
  src/app/api/plans/slug.test.ts
  src/hooks/usePlan.ts                     client state owner
  src/components/Graph.tsx                 ForceGraph3D wrapper
  src/components/NodePanel.tsx
  src/components/Toolbar.tsx
  src/components/SaveIndicator.tsx
  src/components/Toast.tsx
  src/app/page.tsx, src/app/layout.tsx, src/app/globals.css
  e2e/smoke.spec.ts                        Playwright
  e2e/plans/                               fixture dir written by e2e (gitignored)
```

---

### Task 1: Scaffold the app, test runner, and sample plan

**Files:**
- Create: `depgraph/` via create-next-app
- Create: `depgraph/vitest.config.ts`, `depgraph/plans/example.json`, `depgraph/src/lib/smoke.test.ts`
- Modify: `depgraph/package.json` (scripts), `depgraph/.gitignore`

**Interfaces:**
- Produces: a working `npm run dev` on port 3000, `npm test` running Vitest with `@/` alias mapped to `src/`.

- [ ] **Step 1: Scaffold**

Run from the repo root:

```bash
npx --yes create-next-app@16.3.6 depgraph --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm --yes
```

If it prompts anyway, accept defaults. Expected: `depgraph/` exists with `src/app/page.tsx`.

- [ ] **Step 2: Install dependencies**

```bash
cd depgraph
npm i react-force-graph-3d three chokidar
npm i -D vitest @types/three @playwright/test
```

- [ ] **Step 3: Vitest config and scripts**

Create `depgraph/vitest.config.ts`:

```ts
import { defineConfig } from 'vitest/config'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
    testTimeout: 10000,
  },
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
})
```

In `depgraph/package.json` add to `"scripts"`:

```json
"test": "vitest run",
"test:watch": "vitest",
"test:e2e": "playwright test"
```

Append to `depgraph/.gitignore`:

```
e2e/plans/
test-results/
playwright-report/
```

- [ ] **Step 4: Smoke test**

Create `depgraph/src/lib/smoke.test.ts`:

```ts
import { describe, expect, it } from 'vitest'

describe('vitest', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2)
  })
})
```

Run: `npm test`
Expected: `1 passed`.

- [ ] **Step 5: Sample plan**

Create `depgraph/plans/example.json`:

```json
{
  "name": "Example: ship the visualizer",
  "nodes": [
    {
      "id": "api-routes",
      "title": "Write API routes",
      "description": "GET/PUT plan files through Next route handlers.",
      "status": "doing",
      "tags": ["server"],
      "depends_on": ["schema", "store"]
    },
    {
      "id": "design-spec",
      "title": "Approve design spec",
      "description": "",
      "status": "done",
      "tags": ["planning"],
      "depends_on": []
    },
    {
      "id": "e2e",
      "title": "Playwright smoke test",
      "description": "Add a node, reload, it persists.",
      "status": "todo",
      "tags": ["testing"],
      "depends_on": ["node-panel", "graph-view"]
    },
    {
      "id": "graph-view",
      "title": "3D force graph view",
      "description": "react-force-graph-3d wrapper with status colors.",
      "status": "todo",
      "tags": ["client"],
      "depends_on": ["api-routes"]
    },
    {
      "id": "node-panel",
      "title": "Node edit panel",
      "description": "Title, description, status, tags, dependencies.",
      "status": "blocked",
      "tags": ["client"],
      "depends_on": ["graph-view"]
    },
    {
      "id": "schema",
      "title": "Schema + validator",
      "description": "Types, cycle detection, normalization.",
      "status": "done",
      "tags": ["core"],
      "depends_on": ["design-spec"]
    },
    {
      "id": "store",
      "title": "File store",
      "description": "Atomic writes, hash of last write.",
      "status": "done",
      "tags": ["server"],
      "depends_on": ["schema"]
    },
    {
      "id": "watcher",
      "title": "File watcher + SSE",
      "description": "Refresh the browser when the file changes on disk.",
      "status": "todo",
      "tags": ["server"],
      "depends_on": ["store"]
    }
  ]
}
```

- [ ] **Step 6: Verify dev server boots**

Run: `npm run dev -- -p 3000` in the background, then `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/`
Expected: `200`. Stop the server.

- [ ] **Step 7: Commit**

```bash
cd ..
git add depgraph
git commit -m "depgraph: scaffold Next.js app, vitest, sample plan

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Schema, validation, normalization

**Files:**
- Create: `depgraph/src/lib/schema.ts`, `depgraph/src/lib/schema.test.ts`
- Delete: `depgraph/src/lib/smoke.test.ts`

**Interfaces:**
- Produces:
  ```ts
  export const STATUSES: readonly ['todo','doing','done','blocked']
  export type Status = 'todo'|'doing'|'done'|'blocked'
  export interface PlanNode { id: string; title: string; description: string; status: Status; tags: string[]; depends_on: string[] }
  export interface Plan { name: string; nodes: PlanNode[] }
  export const ID_RE: RegExp
  export function validatePlan(input: unknown): string[]      // [] means valid
  export function findCycle(nodes: Pick<PlanNode,'id'|'depends_on'>[]): string[] | null
  export function normalizePlan(plan: Plan): Plan               // sorted, defaults filled, new object
  export function serializePlan(plan: Plan): string             // JSON.stringify(normalizePlan(plan), null, 2) + '\n'
  export function slugify(text: string): string
  export function uniqueId(base: string, existing: Iterable<string>): string
  ```

- [ ] **Step 1: Write failing tests**

Create `depgraph/src/lib/schema.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import {
  findCycle, normalizePlan, serializePlan, slugify, uniqueId, validatePlan, type Plan,
} from '@/lib/schema'

const node = (id: string, depends_on: string[] = [], extra: Partial<Plan['nodes'][number]> = {}) => ({
  id, title: id, description: '', status: 'todo' as const, tags: [], depends_on, ...extra,
})

describe('validatePlan', () => {
  it('accepts a valid plan', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a'), node('b', ['a'])] })).toEqual([])
  })
  it('rejects non-object input', () => {
    expect(validatePlan(null)).toEqual(['plan must be an object'])
    expect(validatePlan('x')).toEqual(['plan must be an object'])
  })
  it('requires name and nodes', () => {
    expect(validatePlan({})).toEqual(['name must be a string', 'nodes must be an array'])
  })
  it('rejects bad id format', () => {
    expect(validatePlan({ name: 'p', nodes: [node('Bad Id')] })).toEqual(['node 0: id "Bad Id" does not match ^[a-z0-9][a-z0-9-]*$'])
  })
  it('rejects duplicate ids', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a'), node('a')] })).toEqual(['node 1: duplicate id "a"'])
  })
  it('rejects bad status', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a', [], { status: 'nope' as never })] })).toEqual(['node "a": invalid status "nope"'])
  })
  it('rejects unknown dependency', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a', ['zzz'])] })).toEqual(['node "a": unknown dependency "zzz"'])
  })
  it('rejects self dependency', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a', ['a'])] })).toEqual(['node "a": depends on itself'])
  })
  it('rejects a 3-node cycle', () => {
    const errors = validatePlan({ name: 'p', nodes: [node('a', ['c']), node('b', ['a']), node('c', ['b'])] })
    expect(errors).toEqual(['cycle: a -> c -> b -> a'])
  })
  it('rejects non-string tags and non-string description', () => {
    expect(validatePlan({ name: 'p', nodes: [node('a', [], { tags: [1] as never, description: 2 as never })] }))
      .toEqual(['node "a": description must be a string', 'node "a": tags must be an array of strings'])
  })
})

describe('findCycle', () => {
  it('returns null for a DAG', () => {
    expect(findCycle([node('a'), node('b', ['a']), node('c', ['a', 'b'])])).toBeNull()
  })
  it('returns the cycle path', () => {
    expect(findCycle([node('a', ['b']), node('b', ['a'])])).toEqual(['a', 'b', 'a'])
  })
})

describe('normalizePlan', () => {
  it('sorts nodes and depends_on, fills defaults, does not mutate input', () => {
    const input = {
      name: 'p',
      nodes: [
        { id: 'b', title: 'B', depends_on: ['z', 'a'] },
        { id: 'a', title: 'A' },
        { id: 'z', title: 'Z' },
      ],
    } as unknown as Plan
    const out = normalizePlan(input)
    expect(out.nodes.map(n => n.id)).toEqual(['a', 'b', 'z'])
    expect(out.nodes[1].depends_on).toEqual(['a', 'z'])
    expect(out.nodes[0]).toEqual({ id: 'a', title: 'A', description: '', status: 'todo', tags: [], depends_on: [] })
    expect(input.nodes[0].id).toBe('b')
  })
})

describe('serializePlan', () => {
  it('is deterministic with 2-space indent and trailing newline', () => {
    const plan: Plan = { name: 'p', nodes: [node('b'), node('a')] }
    const text = serializePlan(plan)
    expect(text.endsWith('\n')).toBe(true)
    expect(text).toBe(JSON.stringify(normalizePlan(plan), null, 2) + '\n')
    expect(serializePlan(JSON.parse(text))).toBe(text)
  })
})

describe('slugify / uniqueId', () => {
  it('slugifies', () => {
    expect(slugify('  Size 6-12mo Runway! ')).toBe('size-6-12mo-runway')
    expect(slugify('___')).toBe('untitled')
    expect(slugify('-leading')).toBe('leading')
  })
  it('dedupes with -2, -3', () => {
    expect(uniqueId('a', ['a', 'a-2'])).toBe('a-3')
    expect(uniqueId('b', ['a'])).toBe('b')
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test`
Expected: FAIL, cannot resolve `@/lib/schema`.

- [ ] **Step 3: Implement**

Create `depgraph/src/lib/schema.ts`:

```ts
export const STATUSES = ['todo', 'doing', 'done', 'blocked'] as const
export type Status = (typeof STATUSES)[number]

export interface PlanNode {
  id: string
  title: string
  description: string
  status: Status
  tags: string[]
  depends_on: string[]
}

export interface Plan {
  name: string
  nodes: PlanNode[]
}

export const ID_RE = /^[a-z0-9][a-z0-9-]*$/

const isRecord = (v: unknown): v is Record<string, unknown> =>
  typeof v === 'object' && v !== null && !Array.isArray(v)
const isStringArray = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every(x => typeof x === 'string')

export function findCycle(nodes: Pick<PlanNode, 'id' | 'depends_on'>[]): string[] | null {
  const deps = new Map(nodes.map(n => [n.id, n.depends_on]))
  const state = new Map<string, 'visiting' | 'done'>()
  const stack: string[] = []
  const visit = (id: string): string[] | null => {
    const s = state.get(id)
    if (s === 'done') return null
    if (s === 'visiting') return [...stack.slice(stack.indexOf(id)), id]
    state.set(id, 'visiting')
    stack.push(id)
    for (const d of deps.get(id) ?? []) {
      if (!deps.has(d)) continue
      const found = visit(d)
      if (found) return found
    }
    stack.pop()
    state.set(id, 'done')
    return null
  }
  for (const n of nodes) {
    const found = visit(n.id)
    if (found) return found
  }
  return null
}

export function validatePlan(input: unknown): string[] {
  if (!isRecord(input)) return ['plan must be an object']
  const errors: string[] = []
  if (typeof input.name !== 'string') errors.push('name must be a string')
  if (!Array.isArray(input.nodes)) {
    errors.push('nodes must be an array')
    return errors
  }
  const seen = new Set<string>()
  const wellFormed: Pick<PlanNode, 'id' | 'depends_on'>[] = []
  input.nodes.forEach((raw, i) => {
    if (!isRecord(raw)) {
      errors.push(`node ${i}: must be an object`)
      return
    }
    const id = raw.id
    if (typeof id !== 'string' || !ID_RE.test(id)) {
      errors.push(`node ${i}: id "${String(id)}" does not match ^[a-z0-9][a-z0-9-]*$`)
      return
    }
    if (seen.has(id)) {
      errors.push(`node ${i}: duplicate id "${id}"`)
      return
    }
    seen.add(id)
    if (typeof raw.title !== 'string') errors.push(`node "${id}": title must be a string`)
    if (raw.description !== undefined && typeof raw.description !== 'string')
      errors.push(`node "${id}": description must be a string`)
    if (raw.status !== undefined && !STATUSES.includes(raw.status as Status))
      errors.push(`node "${id}": invalid status "${String(raw.status)}"`)
    if (raw.tags !== undefined && !isStringArray(raw.tags))
      errors.push(`node "${id}": tags must be an array of strings`)
    if (raw.depends_on !== undefined && !isStringArray(raw.depends_on)) {
      errors.push(`node "${id}": depends_on must be an array of strings`)
      return
    }
    wellFormed.push({ id, depends_on: raw.depends_on ?? [] })
  })
  for (const n of wellFormed) {
    for (const d of n.depends_on) {
      if (d === n.id) errors.push(`node "${n.id}": depends on itself`)
      else if (!seen.has(d)) errors.push(`node "${n.id}": unknown dependency "${d}"`)
    }
  }
  if (errors.length === 0) {
    const cycle = findCycle(wellFormed)
    if (cycle) errors.push(`cycle: ${cycle.join(' -> ')}`)
  }
  return errors
}

export function normalizePlan(plan: Plan): Plan {
  const nodes = plan.nodes
    .map(n => ({
      id: n.id,
      title: n.title ?? '',
      description: n.description ?? '',
      status: n.status ?? 'todo',
      tags: [...(n.tags ?? [])],
      depends_on: [...(n.depends_on ?? [])].sort(),
    }))
    .sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0))
  return { name: plan.name, nodes }
}

export function serializePlan(plan: Plan): string {
  return JSON.stringify(normalizePlan(plan), null, 2) + '\n'
}

export function slugify(text: string): string {
  const s = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  return s || 'untitled'
}

export function uniqueId(base: string, existing: Iterable<string>): string {
  const taken = new Set(existing)
  if (!taken.has(base)) return base
  for (let i = 2; ; i++) {
    const candidate = `${base}-${i}`
    if (!taken.has(candidate)) return candidate
  }
}
```

Delete `depgraph/src/lib/smoke.test.ts`.

- [ ] **Step 4: Run tests**

Run: `npm test`
Expected: all schema tests PASS.

- [ ] **Step 5: Commit**

```bash
git add -A src/lib
git commit -m "depgraph: plan schema, validator with cycle detection, normalizer

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: File store with atomic writes

**Files:**
- Create: `depgraph/src/lib/store.ts`, `depgraph/src/lib/store.test.ts`

**Interfaces:**
- Consumes: `Plan`, `validatePlan`, `serializePlan`, `slugify`, `ID_RE` from `@/lib/schema`.
- Produces:
  ```ts
  export interface PlanSummary { slug: string; name: string; nodeCount: number }
  export class PlanExistsError extends Error {}
  export function plansDir(): string
  export function hashOf(text: string): string
  export function lastWrittenHash(slug: string): string | undefined
  export async function listPlans(dir?: string): Promise<PlanSummary[]>
  export async function readPlan(slug: string, dir?: string): Promise<Plan | null>
  export async function writePlan(slug: string, plan: Plan, dir?: string): Promise<Plan>   // throws Error(errors.join('; ')) if invalid
  export async function createPlan(name: string, dir?: string): Promise<{ slug: string; plan: Plan }>
  ```

- [ ] **Step 1: Write failing tests**

Create `depgraph/src/lib/store.test.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtemp, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import {
  createPlan, hashOf, lastWrittenHash, listPlans, PlanExistsError, plansDir, readPlan, writePlan,
} from '@/lib/store'
import { serializePlan, type Plan } from '@/lib/schema'

let dir: string
const plan: Plan = {
  name: 'Test',
  nodes: [
    { id: 'b', title: 'B', description: '', status: 'todo', tags: [], depends_on: ['a'] },
    { id: 'a', title: 'A', description: '', status: 'done', tags: [], depends_on: [] },
  ],
}

beforeEach(async () => { dir = await mkdtemp(path.join(tmpdir(), 'depgraph-')) })
afterEach(async () => { await rm(dir, { recursive: true, force: true }) })

describe('plansDir', () => {
  it('uses PLANS_DIR when set, else ./plans', () => {
    const prev = process.env.PLANS_DIR
    process.env.PLANS_DIR = '/tmp/x'
    expect(plansDir()).toBe('/tmp/x')
    delete process.env.PLANS_DIR
    expect(plansDir()).toBe(path.join(process.cwd(), 'plans'))
    if (prev !== undefined) process.env.PLANS_DIR = prev
  })
})

describe('writePlan / readPlan', () => {
  it('round-trips normalized, atomically, and records the hash', async () => {
    const written = await writePlan('test', plan, dir)
    expect(written.nodes.map(n => n.id)).toEqual(['a', 'b'])
    const text = await readFile(path.join(dir, 'test.json'), 'utf8')
    expect(text).toBe(serializePlan(plan))
    expect(await readdir(dir)).toEqual(['test.json'])
    expect(lastWrittenHash('test')).toBe(hashOf(text))
    expect(await readPlan('test', dir)).toEqual(written)
  })
  it('rejects invalid plans without writing', async () => {
    const bad = { name: 'x', nodes: [{ id: 'a', title: 'A', depends_on: ['a'] }] } as unknown as Plan
    await expect(writePlan('bad', bad, dir)).rejects.toThrow('depends on itself')
    expect(await readdir(dir)).toEqual([])
  })
  it('returns null for a missing plan', async () => {
    expect(await readPlan('nope', dir)).toBeNull()
  })
  it('rejects slugs that are not valid ids', async () => {
    await expect(readPlan('../etc', dir)).rejects.toThrow('invalid slug')
    await expect(writePlan('A B', plan, dir)).rejects.toThrow('invalid slug')
  })
})

describe('listPlans', () => {
  it('lists json files sorted by slug with counts, ignoring others', async () => {
    await writePlan('zeta', plan, dir)
    await writePlan('alpha', { name: 'Alpha', nodes: [] }, dir)
    await writeFile(path.join(dir, 'notes.txt'), 'x')
    expect(await listPlans(dir)).toEqual([
      { slug: 'alpha', name: 'Alpha', nodeCount: 0 },
      { slug: 'zeta', name: 'Test', nodeCount: 2 },
    ])
  })
  it('returns [] when the dir does not exist', async () => {
    expect(await listPlans(path.join(dir, 'missing'))).toEqual([])
  })
})

describe('createPlan', () => {
  it('creates an empty plan from a name and refuses duplicates', async () => {
    const { slug, plan: created } = await createPlan('My Big Plan', dir)
    expect(slug).toBe('my-big-plan')
    expect(created).toEqual({ name: 'My Big Plan', nodes: [] })
    await expect(createPlan('My Big Plan', dir)).rejects.toBeInstanceOf(PlanExistsError)
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test -- store`
Expected: FAIL, cannot resolve `@/lib/store`.

- [ ] **Step 3: Implement**

Create `depgraph/src/lib/store.ts`:

```ts
import { createHash } from 'node:crypto'
import { mkdir, readdir, readFile, rename, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { ID_RE, serializePlan, slugify, validatePlan, type Plan } from '@/lib/schema'

export interface PlanSummary { slug: string; name: string; nodeCount: number }
export class PlanExistsError extends Error {}

// Survives Next.js dev HMR re-evaluation of this module.
const g = globalThis as unknown as { __depgraphHashes?: Map<string, string> }
const hashes = (g.__depgraphHashes ??= new Map<string, string>())

export function plansDir(): string {
  return process.env.PLANS_DIR ? path.resolve(process.env.PLANS_DIR) : path.join(process.cwd(), 'plans')
}

export function hashOf(text: string): string {
  return createHash('sha1').update(text).digest('hex')
}

export function lastWrittenHash(slug: string): string | undefined {
  return hashes.get(slug)
}

function assertSlug(slug: string): void {
  if (!ID_RE.test(slug)) throw new Error(`invalid slug "${slug}"`)
}

const fileFor = (slug: string, dir: string) => path.join(dir, `${slug}.json`)

export async function readPlan(slug: string, dir = plansDir()): Promise<Plan | null> {
  assertSlug(slug)
  try {
    return JSON.parse(await readFile(fileFor(slug, dir), 'utf8')) as Plan
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === 'ENOENT') return null
    throw e
  }
}

export async function writePlan(slug: string, plan: Plan, dir = plansDir()): Promise<Plan> {
  assertSlug(slug)
  const errors = validatePlan(plan)
  if (errors.length) throw new Error(errors.join('; '))
  const text = serializePlan(plan)
  await mkdir(dir, { recursive: true })
  const target = fileFor(slug, dir)
  const tmp = `${target}.tmp`
  await writeFile(tmp, text, 'utf8')
  hashes.set(slug, hashOf(text))
  await rename(tmp, target)
  return JSON.parse(text) as Plan
}

export async function listPlans(dir = plansDir()): Promise<PlanSummary[]> {
  let files: string[]
  try {
    files = await readdir(dir)
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === 'ENOENT') return []
    throw e
  }
  const slugs = files.filter(f => f.endsWith('.json')).map(f => f.slice(0, -5)).filter(s => ID_RE.test(s)).sort()
  const out: PlanSummary[] = []
  for (const slug of slugs) {
    const plan = await readPlan(slug, dir)
    if (plan) out.push({ slug, name: plan.name, nodeCount: plan.nodes.length })
  }
  return out
}

export async function createPlan(name: string, dir = plansDir()): Promise<{ slug: string; plan: Plan }> {
  const slug = slugify(name)
  if (await readPlan(slug, dir)) throw new PlanExistsError(`plan "${slug}" already exists`)
  const plan = await writePlan(slug, { name, nodes: [] }, dir)
  return { slug, plan }
}
```

- [ ] **Step 4: Run tests**

Run: `npm test`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/lib/store.ts src/lib/store.test.ts
git commit -m "depgraph: file store with atomic writes and last-write hash

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: REST route handlers

**Files:**
- Create: `depgraph/src/app/api/plans/route.ts`, `depgraph/src/app/api/plans/[slug]/route.ts`
- Create: `depgraph/src/app/api/plans/route.test.ts`, `depgraph/src/app/api/plans/slug.test.ts`

**Interfaces:**
- Consumes: `listPlans, readPlan, writePlan, createPlan, PlanExistsError` from `@/lib/store`; `validatePlan` from `@/lib/schema`.
- Produces HTTP:
  - `GET /api/plans` -> 200 `PlanSummary[]`
  - `POST /api/plans` `{name}` -> 201 `{slug, plan}`; 400 `{errors}` if name missing; 409 `{errors}` if exists
  - `GET /api/plans/[slug]` -> 200 `Plan`; 404 `{errors:["not found"]}`; 400 on bad slug
  - `PUT /api/plans/[slug]` body `Plan` -> 200 normalized `Plan`; 400 `{errors: string[]}`
- Next 16 route context: second arg is `{ params: Promise<{ slug: string }> }`.

- [ ] **Step 1: Write failing tests**

Create `depgraph/src/app/api/plans/route.test.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtemp, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { GET, POST } from './route'

let dir: string
beforeEach(async () => {
  dir = await mkdtemp(path.join(tmpdir(), 'depgraph-api-'))
  process.env.PLANS_DIR = dir
})
afterEach(async () => {
  delete process.env.PLANS_DIR
  await rm(dir, { recursive: true, force: true })
})

const post = (body: unknown) =>
  POST(new Request('http://x/api/plans', { method: 'POST', body: JSON.stringify(body), headers: { 'content-type': 'application/json' } }))

describe('/api/plans', () => {
  it('lists nothing initially', async () => {
    const res = await GET()
    expect(res.status).toBe(200)
    expect(await res.json()).toEqual([])
  })
  it('creates then lists', async () => {
    const created = await post({ name: 'New Plan' })
    expect(created.status).toBe(201)
    expect(await created.json()).toEqual({ slug: 'new-plan', plan: { name: 'New Plan', nodes: [] } })
    expect(await (await GET()).json()).toEqual([{ slug: 'new-plan', name: 'New Plan', nodeCount: 0 }])
  })
  it('400 without a name, 409 on duplicate', async () => {
    expect((await post({})).status).toBe(400)
    await post({ name: 'Dup' })
    const dup = await post({ name: 'Dup' })
    expect(dup.status).toBe(409)
    expect(await dup.json()).toEqual({ errors: ['plan "dup" already exists'] })
  })
})
```

Create `depgraph/src/app/api/plans/slug.test.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtemp, readFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { GET, PUT } from './[slug]/route'
import { serializePlan, type Plan } from '@/lib/schema'

let dir: string
beforeEach(async () => {
  dir = await mkdtemp(path.join(tmpdir(), 'depgraph-api-'))
  process.env.PLANS_DIR = dir
})
afterEach(async () => {
  delete process.env.PLANS_DIR
  await rm(dir, { recursive: true, force: true })
})

const ctx = (slug: string) => ({ params: Promise.resolve({ slug }) })
const put = (slug: string, body: unknown) =>
  PUT(new Request(`http://x/api/plans/${slug}`, { method: 'PUT', body: JSON.stringify(body) }), ctx(slug))
const get = (slug: string) => GET(new Request(`http://x/api/plans/${slug}`), ctx(slug))

const plan: Plan = {
  name: 'P',
  nodes: [
    { id: 'b', title: 'B', description: '', status: 'todo', tags: [], depends_on: ['a'] },
    { id: 'a', title: 'A', description: '', status: 'done', tags: [], depends_on: [] },
  ],
}

describe('/api/plans/[slug]', () => {
  it('404 for missing, 400 for bad slug', async () => {
    expect((await get('missing')).status).toBe(404)
    expect((await get('Bad Slug')).status).toBe(400)
  })
  it('PUT writes normalized and GET reads it back', async () => {
    const res = await put('p', plan)
    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.nodes.map((n: { id: string }) => n.id)).toEqual(['a', 'b'])
    expect(await readFile(path.join(dir, 'p.json'), 'utf8')).toBe(serializePlan(plan))
    expect(await (await get('p')).json()).toEqual(body)
  })
  it('PUT 400 with errors on invalid plan and writes nothing', async () => {
    const res = await put('p', { name: 'P', nodes: [{ id: 'a', title: 'A', depends_on: ['a'] }] })
    expect(res.status).toBe(400)
    expect(await res.json()).toEqual({ errors: ['node "a": depends on itself'] })
    expect((await get('p')).status).toBe(404)
  })
  it('PUT 400 on malformed JSON', async () => {
    const res = await PUT(new Request('http://x/api/plans/p', { method: 'PUT', body: '{nope' }), ctx('p'))
    expect(res.status).toBe(400)
    expect(await res.json()).toEqual({ errors: ['body must be valid JSON'] })
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test -- api`
Expected: FAIL, cannot resolve `./route`.

- [ ] **Step 3: Implement**

Create `depgraph/src/app/api/plans/route.ts`:

```ts
import { createPlan, listPlans, PlanExistsError } from '@/lib/store'

export const dynamic = 'force-dynamic'

export async function GET() {
  return Response.json(await listPlans())
}

export async function POST(req: Request) {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return Response.json({ errors: ['body must be valid JSON'] }, { status: 400 })
  }
  const name = (body as { name?: unknown })?.name
  if (typeof name !== 'string' || !name.trim()) {
    return Response.json({ errors: ['name must be a non-empty string'] }, { status: 400 })
  }
  try {
    return Response.json(await createPlan(name.trim()), { status: 201 })
  } catch (e) {
    if (e instanceof PlanExistsError) return Response.json({ errors: [e.message] }, { status: 409 })
    throw e
  }
}
```

Create `depgraph/src/app/api/plans/[slug]/route.ts`:

```ts
import { ID_RE, validatePlan, type Plan } from '@/lib/schema'
import { readPlan, writePlan } from '@/lib/store'

export const dynamic = 'force-dynamic'

type Ctx = { params: Promise<{ slug: string }> }

async function slugOf(ctx: Ctx): Promise<string | Response> {
  const { slug } = await ctx.params
  if (!ID_RE.test(slug)) return Response.json({ errors: [`invalid slug "${slug}"`] }, { status: 400 })
  return slug
}

export async function GET(_req: Request, ctx: Ctx) {
  const slug = await slugOf(ctx)
  if (slug instanceof Response) return slug
  const plan = await readPlan(slug)
  if (!plan) return Response.json({ errors: ['not found'] }, { status: 404 })
  return Response.json(plan)
}

export async function PUT(req: Request, ctx: Ctx) {
  const slug = await slugOf(ctx)
  if (slug instanceof Response) return slug
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return Response.json({ errors: ['body must be valid JSON'] }, { status: 400 })
  }
  const errors = validatePlan(body)
  if (errors.length) return Response.json({ errors }, { status: 400 })
  return Response.json(await writePlan(slug, body as Plan))
}
```

- [ ] **Step 4: Run tests**

Run: `npm test`
Expected: all PASS.

- [ ] **Step 5: Manual check**

Run `npm run dev -- -p 3000` in background, then:

```bash
curl -s http://localhost:3000/api/plans
curl -s http://localhost:3000/api/plans/example | head -c 200
```

Expected: first prints `[{"slug":"example","name":"Example: ship the visualizer","nodeCount":8}]`; second prints the plan JSON. Stop the server.

- [ ] **Step 6: Commit**

```bash
git add src/app/api
git commit -m "depgraph: REST routes for listing, creating, reading, writing plans

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: File watcher and SSE route

**Files:**
- Create: `depgraph/src/lib/watcher.ts`, `depgraph/src/lib/watcher.test.ts`, `depgraph/src/app/api/plans/[slug]/events/route.ts`

**Interfaces:**
- Consumes: `hashOf, lastWrittenHash, plansDir` from `@/lib/store`; `ID_RE` from `@/lib/schema`.
- Produces:
  ```ts
  export type ChangeListener = (slug: string) => void
  export function subscribe(listener: ChangeListener, dir?: string): () => void   // returns unsubscribe
  ```
  and `GET /api/plans/[slug]/events` streaming `event: changed\ndata: {}\n\n` whenever that slug's file changes on disk with content different from the app's own last write. Comment line `: ping` every 15 s.

- [ ] **Step 1: Write failing test**

Create `depgraph/src/lib/watcher.test.ts`:

```ts
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'
import { subscribe } from '@/lib/watcher'
import { writePlan } from '@/lib/store'

let dir: string
beforeEach(async () => { dir = await mkdtemp(path.join(tmpdir(), 'depgraph-watch-')) })
afterEach(async () => { await rm(dir, { recursive: true, force: true }) })

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

describe('subscribe', () => {
  it('notifies on external change but not on own writes', async () => {
    const seen: string[] = []
    const unsub = subscribe(s => seen.push(s), dir)
    await sleep(300) // let chokidar attach
    await writePlan('own', { name: 'own', nodes: [] }, dir)
    await sleep(500)
    expect(seen).toEqual([])
    await writeFile(path.join(dir, 'ext.json'), '{"name":"ext","nodes":[]}\n')
    await writeFile(path.join(dir, 'ignored.txt'), 'x')
    await sleep(800)
    expect(seen).toEqual(['ext'])
    unsub()
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test -- watcher`
Expected: FAIL, cannot resolve `@/lib/watcher`.

- [ ] **Step 3: Implement watcher**

Create `depgraph/src/lib/watcher.ts`:

```ts
import chokidar, { type FSWatcher } from 'chokidar'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { ID_RE } from '@/lib/schema'
import { hashOf, lastWrittenHash, plansDir } from '@/lib/store'

export type ChangeListener = (slug: string) => void

interface Entry { watcher: FSWatcher; listeners: Set<ChangeListener> }
const g = globalThis as unknown as { __depgraphWatchers?: Map<string, Entry> }
const entries = (g.__depgraphWatchers ??= new Map<string, Entry>())

function entryFor(dir: string): Entry {
  const existing = entries.get(dir)
  if (existing) return existing
  const listeners = new Set<ChangeListener>()
  const watcher = chokidar.watch(dir, { ignoreInitial: true, depth: 0 })
  const onEvent = async (file: string) => {
    if (!file.endsWith('.json')) return
    const slug = path.basename(file, '.json')
    if (!ID_RE.test(slug)) return
    let text: string
    try {
      text = await readFile(file, 'utf8')
    } catch {
      return
    }
    if (hashOf(text) === lastWrittenHash(slug)) return
    for (const l of listeners) l(slug)
  }
  watcher.on('add', onEvent).on('change', onEvent)
  const entry = { watcher, listeners }
  entries.set(dir, entry)
  return entry
}

export function subscribe(listener: ChangeListener, dir = plansDir()): () => void {
  const entry = entryFor(path.resolve(dir))
  entry.listeners.add(listener)
  return () => {
    entry.listeners.delete(listener)
  }
}
```

- [ ] **Step 4: Run test**

Run: `npm test -- watcher`
Expected: PASS. If it is flaky on macOS, raise the sleeps to 1000 ms; do not add polling.

- [ ] **Step 5: SSE route**

Create `depgraph/src/app/api/plans/[slug]/events/route.ts`:

```ts
import { ID_RE } from '@/lib/schema'
import { subscribe } from '@/lib/watcher'

export const dynamic = 'force-dynamic'

export async function GET(_req: Request, ctx: { params: Promise<{ slug: string }> }) {
  const { slug } = await ctx.params
  if (!ID_RE.test(slug)) return Response.json({ errors: [`invalid slug "${slug}"`] }, { status: 400 })
  const encoder = new TextEncoder()
  let unsubscribe = () => {}
  let ping: ReturnType<typeof setInterval> | undefined
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const send = (s: string) => {
        try {
          controller.enqueue(encoder.encode(s))
        } catch {
          /* closed */
        }
      }
      send(': connected\n\n')
      unsubscribe = subscribe(changed => {
        if (changed === slug) send('event: changed\ndata: {}\n\n')
      })
      ping = setInterval(() => send(': ping\n\n'), 15000)
    },
    cancel() {
      unsubscribe()
      if (ping) clearInterval(ping)
    },
  })
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  })
}
```

- [ ] **Step 6: Manual check**

Run `npm run dev -- -p 3000` in background. In another shell:

```bash
curl -N http://localhost:3000/api/plans/example/events &
sleep 1; echo "" >> plans/example.json; sleep 1; kill %1
```

Expected: curl prints `: connected` then `event: changed`. Then `git checkout plans/example.json` to restore. Stop the server.

- [ ] **Step 7: Commit**

```bash
git add src/lib/watcher.ts src/lib/watcher.test.ts src/app/api/plans/[slug]/events
git commit -m "depgraph: chokidar watcher and SSE change events

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Pure mutations and graph data mapping

**Files:**
- Create: `depgraph/src/lib/mutations.ts`, `depgraph/src/lib/mutations.test.ts`, `depgraph/src/lib/graphData.ts`, `depgraph/src/lib/graphData.test.ts`

**Interfaces:**
- Consumes: `Plan, PlanNode, Status, uniqueId, slugify` from `@/lib/schema`.
- Produces:
  ```ts
  // mutations.ts — all return a NEW plan, never mutate; never validate (caller does)
  export function addNode(plan: Plan, title?: string): { plan: Plan; id: string }   // title default 'Untitled'; id = uniqueId(slugify(title))
  export function updateNode(plan: Plan, id: string, patch: Partial<Omit<PlanNode,'id'>>): Plan
  export function deleteNode(plan: Plan, id: string): Plan                          // strips id from every depends_on
  export function addDependency(plan: Plan, dependencyId: string, dependentId: string): Plan   // adds dependencyId to dependent.depends_on (idempotent)
  export function removeDependency(plan: Plan, dependencyId: string, dependentId: string): Plan

  // graphData.ts
  export interface GraphNode { id: string; title: string; status: Status; x?: number; y?: number; z?: number }
  export interface GraphLink { source: string; target: string }   // source = dependency, target = dependent
  export interface GraphData { nodes: GraphNode[]; links: GraphLink[] }
  export function toGraphData(plan: Plan, cache: Map<string, GraphNode>): GraphData
  // Reuses objects from cache by id (so force-graph keeps x/y/z), updates title/status in place, drops stale entries.
  ```

- [ ] **Step 1: Write failing tests**

Create `depgraph/src/lib/mutations.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan } from '@/lib/schema'

const base: Plan = {
  name: 'p',
  nodes: [
    { id: 'a', title: 'A', description: '', status: 'todo', tags: [], depends_on: [] },
    { id: 'b', title: 'B', description: '', status: 'todo', tags: [], depends_on: ['a'] },
  ],
}

describe('addNode', () => {
  it('adds an untitled node with a unique slug id', () => {
    const { plan, id } = addNode(base)
    expect(id).toBe('untitled')
    expect(plan.nodes).toHaveLength(3)
    expect(plan.nodes[2]).toEqual({ id: 'untitled', title: 'Untitled', description: '', status: 'todo', tags: [], depends_on: [] })
    expect(addNode(plan).id).toBe('untitled-2')
    expect(base.nodes).toHaveLength(2)
  })
  it('slugifies a given title', () => {
    expect(addNode(base, 'Ship It!').id).toBe('ship-it')
  })
})

describe('updateNode', () => {
  it('patches fields without touching id', () => {
    const plan = updateNode(base, 'a', { title: 'AA', status: 'done', tags: ['x'] })
    expect(plan.nodes[0]).toEqual({ id: 'a', title: 'AA', description: '', status: 'done', tags: ['x'], depends_on: [] })
    expect(base.nodes[0].title).toBe('A')
  })
})

describe('deleteNode', () => {
  it('removes the node and references to it', () => {
    const plan = deleteNode(base, 'a')
    expect(plan.nodes.map(n => n.id)).toEqual(['b'])
    expect(plan.nodes[0].depends_on).toEqual([])
  })
})

describe('addDependency / removeDependency', () => {
  it('adds idempotently and removes', () => {
    const p1 = addDependency(base, 'b', 'a')
    expect(p1.nodes[0].depends_on).toEqual(['b'])
    expect(addDependency(p1, 'b', 'a').nodes[0].depends_on).toEqual(['b'])
    expect(removeDependency(p1, 'b', 'a').nodes[0].depends_on).toEqual([])
  })
})
```

Create `depgraph/src/lib/graphData.test.ts`:

```ts
import { describe, expect, it } from 'vitest'
import { toGraphData, type GraphNode } from '@/lib/graphData'
import type { Plan } from '@/lib/schema'

const plan: Plan = {
  name: 'p',
  nodes: [
    { id: 'a', title: 'A', description: '', status: 'done', tags: [], depends_on: [] },
    { id: 'b', title: 'B', description: '', status: 'todo', tags: [], depends_on: ['a'] },
  ],
}

describe('toGraphData', () => {
  it('maps nodes and derives links dependency->dependent', () => {
    const data = toGraphData(plan, new Map())
    expect(data.nodes).toEqual([{ id: 'a', title: 'A', status: 'done' }, { id: 'b', title: 'B', status: 'todo' }])
    expect(data.links).toEqual([{ source: 'a', target: 'b' }])
  })
  it('reuses cached node objects and updates them in place', () => {
    const cache = new Map<string, GraphNode>()
    const first = toGraphData(plan, cache)
    first.nodes[0].x = 42
    const updated: Plan = { ...plan, nodes: [{ ...plan.nodes[0], title: 'A2' }] }
    const second = toGraphData(updated, cache)
    expect(second.nodes[0]).toBe(first.nodes[0])
    expect(second.nodes[0].x).toBe(42)
    expect(second.nodes[0].title).toBe('A2')
    expect(cache.has('b')).toBe(false)
  })
})
```

- [ ] **Step 2: Run to verify failure**

Run: `npm test -- mutations graphData`
Expected: FAIL, modules not found.

- [ ] **Step 3: Implement**

Create `depgraph/src/lib/mutations.ts`:

```ts
import { slugify, uniqueId, type Plan, type PlanNode } from '@/lib/schema'

export function addNode(plan: Plan, title = 'Untitled'): { plan: Plan; id: string } {
  const id = uniqueId(slugify(title), plan.nodes.map(n => n.id))
  const node: PlanNode = { id, title, description: '', status: 'todo', tags: [], depends_on: [] }
  return { plan: { ...plan, nodes: [...plan.nodes, node] }, id }
}

export function updateNode(plan: Plan, id: string, patch: Partial<Omit<PlanNode, 'id'>>): Plan {
  return { ...plan, nodes: plan.nodes.map(n => (n.id === id ? { ...n, ...patch, id } : n)) }
}

export function deleteNode(plan: Plan, id: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.filter(n => n.id !== id).map(n => ({ ...n, depends_on: n.depends_on.filter(d => d !== id) })),
  }
}

export function addDependency(plan: Plan, dependencyId: string, dependentId: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.map(n =>
      n.id === dependentId && !n.depends_on.includes(dependencyId)
        ? { ...n, depends_on: [...n.depends_on, dependencyId] }
        : n,
    ),
  }
}

export function removeDependency(plan: Plan, dependencyId: string, dependentId: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.map(n =>
      n.id === dependentId ? { ...n, depends_on: n.depends_on.filter(d => d !== dependencyId) } : n,
    ),
  }
}
```

Create `depgraph/src/lib/graphData.ts`:

```ts
import type { Plan, Status } from '@/lib/schema'

export interface GraphNode { id: string; title: string; status: Status; x?: number; y?: number; z?: number }
export interface GraphLink { source: string; target: string }
export interface GraphData { nodes: GraphNode[]; links: GraphLink[] }

export function toGraphData(plan: Plan, cache: Map<string, GraphNode>): GraphData {
  const ids = new Set(plan.nodes.map(n => n.id))
  for (const id of [...cache.keys()]) if (!ids.has(id)) cache.delete(id)
  const nodes = plan.nodes.map(n => {
    const existing = cache.get(n.id)
    if (existing) {
      existing.title = n.title
      existing.status = n.status
      return existing
    }
    const fresh: GraphNode = { id: n.id, title: n.title, status: n.status }
    cache.set(n.id, fresh)
    return fresh
  })
  const links: GraphLink[] = []
  for (const n of plan.nodes) for (const d of n.depends_on) links.push({ source: d, target: n.id })
  return { nodes, links }
}
```

- [ ] **Step 4: Run tests**

Run: `npm test`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add src/lib/mutations.ts src/lib/mutations.test.ts src/lib/graphData.ts src/lib/graphData.test.ts
git commit -m "depgraph: pure plan mutations and force-graph data mapping

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Client state hook and 3D graph page

**Files:**
- Create: `depgraph/src/hooks/usePlan.ts`, `depgraph/src/components/Graph.tsx`, `depgraph/src/components/SaveIndicator.tsx`
- Modify: `depgraph/src/app/page.tsx` (replace), `depgraph/src/app/layout.tsx` (replace), `depgraph/src/app/globals.css` (replace)

**Interfaces:**
- Consumes: `Plan, validatePlan` from `@/lib/schema`; `toGraphData, GraphNode, GraphLink` from `@/lib/graphData`; API routes from Task 4/5.
- Produces:
  ```ts
  // usePlan.ts
  export type SaveState = 'idle' | 'saving' | 'saved' | 'error'
  export function usePlan(slug: string | null): {
    plan: Plan | null
    loadError: string | null
    saveState: SaveState
    saveError: string | null
    apply: (mutate: (plan: Plan) => Plan) => string[]   // validates; [] = applied and save scheduled; else errors, nothing applied
    reload: () => Promise<void>
  }
  // Graph.tsx (default export, client only)
  interface GraphProps {
    plan: Plan
    selectedId: string | null
    onSelect: (id: string | null) => void          // null on background click
    onLinkRightClick: (dependencyId: string, dependentId: string) => void
  }
  ```
  Status colors exported from `Graph.tsx`: `STATUS_COLORS: Record<Status, string>` = todo `#8b95a7`, doing `#5ac8fa`, done `#3a4152`, blocked `#ff6b6b`.

- [ ] **Step 1: usePlan hook**

Create `depgraph/src/hooks/usePlan.ts`:

```ts
'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import { validatePlan, type Plan } from '@/lib/schema'

export type SaveState = 'idle' | 'saving' | 'saved' | 'error'

const DEBOUNCE_MS = 300

export function usePlan(slug: string | null) {
  const [plan, setPlan] = useState<Plan | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)
  const planRef = useRef<Plan | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const dirty = useRef(false)

  const reload = useCallback(async () => {
    if (!slug) return
    if (dirty.current) return // local edits pending; they will overwrite the file anyway
    try {
      const res = await fetch(`/api/plans/${slug}`, { cache: 'no-store' })
      if (!res.ok) throw new Error((await res.json()).errors?.join('; ') ?? res.statusText)
      const next = (await res.json()) as Plan
      planRef.current = next
      setPlan(next)
      setLoadError(null)
    } catch (e) {
      setLoadError((e as Error).message)
    }
  }, [slug])

  const flush = useCallback(async () => {
    if (!slug || !planRef.current) return
    dirty.current = false
    setSaveState('saving')
    try {
      const res = await fetch(`/api/plans/${slug}`, {
        method: 'PUT',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(planRef.current),
      })
      if (!res.ok) throw new Error(((await res.json()).errors as string[]).join('; '))
      setSaveState('saved')
      setSaveError(null)
    } catch (e) {
      setSaveState('error')
      setSaveError((e as Error).message)
    }
  }, [slug])

  const apply = useCallback(
    (mutate: (plan: Plan) => Plan): string[] => {
      if (!planRef.current) return ['no plan loaded']
      const next = mutate(planRef.current)
      const errors = validatePlan(next)
      if (errors.length) return errors
      planRef.current = next
      setPlan(next)
      dirty.current = true
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(flush, DEBOUNCE_MS)
      return []
    },
    [flush],
  )

  useEffect(() => {
    planRef.current = null
    setPlan(null)
    setSaveState('idle')
    setSaveError(null)
    dirty.current = false
    void reload()
    if (!slug) return
    const es = new EventSource(`/api/plans/${slug}/events`)
    es.addEventListener('changed', () => void reload())
    return () => es.close()
  }, [slug, reload])

  return { plan, loadError, saveState, saveError, apply, reload }
}
```

- [ ] **Step 2: Graph component**

Create `depgraph/src/components/Graph.tsx`:

```tsx
'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph3D, { type ForceGraphMethods } from 'react-force-graph-3d'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
import type { Plan, Status } from '@/lib/schema'

export const STATUS_COLORS: Record<Status, string> = {
  todo: '#8b95a7',
  doing: '#5ac8fa',
  done: '#3a4152',
  blocked: '#ff6b6b',
}

interface GraphProps {
  plan: Plan
  selectedId: string | null
  onSelect: (id: string | null) => void
  onLinkRightClick: (dependencyId: string, dependentId: string) => void
}

const idOf = (end: unknown) => (typeof end === 'string' ? end : (end as GraphNode).id)

export default function Graph({ plan, selectedId, onSelect, onLinkRightClick }: GraphProps) {
  const cache = useRef(new Map<string, GraphNode>())
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined)
  const [size, setSize] = useState({ w: 800, h: 600 })

  useEffect(() => {
    const update = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])

  const structureKey = plan.nodes.map(n => `${n.id}:${n.status}:${n.title}:${n.depends_on.join(',')}`).join('|')
  const data = useMemo(() => toGraphData(plan, cache.current), [structureKey]) // eslint-disable-line react-hooks/exhaustive-deps

  const neighbors = useMemo(() => {
    const set = new Set<string>()
    if (!selectedId) return set
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId) set.add(idOf(l.target))
      if (l.target === selectedId || idOf(l.target) === selectedId) set.add(idOf(l.source))
    }
    return set
  }, [data, selectedId])

  const nodeColor = (n: GraphNode) => {
    const base = STATUS_COLORS[n.status]
    if (!selectedId || n.id === selectedId || neighbors.has(n.id)) return base
    return base + '33'
  }

  return (
    <ForceGraph3D<GraphNode, GraphLink>
      ref={fgRef}
      width={size.w}
      height={size.h}
      graphData={data}
      backgroundColor="#05060a"
      nodeLabel={(n: GraphNode) => `${n.title} · ${n.status}`}
      nodeColor={nodeColor}
      nodeRelSize={6}
      nodeOpacity={1}
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
  )
}
```

Note: `react-force-graph-3d` mutates link `source`/`target` from id strings into node objects after the first render; `idOf` handles both shapes.

- [ ] **Step 3: SaveIndicator**

Create `depgraph/src/components/SaveIndicator.tsx`:

```tsx
'use client'
import type { SaveState } from '@/hooks/usePlan'

const LABEL: Record<SaveState, string> = { idle: '', saving: 'saving…', saved: 'saved', error: 'save failed' }

export default function SaveIndicator({ state, error }: { state: SaveState; error: string | null }) {
  if (state === 'idle') return null
  return (
    <div
      data-testid="save-indicator"
      data-state={state}
      className={`fixed bottom-4 right-4 rounded-md border px-3 py-1.5 font-mono text-xs backdrop-blur ${
        state === 'error' ? 'border-red-400/40 bg-red-950/40 text-red-200' : 'border-white/10 bg-white/5 text-white/60'
      }`}
    >
      {LABEL[state]}
      {state === 'error' && error ? `: ${error}` : ''}
    </div>
  )
}
```

- [ ] **Step 4: Page and layout**

Replace `depgraph/src/app/layout.tsx`:

```tsx
import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = { title: 'depgraph', description: 'Plans as dependency graphs' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="h-screen w-screen overflow-hidden bg-[#05060a] text-white antialiased">{children}</body>
    </html>
  )
}
```

Replace `depgraph/src/app/globals.css`:

```css
@import "tailwindcss";

:root { color-scheme: dark; }
body { margin: 0; }
```

Replace `depgraph/src/app/page.tsx`:

```tsx
'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import SaveIndicator from '@/components/SaveIndicator'
import { usePlan } from '@/hooks/usePlan'
import { removeDependency } from '@/lib/mutations'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  useEffect(() => {
    if (plan && selectedId && !plan.nodes.some(n => n.id === selectedId)) setSelectedId(null)
  }, [plan, selectedId])

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onLinkRightClick={(dep, dependent) => apply(p => removeDependency(p, dep, dependent))}
      />
      <div className="pointer-events-none fixed left-4 top-4 font-mono text-xs text-white/60">
        {plan.name} · <span data-testid="node-count">{plan.nodes.length} nodes</span>
        {selectedId ? ` · selected ${selectedId}` : ''}
      </div>
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

- [ ] **Step 5: Type-check and run**

Run: `npx tsc --noEmit`
Expected: no errors. If `ForceGraph3D` generic props complain, drop the explicit `<GraphNode, GraphLink>` type arguments on the JSX element and keep the callback parameter annotations.

Run `npm run dev -- -p 3000`, open http://localhost:3000 in the browser pane.
Expected: dark scene, 8 colored spheres with arrows, hover shows label, click a node shows `selected <id>` top-left, click background clears it. Right-click the arrow between `schema` and `store`: the arrow disappears, indicator shows `saved`, and `plans/example.json` no longer lists `schema` under `store`. Restore with `git checkout plans/example.json` and confirm the browser refreshes the arrow back within ~1 s.

- [ ] **Step 6: Commit**

```bash
git add src/hooks src/components src/app/page.tsx src/app/layout.tsx src/app/globals.css
git commit -m "depgraph: client plan state, 3D force graph, live reload

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: Toolbar, node panel, link mode, toasts

**Files:**
- Create: `depgraph/src/components/Toolbar.tsx`, `depgraph/src/components/NodePanel.tsx`, `depgraph/src/components/Toast.tsx`
- Modify: `depgraph/src/app/page.tsx`, `depgraph/src/components/Graph.tsx`

**Interfaces:**
- Consumes: `addNode, updateNode, deleteNode, addDependency` from `@/lib/mutations`; `usePlan().apply`; `PlanSummary`.
- Produces:
  ```ts
  // Toolbar.tsx
  interface ToolbarProps {
    plans: PlanSummary[]; slug: string; planName: string; nodeCount: number
    linkMode: boolean; onToggleLinkMode: () => void
    onAddNode: () => void; onNewPlan: () => void
  }
  // NodePanel.tsx
  interface NodePanelProps { plan: Plan; nodeId: string; onChange: (patch: Partial<Omit<PlanNode,'id'>>) => string[]; onDelete: () => void; onClose: () => void }
  // Toast.tsx
  export function useToast(): { message: string | null; show: (m: string) => void }
  export default function Toast({ message }: { message: string | null })
  // Graph.tsx gains prop: linkMode: boolean  (cursor crosshair; node click semantics stay in page)
  ```

- [ ] **Step 1: Toast**

Create `depgraph/src/components/Toast.tsx`:

```tsx
'use client'
import { useCallback, useRef, useState } from 'react'

export function useToast() {
  const [message, setMessage] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const show = useCallback((m: string) => {
    setMessage(m)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setMessage(null), 3500)
  }, [])
  return { message, show }
}

export default function Toast({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <div
      role="status"
      className="fixed bottom-4 left-1/2 -translate-x-1/2 rounded-md border border-amber-400/40 bg-amber-950/60 px-4 py-2 font-mono text-xs text-amber-100 backdrop-blur"
    >
      {message}
    </div>
  )
}
```

- [ ] **Step 2: Toolbar**

Create `depgraph/src/components/Toolbar.tsx`:

```tsx
'use client'
import { useRouter } from 'next/navigation'
import type { PlanSummary } from '@/lib/store'

interface ToolbarProps {
  plans: PlanSummary[]
  slug: string
  planName: string
  nodeCount: number
  linkMode: boolean
  onToggleLinkMode: () => void
  onAddNode: () => void
  onNewPlan: () => void
}

const btn = 'rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-xs hover:bg-white/10'

export default function Toolbar(p: ToolbarProps) {
  const router = useRouter()
  return (
    <div className="fixed left-4 top-4 flex items-center gap-2 rounded-lg border border-white/10 bg-black/40 p-2 backdrop-blur">
      <select
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
      <button className={btn} onClick={p.onNewPlan}>New plan</button>
      <button className={btn} onClick={p.onAddNode}>Add node</button>
      <button className={`${btn} ${p.linkMode ? 'border-sky-400/60 bg-sky-500/20' : ''}`} aria-pressed={p.linkMode} onClick={p.onToggleLinkMode}>
        Link mode
      </button>
      <span className="ml-2 font-mono text-xs text-white/50">
        <span data-testid="node-count">{p.nodeCount} nodes</span>
      </span>
    </div>
  )
}
```

- [ ] **Step 3: NodePanel**

Create `depgraph/src/components/NodePanel.tsx`:

```tsx
'use client'
import { useEffect, useRef, useState } from 'react'
import { STATUSES, type Plan, type PlanNode, type Status } from '@/lib/schema'

interface NodePanelProps {
  plan: Plan
  nodeId: string
  onChange: (patch: Partial<Omit<PlanNode, 'id'>>) => string[]
  onDelete: () => void
  onClose: () => void
}

const field = 'w-full rounded-md border border-white/10 bg-white/5 px-2 py-1.5 text-sm outline-none focus:border-sky-400/60'

export default function NodePanel({ plan, nodeId, onChange, onDelete, onClose }: NodePanelProps) {
  const node = plan.nodes.find(n => n.id === nodeId)
  const [filter, setFilter] = useState('')
  const [tagDraft, setTagDraft] = useState('')
  const [error, setError] = useState<string | null>(null)
  const titleRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (node?.title === 'Untitled') titleRef.current?.select()
  }, [nodeId]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!node) return null

  const change = (patch: Partial<Omit<PlanNode, 'id'>>) => {
    const errors = onChange(patch)
    setError(errors.length ? errors.join('; ') : null)
  }

  const others = plan.nodes.filter(n => n.id !== nodeId && (n.title + n.id).toLowerCase().includes(filter.toLowerCase()))

  return (
    <aside
      data-testid="node-panel"
      className="fixed right-4 top-4 bottom-4 flex w-80 flex-col gap-3 overflow-y-auto rounded-lg border border-white/10 bg-black/50 p-4 backdrop-blur"
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-white/50">{node.id}</span>
        <button className="text-xs text-white/50 hover:text-white" onClick={onClose} aria-label="Close panel">✕</button>
      </div>

      <label className="text-xs text-white/60">
        Title
        <input ref={titleRef} aria-label="Title" className={field} value={node.title} onChange={e => change({ title: e.target.value })} />
      </label>

      <label className="text-xs text-white/60">
        Description
        <textarea aria-label="Description" className={`${field} min-h-24`} value={node.description} onChange={e => change({ description: e.target.value })} />
      </label>

      <div className="text-xs text-white/60">
        Status
        <div className="mt-1 grid grid-cols-4 gap-1" role="radiogroup" aria-label="Status">
          {STATUSES.map(s => (
            <button
              key={s}
              role="radio"
              aria-checked={node.status === s}
              className={`rounded-md border px-1 py-1 text-xs ${node.status === s ? 'border-sky-400/60 bg-sky-500/20' : 'border-white/10 bg-white/5'}`}
              onClick={() => change({ status: s as Status })}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="text-xs text-white/60">
        Tags
        <div className="mt-1 flex flex-wrap gap-1">
          {node.tags.map(t => (
            <button key={t} className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs" onClick={() => change({ tags: node.tags.filter(x => x !== t) })} title="Remove tag">
              {t} ✕
            </button>
          ))}
        </div>
        <input
          aria-label="Add tag"
          className={`${field} mt-1`}
          placeholder="add tag, press Enter"
          value={tagDraft}
          onChange={e => setTagDraft(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && tagDraft.trim()) {
              if (!node.tags.includes(tagDraft.trim())) change({ tags: [...node.tags, tagDraft.trim()] })
              setTagDraft('')
            }
          }}
        />
      </div>

      <div className="text-xs text-white/60">
        Depends on
        <input aria-label="Filter dependencies" className={`${field} mt-1`} placeholder="filter…" value={filter} onChange={e => setFilter(e.target.value)} />
        <ul className="mt-1 max-h-48 overflow-y-auto">
          {others.map(o => (
            <li key={o.id}>
              <label className="flex cursor-pointer items-center gap-2 py-0.5">
                <input
                  type="checkbox"
                  checked={node.depends_on.includes(o.id)}
                  onChange={e =>
                    change({ depends_on: e.target.checked ? [...node.depends_on, o.id] : node.depends_on.filter(d => d !== o.id) })
                  }
                />
                <span className="truncate">{o.title}</span>
                <span className="font-mono text-white/40">{o.id}</span>
              </label>
            </li>
          ))}
        </ul>
      </div>

      {error && <div role="alert" className="rounded-md border border-red-400/40 bg-red-950/40 p-2 text-xs text-red-200">{error}</div>}

      <button
        className="mt-auto rounded-md border border-red-400/30 bg-red-950/30 px-2 py-1.5 text-xs text-red-200 hover:bg-red-950/60"
        onClick={() => {
          if (window.confirm(`Delete "${node.title}"?`)) onDelete()
        }}
      >
        Delete node
      </button>
    </aside>
  )
}
```

- [ ] **Step 4: Graph link-mode cursor**

In `depgraph/src/components/Graph.tsx`, add `linkMode: boolean` to `GraphProps`, destructure it, and wrap the `ForceGraph3D` in:

```tsx
<div style={{ cursor: linkMode ? 'crosshair' : 'default' }}>
  ...ForceGraph3D...
</div>
```

- [ ] **Step 5: Wire the page**

Replace the `Workspace` body in `depgraph/src/app/page.tsx` so the returned JSX and handlers become:

```tsx
import Toolbar from '@/components/Toolbar'
import NodePanel from '@/components/NodePanel'
import Toast, { useToast } from '@/components/Toast'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
// ...inside Workspace, after usePlan:
const [linkMode, setLinkMode] = useState(false)
const [linkSource, setLinkSource] = useState<string | null>(null)
const toast = useToast()

const report = (errors: string[]) => { if (errors.length) toast.show(errors.join('; ')) }

const handleSelect = (id: string | null) => {
  if (!linkMode || !id) { setSelectedId(id); setLinkSource(null); return }
  if (!linkSource) { setLinkSource(id); toast.show(`link: ${id} → click the node that depends on it`); return }
  if (linkSource === id) { setLinkSource(null); return }
  report(apply(p => addDependency(p, linkSource, id)))
  setLinkSource(null)
}

const handleAddNode = () => {
  let newId = ''
  report(apply(p => { const r = addNode(p); newId = r.id; return r.plan }))
  if (newId) setSelectedId(newId)
}

const handleNewPlan = async () => {
  const name = window.prompt('Plan name')
  if (!name) return
  const res = await fetch('/api/plans', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ name }) })
  const body = await res.json()
  if (!res.ok) { toast.show((body.errors as string[]).join('; ')); return }
  router.push(`/?plan=${body.slug}`)
}

// JSX:
return (
  <>
    <Graph plan={plan} selectedId={linkSource ?? selectedId} linkMode={linkMode} onSelect={handleSelect}
      onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))} />
    <Toolbar plans={plans} slug={slug} planName={plan.name} nodeCount={plan.nodes.length}
      linkMode={linkMode} onToggleLinkMode={() => { setLinkMode(v => !v); setLinkSource(null) }}
      onAddNode={handleAddNode} onNewPlan={handleNewPlan} />
    {selectedId && !linkMode && (
      <NodePanel plan={plan} nodeId={selectedId}
        onChange={patch => apply(p => updateNode(p, selectedId, patch))}
        onDelete={() => { report(apply(p => deleteNode(p, selectedId))); setSelectedId(null) }}
        onClose={() => setSelectedId(null)} />
    )}
    <Toast message={toast.message} />
    <SaveIndicator state={saveState} error={saveError} />
  </>
)
```

Remove the old top-left `<div>` with the plan name (the Toolbar now owns `node-count`). Keep the `Empty`, `Suspense`, plan-list effect, and stale-selection effect from Task 7.

- [ ] **Step 6: Type-check and manual check**

Run: `npx tsc --noEmit` — expected no errors. Run `npm run dev -- -p 3000` and in the browser pane verify:
1. Add node: a new sphere appears, panel opens with title selected; type a title, status `saved` appears; `plans/example.json` contains the new node with a slug id `untitled` (id stays `untitled` even after the title changes, by design).
2. Panel: change status to `blocked`, sphere turns red. Add a tag, remove it. Check a dependency checkbox, arrow appears.
3. Cycle: on node `schema`, check `api-routes` as a dependency. Expected: the checkbox does not stick and the panel shows `cycle: ...` in red.
4. Link mode: toggle, click `design-spec` then `e2e`; arrow from design-spec to e2e appears. Toggle off.
5. Delete: delete the new node; it disappears and no `depends_on` references remain in the file.
6. New plan: creates `plans/<slug>.json` and navigates to it (empty scene, toolbar shows `0 nodes`).

- [ ] **Step 7: Commit**

```bash
git add src/components src/app/page.tsx
git commit -m "depgraph: toolbar, node edit panel, link mode, toasts

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: Visual polish (frontend-design) and Playwright smoke test

**Files:**
- Modify: `depgraph/src/components/Graph.tsx`, `depgraph/src/app/globals.css`, `depgraph/src/app/layout.tsx`, `depgraph/src/components/Toolbar.tsx`, `depgraph/src/components/NodePanel.tsx`
- Create: `depgraph/playwright.config.ts`, `depgraph/e2e/smoke.spec.ts`, `depgraph/README.md`

**Interfaces:**
- Consumes everything above. No new exports. Behaviour and `data-testid`s (`node-count`, `node-panel`, `save-indicator`) must stay.

- [ ] **Step 1: Invoke the frontend-design skill**

Invoke `frontend-design:frontend-design` and apply it to: emissive glowing spheres per status, slow pulse on `blocked`, exponential fog, a humanist sans for titles (load one Google Font in `layout.tsx` via `next/font/google`, e.g. `Inter` for body and keep monospace for ids), and glass overlays. Concretely in `Graph.tsx`:

```tsx
import * as THREE from 'three'
// inside component:
const blocked = useRef(new Set<THREE.Mesh>())
useEffect(() => {
  let raf = 0
  const tick = (t: number) => {
    for (const m of blocked.current) (m.material as THREE.MeshStandardMaterial).emissiveIntensity = 0.55 + 0.45 * Math.sin(t / 400)
    raf = requestAnimationFrame(tick)
  }
  raf = requestAnimationFrame(tick)
  return () => cancelAnimationFrame(raf)
}, [])
useEffect(() => {
  const fg = fgRef.current
  if (fg) fg.scene().fog = new THREE.FogExp2(0x05060a, 0.002)
}, [])
// prop:
nodeThreeObject={(n: GraphNode) => {
  const dim = !!selectedId && n.id !== selectedId && !neighbors.has(n.id)
  const color = new THREE.Color(STATUS_COLORS[n.status])
  const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: n.status === 'done' ? 0.15 : 0.7, transparent: true, opacity: dim ? 0.18 : 1, roughness: 0.4 })
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(n.id === selectedId ? 6.5 : 5, 24, 24), mat)
  if (n.status === 'blocked') blocked.current.add(mesh)
  return mesh
}}
nodeThreeObjectExtend={false}
```

Remove the `nodeColor` prop (the mesh now owns color). Clear `blocked.current` at the top of the `data` memo so stale meshes are dropped.

- [ ] **Step 2: Playwright config**

Create `depgraph/playwright.config.ts`:

```ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: 'e2e',
  timeout: 60000,
  use: { baseURL: 'http://localhost:3123', headless: true },
  webServer: {
    command: 'PLANS_DIR=e2e/plans npm run dev -- -p 3123',
    url: 'http://localhost:3123/api/plans',
    reuseExistingServer: false,
    timeout: 120000,
  },
})
```

Run once: `npx playwright install chromium`.

- [ ] **Step 3: Smoke test**

Create `depgraph/e2e/smoke.spec.ts`:

```ts
import { expect, test } from '@playwright/test'
import { copyFile, mkdir, readFile } from 'node:fs/promises'

test.beforeEach(async () => {
  await mkdir('e2e/plans', { recursive: true })
  await copyFile('plans/example.json', 'e2e/plans/example.json')
})

test('add a node, it persists to the file and survives reload', async ({ page }) => {
  await page.goto('/?plan=example')
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')

  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-panel')).toBeVisible()
  await page.getByLabel('Title').fill('Smoke node')
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')

  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"title": "Smoke node"')
  expect(text).toContain('"id": "untitled"')

  await page.reload()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
})

test('cycle is refused with an error', async ({ page }) => {
  await page.goto('/?plan=example')
  // Select "schema" via the URL-less route: open panel by adding a node, then use dependency list on it.
  await page.getByRole('button', { name: 'Add node' }).click()
  await page.getByLabel('Title').fill('Cycle probe')
  // untitled depends on api-routes; then make api-routes depend on untitled through the file is not possible from UI,
  // so instead: check "api-routes" then confirm no error, then verify a self-referencing edit is impossible by API.
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
```

- [ ] **Step 4: Run e2e**

Run: `npm run test:e2e`
Expected: `2 passed`. If WebGL fails to init in headless Chromium, add `launchOptions: { args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] }` under `use` in the config.

- [ ] **Step 5: README**

Create `depgraph/README.md`:

```markdown
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
```

- [ ] **Step 6: Full verification**

Run: `npm test && npx tsc --noEmit && npm run lint && npm run test:e2e`
Expected: all green.

- [ ] **Step 7: Commit**

```bash
git add -A .
git commit -m "depgraph: visual polish, playwright smoke test, README

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
