import { describe, expect, it } from 'vitest'
import { pulseBlocked, type Pulsable } from './pulse'

const mk = (parent: unknown | null): Pulsable => ({ parent, material: { emissiveIntensity: 0 } })

describe('pulseBlocked', () => {
  it('sets emissive intensity from t on attached meshes', () => {
    const m = mk({})
    const set = new Set([m])
    pulseBlocked(set, 0)
    expect(m.material.emissiveIntensity).toBeCloseTo(0.55)
    pulseBlocked(set, 200 * Math.PI)
    expect(m.material.emissiveIntensity).toBeCloseTo(1.0)
    pulseBlocked(set, 400 * Math.PI)
    expect(m.material.emissiveIntensity).toBeCloseTo(0.55)
  })

  it('removes detached meshes (parent null) from the set', () => {
    const m = mk(null)
    const set = new Set([m])
    pulseBlocked(set, 100)
    expect(set.has(m)).toBe(false)
    expect(m.material.emissiveIntensity).toBe(0)
  })

  it('leaves attached meshes in the set', () => {
    const a = mk({})
    const b = mk(null)
    const set = new Set([a, b])
    pulseBlocked(set, 100)
    expect(set.has(a)).toBe(true)
    expect(set.size).toBe(1)
  })
})
