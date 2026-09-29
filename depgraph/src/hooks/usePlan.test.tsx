// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, renderHook } from '@testing-library/react'
import { usePlan } from './usePlan'
import type { Plan } from '@/lib/schema'

const basePlan = (name = 'P'): Plan => ({
  name,
  nodes: [
    { id: 'a', title: 'A', description: '', status: 'todo', tags: [], depends_on: [] },
    { id: 'b', title: 'B', description: '', status: 'todo', tags: [], depends_on: ['a'] },
  ],
})

interface FakeCall {
  url: string
  method: string
  body: string | undefined
  respond: (status: number, json: unknown) => Promise<void>
}

let calls: FakeCall[]
let sources: FakeEventSource[]

class FakeEventSource {
  listeners: Record<string, Array<() => void>> = {}
  closed = false
  constructor(public url: string) {
    sources.push(this)
  }
  addEventListener(type: string, fn: () => void) {
    ;(this.listeners[type] ??= []).push(fn)
  }
  close() {
    this.closed = true
  }
  emit(type: string) {
    this.listeners[type]?.forEach((fn) => fn())
  }
}

const gets = (slug: string) => calls.filter((c) => c.method === 'GET' && c.url === `/api/plans/${slug}`)
const puts = (slug?: string) =>
  calls.filter((c) => c.method === 'PUT' && (slug === undefined || c.url === `/api/plans/${slug}`))

const renamed = (title: string) => (p: Plan): Plan => ({
  ...p,
  nodes: p.nodes.map((n) => (n.id === 'a' ? { ...n, title } : n)),
})

beforeEach(() => {
  vi.useFakeTimers()
  calls = []
  sources = []
  vi.stubGlobal('EventSource', FakeEventSource)
  vi.stubGlobal(
    'fetch',
    (url: string, init?: { method?: string; body?: string }) =>
      new Promise((resolve) => {
        calls.push({
          url,
          method: init?.method ?? 'GET',
          body: init?.body,
          respond: async (status, json) => {
            await act(async () => {
              resolve({
                ok: status >= 200 && status < 300,
                status,
                statusText: String(status),
                json: async () => json,
              })
            })
          },
        })
      }),
  )
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

async function mountLoaded(slug = 'alpha') {
  const hook = renderHook(({ s }) => usePlan(s), { initialProps: { s: slug } })
  await gets(slug)[0].respond(200, basePlan())
  return hook
}

describe('usePlan', () => {
  it('apply returns validation errors and leaves plan untouched', async () => {
    const { result } = await mountLoaded()
    const before = result.current.plan
    let errors: string[] = []
    act(() => {
      errors = result.current.apply((p) => ({
        ...p,
        nodes: p.nodes.map((n) => (n.id === 'a' ? { ...n, depends_on: ['b'] } : n)),
      }))
    })
    expect(errors[0]).toMatch(/^cycle:/)
    expect(result.current.plan).toBe(before)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000)
    })
    expect(puts()).toHaveLength(0)
  })

  it('edits within the debounce window coalesce into one PUT', async () => {
    const { result } = await mountLoaded()
    act(() => {
      result.current.apply(renamed('A2'))
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(100)
    })
    act(() => {
      result.current.apply((p) => ({
        ...p,
        nodes: p.nodes.map((n) => (n.id === 'b' ? { ...n, title: 'B2' } : n)),
      }))
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(300)
    })
    expect(puts()).toHaveLength(1)
    const body = JSON.parse(puts()[0].body!)
    expect(body.nodes.map((n: { title: string }) => n.title)).toEqual(['A2', 'B2'])
  })

  it('unmount clears the pending save', async () => {
    const { result, unmount } = await mountLoaded()
    act(() => {
      result.current.apply(renamed('A2'))
    })
    unmount()
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000)
    })
    expect(puts()).toHaveLength(0)
  })

  it('changing slug clears the pending save for the old slug', async () => {
    const { result, rerender } = await mountLoaded('alpha')
    act(() => {
      result.current.apply(renamed('A2'))
    })
    rerender({ s: 'beta' })
    await gets('beta')[0].respond(200, basePlan('Beta'))
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1000)
    })
    expect(puts('alpha')).toHaveLength(0)
  })

  it('a reload response that lands after a local edit does not overwrite it', async () => {
    const { result } = await mountLoaded()
    act(() => {
      sources[0].emit('changed')
    })
    expect(gets('alpha')).toHaveLength(2)
    act(() => {
      result.current.apply(renamed('A2'))
    })
    await gets('alpha')[1].respond(200, basePlan())
    expect(result.current.plan!.nodes[0].title).toBe('A2')
    await act(async () => {
      await vi.advanceTimersByTimeAsync(300)
    })
    expect(puts()).toHaveLength(1)
    expect(puts()[0].body).toContain('A2')
  })

  it('a GET for the previous slug is ignored after switching', async () => {
    const { result, rerender } = renderHook(({ s }) => usePlan(s), { initialProps: { s: 'alpha' } })
    rerender({ s: 'beta' })
    await gets('beta')[0].respond(200, basePlan('Beta'))
    await gets('alpha')[0].respond(200, basePlan('Alpha'))
    expect(result.current.plan!.name).toBe('Beta')
  })

  it('slug change clears loadError', async () => {
    const { result, rerender } = renderHook(({ s }) => usePlan(s), { initialProps: { s: 'alpha' } })
    await gets('alpha')[0].respond(404, { errors: ['not found'] })
    expect(result.current.loadError).toBe('not found')
    rerender({ s: 'beta' })
    expect(result.current.loadError).toBeNull()
  })

  it('a reload that resolves while a PUT is in flight does not overwrite the edit', async () => {
    const { result } = await mountLoaded()
    act(() => {
      sources[0].emit('changed')
    })
    expect(gets('alpha')).toHaveLength(2)
    act(() => {
      result.current.apply(renamed('A2'))
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(300)
    })
    expect(puts()).toHaveLength(1)
    await gets('alpha')[1].respond(200, basePlan())
    expect(result.current.plan!.nodes[0].title).toBe('A2')
  })

  it('a stale GET failure does not set loadError on the new slug', async () => {
    const { result, rerender } = renderHook(({ s }) => usePlan(s), { initialProps: { s: 'alpha' } })
    rerender({ s: 'beta' })
    await gets('beta')[0].respond(200, basePlan('Beta'))
    await gets('alpha')[0].respond(404, { errors: ['not found'] })
    expect(result.current.plan!.name).toBe('Beta')
    expect(result.current.loadError).toBeNull()
  })

  it('an in-flight PUT for the old slug does not report on the new slug', async () => {
    const { result, rerender } = await mountLoaded('alpha')
    act(() => {
      result.current.apply(renamed('A2'))
    })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(300)
    })
    expect(puts('alpha')).toHaveLength(1)
    rerender({ s: 'beta' })
    await gets('beta')[0].respond(200, basePlan('Beta'))
    await puts('alpha')[0].respond(400, { errors: ['boom'] })
    expect(result.current.saveState).toBe('idle')
    expect(result.current.saveError).toBeNull()
  })
})
