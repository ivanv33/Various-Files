export type Pulsable = { parent: unknown | null; material: { emissiveIntensity: number } }

export function pulseBlocked(set: Set<Pulsable>, t: number): void {
  for (const m of set) {
    if (m.parent === null) {
      set.delete(m)
      continue
    }
    m.material.emissiveIntensity = 0.55 + 0.45 * Math.sin(t / 400)
  }
}
