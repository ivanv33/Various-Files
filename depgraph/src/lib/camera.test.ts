import { describe, expect, it } from 'vitest'
import { FLY_DISTANCE, cameraFor } from './camera'

describe('cameraFor', () => {
  it('looks straight at the node from FLY_DISTANCE along the plane normal (+z)', () => {
    expect(FLY_DISTANCE).toBe(120)
    expect(cameraFor({ x: 30, y: -40, z: 0 })).toEqual({ position: { x: 30, y: -40, z: 120 }, lookAt: { x: 30, y: -40, z: 0 } })
  })

  it('keeps exactly `distance` between camera and node without tilting', () => {
    const { position, lookAt } = cameraFor({ x: 3, y: 4, z: 0 }, 5)
    expect(position).toEqual({ x: 3, y: 4, z: 5 })
    expect(Math.hypot(position.x - lookAt.x, position.y - lookAt.y, position.z - lookAt.z)).toBeCloseTo(5)
  })

  it('stays on the normal even when the node has a z offset', () => {
    expect(cameraFor({ x: 10, y: 0, z: 30 })).toEqual({ position: { x: 10, y: 0, z: 150 }, lookAt: { x: 10, y: 0, z: 30 } })
  })

  it('treats a node without coordinates as the origin', () => {
    expect(cameraFor({})).toEqual({ position: { x: 0, y: 0, z: 120 }, lookAt: { x: 0, y: 0, z: 0 } })
  })
})
