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
