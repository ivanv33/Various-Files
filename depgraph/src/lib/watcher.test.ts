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
