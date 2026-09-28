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
