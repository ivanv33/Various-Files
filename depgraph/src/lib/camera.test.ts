import { describe, expect, it } from 'vitest'
import { FLY_DISTANCE, cameraFor } from './camera'

describe('cameraFor', () => {
  it('looks at the node from FLY_DISTANCE further out along the ray from the origin', () => {
    expect(FLY_DISTANCE).toBe(120)
    expect(cameraFor({ x: 0, y: 0, z: 30 })).toEqual({ position: { x: 0, y: 0, z: 150 }, lookAt: { x: 0, y: 0, z: 30 } })
  })

  it('keeps exactly `distance` between camera and node', () => {
    const { position, lookAt } = cameraFor({ x: 3, y: 4, z: 0 }, 5)
    expect(position).toEqual({ x: 6, y: 8, z: 0 })
    expect(Math.hypot(position.x - lookAt.x, position.y - lookAt.y, position.z - lookAt.z)).toBeCloseTo(5)
  })

  it('treats a node at (or without) coordinates at the origin by looking down +z', () => {
    expect(cameraFor({})).toEqual({ position: { x: 0, y: 0, z: 120 }, lookAt: { x: 0, y: 0, z: 0 } })
  })
})
