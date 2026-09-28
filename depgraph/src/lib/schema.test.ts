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
