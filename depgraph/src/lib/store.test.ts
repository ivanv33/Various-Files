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
  it('skips files that are not valid JSON', async () => {
    await writePlan('good', plan, dir)
    await writeFile(path.join(dir, 'broken.json'), '{ not json')
    expect((await listPlans(dir)).map(p => p.slug)).toEqual(['good'])
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
