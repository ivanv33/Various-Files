import { describe, expect, it } from 'vitest'
import { applyTreeForces, fitOnce, frameFor, rowSpread, TREE } from './treeLayout'

type Force = { strength?: (v: number) => Force; distance?: (v: number) => Force }

function fakeGraph() {
  const calls: Record<string, number> = {}
  const charge = { strength: (v: number) => ((calls.charge = v), charge) }
  const link = { distance: (v: number) => ((calls.link = v), link) }
  const set: Record<string, Force> = {}
  function d3Force(name: string): Force | undefined
  function d3Force(name: string, force: Force | null): unknown
  function d3Force(name: string, force?: Force | null): unknown {
    if (force !== undefined) {
      if (force) set[name] = force
      return fg
    }
    return name === 'charge' ? charge : name === 'link' ? link : set[name]
  }
  const fg = { d3Force }
  return { fg, calls, set }
}

describe('applyTreeForces', () => {
  it('pushes siblings apart harder than the default charge', () => {
    const { fg, calls } = fakeGraph()
    applyTreeForces(fg)
    expect(calls.charge).toBe(TREE.chargeStrength)
    expect(TREE.chargeStrength).toBeLessThan(-30)
  })

  it('keeps edges long enough for a label between rows', () => {
    const { fg, calls } = fakeGraph()
    applyTreeForces(fg)
    expect(calls.link).toBe(TREE.linkDistance)
  })

  it('adds a row-spread force sized for a label', () => {
    const { fg, set } = fakeGraph()
    applyTreeForces(fg)
    expect(set.rowSpread).toBeTruthy()
    expect(TREE.siblingGap).toBeGreaterThanOrEqual(130)
  })
})

describe('frameFor', () => {
  const tan30 = Math.tan(Math.PI / 6)

  it('looks straight down at the centre from far enough to fit the height', () => {
    const f = frameFor([{ x: 0, y: -350 }, { x: 0, y: 350 }], { w: 800, h: 1000 }, 60, { pad: 0, maxZ: Infinity })
    expect(f.lookAt).toEqual({ x: 0, y: 0, z: 0 })
    expect(f.position.x).toBe(0)
    expect(f.position.y).toBe(0)
    expect(f.position.z).toBeCloseTo(350 / tan30, 5)
  })

  it('backs off further when the width is the limit', () => {
    const f = frameFor([{ x: -800, y: 0 }, { x: 800, y: 0 }], { w: 500, h: 1000 }, 60, { pad: 0, maxZ: Infinity })
    expect(f.position.z).toBeCloseTo(800 / (tan30 * 0.5), 5)
  })

  it('leaves room around the edges', () => {
    const f = frameFor([{ x: 0, y: -350 }, { x: 0, y: 350 }], { w: 800, h: 1000 }, 60, { pad: 0.1, maxZ: Infinity })
    expect(f.position.z).toBeCloseTo(350 / (tan30 * 0.8), 5)
  })

  it('never backs off past maxZ, and then keeps the root row at the top of the view', () => {
    const f = frameFor([{ x: 0, y: -600 }, { x: 0, y: 600 }], { w: 800, h: 1000 }, 60, { pad: 0, maxZ: 500 })
    expect(f.position.z).toBe(500)
    const halfVisible = 500 * tan30
    expect(f.lookAt.y).toBeCloseTo(600 - halfVisible, 5)
    expect(f.position.y).toBeCloseTo(600 - halfVisible, 5)
  })

  it('centres a single node', () => {
    const f = frameFor([{ x: 5, y: -7 }], { w: 800, h: 1000 }, 60, { pad: 0, maxZ: 500 })
    expect(f.lookAt).toEqual({ x: 5, y: -7, z: 0 })
    expect(f.position.z).toBeGreaterThan(0)
  })
})

describe('fitOnce', () => {
  it('frames the whole tree the first time the layout settles, and never again', () => {
    const moves: unknown[] = []
    const host = {
      nodes: () => [{ x: 0, y: -350 }, { x: 0, y: 350 }],
      fov: () => 60,
      view: () => ({ w: 800, h: 1000 }),
      move: (position: unknown, lookAt: unknown, ms: number) => moves.push([position, lookAt, ms]),
    }
    const onStop = fitOnce(host)
    onStop()
    onStop()
    expect(moves).toHaveLength(1)
    const [position, lookAt, ms] = moves[0] as [{ z: number }, { x: number; y: number; z: number }, number]
    expect(lookAt).toEqual({ x: 0, y: 0, z: 0 })
    expect(position.z).toBeGreaterThan(0)
    expect(ms).toBe(TREE.fitMs)
  })

  it('does nothing before there are nodes to frame', () => {
    const moves: unknown[] = []
    const host = { nodes: () => [], fov: () => 60, view: () => ({ w: 800, h: 1000 }), move: (...a: unknown[]) => moves.push(a) }
    fitOnce(host)()
    expect(moves).toHaveLength(0)
  })
})

describe('rowSpread', () => {
  type N = { x: number; y: number; fy?: number; vx: number; vy: number }
  const settle = (nodes: N[], gap: number, ticks = 300, alpha = 1) => {
    const force = rowSpread(gap)
    force.initialize(nodes)
    for (let i = 0; i < ticks; i++) {
      force(alpha)
      for (const n of nodes) {
        n.x += n.vx
        n.vx *= 0.4
      }
    }
  }

  it('pushes two nodes in the same row apart until they are a gap apart', () => {
    const nodes: N[] = [{ x: 0, y: 0, fy: 0, vx: 0, vy: 0 }, { x: 10, y: 0, fy: 0, vx: 0, vy: 0 }]
    settle(nodes, 140)
    expect(Math.abs(nodes[1].x - nodes[0].x)).toBeGreaterThanOrEqual(139)
    expect(nodes[0].vy).toBe(0)
  })

  it('ignores nodes in different rows even when they sit at the same x', () => {
    const nodes: N[] = [{ x: 0, y: 0, fy: 0, vx: 0, vy: 0 }, { x: 0, y: 70, fy: 70, vx: 0, vy: 0 }]
    settle(nodes, 140)
    expect(nodes[0].x).toBe(0)
    expect(nodes[1].x).toBe(0)
  })

  it('still holds the gap once the simulation has cooled, like collide does', () => {
    const nodes: N[] = [{ x: 0, y: 0, fy: 0, vx: 0, vy: 0 }, { x: 10, y: 0, fy: 0, vx: 0, vy: 0 }]
    settle(nodes, 140, 50, 0.01)
    expect(Math.abs(nodes[1].x - nodes[0].x)).toBeGreaterThanOrEqual(139)
  })

  it('separates nodes that start on exactly the same spot', () => {
    const nodes: N[] = [{ x: 0, y: 0, fy: 0, vx: 0, vy: 0 }, { x: 0, y: 0, fy: 0, vx: 0, vy: 0 }]
    settle(nodes, 140)
    expect(Math.abs(nodes[1].x - nodes[0].x)).toBeGreaterThanOrEqual(139)
  })
})
