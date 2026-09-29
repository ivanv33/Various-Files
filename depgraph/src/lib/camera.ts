export interface Vec3 {
  x: number
  y: number
  z: number
}

export const FLY_DISTANCE = 120

/** The graph is laid out on the z = 0 plane and viewed straight on, so the camera always sits on the plane normal above the node. */
export function cameraFor(node: { x?: number; y?: number; z?: number }, distance = FLY_DISTANCE): { position: Vec3; lookAt: Vec3 } {
  const lookAt = { x: node.x ?? 0, y: node.y ?? 0, z: node.z ?? 0 }
  return { position: { x: lookAt.x, y: lookAt.y, z: lookAt.z + distance }, lookAt }
}
