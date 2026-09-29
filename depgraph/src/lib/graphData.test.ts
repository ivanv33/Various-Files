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
