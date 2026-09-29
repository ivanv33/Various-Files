export interface Vec3 {
  x: number
  y: number
  z: number
}

export const FLY_DISTANCE = 120

export function cameraFor(node: { x?: number; y?: number; z?: number }, distance = FLY_DISTANCE): { position: Vec3; lookAt: Vec3 } {
  const lookAt = { x: node.x ?? 0, y: node.y ?? 0, z: node.z ?? 0 }
  const r = Math.hypot(lookAt.x, lookAt.y, lookAt.z)
  if (r === 0) return { position: { x: 0, y: 0, z: distance }, lookAt }
  const k = 1 + distance / r
  return { position: { x: lookAt.x * k, y: lookAt.y * k, z: lookAt.z * k }, lookAt }
}
