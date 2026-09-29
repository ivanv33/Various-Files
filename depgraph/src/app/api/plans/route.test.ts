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
