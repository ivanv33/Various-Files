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
