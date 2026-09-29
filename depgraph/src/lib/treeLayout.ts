/**
 * Top-down tree layout. dagMode pins every node to its row (fy), so the forces here only decide
 * how siblings spread sideways. Labels are fixed-pixel CSS2D objects about 130 px wide, and the
 * camera never frames further out than one pixel per world unit, so a sibling gap of 140 units
 * keeps labels in a row from overprinting. Rows are only 70 apart, so a round collide radius
 * would shove neighbouring rows sideways too; the row-only spread force below does not.
 */
export const TREE = {
  dagMode: 'td' as const,
  levelDistance: 70,
  chargeStrength: -40,
  linkDistance: 60,
  siblingGap: 140,
  fitMs: 600,
  /** Fraction of the view kept clear on each side when framing. */
  fitPad: 0.06,
  /** Never frame so far out that a world unit is smaller than this many pixels: labels are fixed-size. */
  minPxPerUnit: 1,
}

type ForceLike = { [key: string]: unknown }
type ForceHost = {
  d3Force(name: string): ForceLike | undefined
  d3Force(name: string, force: ForceLike | null): unknown
}

export function applyTreeForces(fg: ForceHost): void {
  const charge = fg.d3Force('charge') as { strength?: (v: number) => unknown } | undefined
  charge?.strength?.(TREE.chargeStrength)
  const link = fg.d3Force('link') as { distance?: (v: number) => unknown } | undefined
  link?.distance?.(TREE.linkDistance)
  fg.d3Force('rowSpread', rowSpread(TREE.siblingGap))
}

type RowNode = { x?: number; fy?: number | null; y?: number; vx?: number; index?: number }

/**
 * d3 force: nodes pinned to the same row (equal fy) that are closer than `gap` along x are pushed
 * apart along x only. Like d3's collide it corrects the whole overlap every tick regardless of
 * alpha, so the link and charge forces cannot settle siblings closer than the gap. Coincident
 * nodes are nudged by index so they can separate.
 */
export type RowSpreadForce = ForceLike & { (alpha: number): void; initialize: (ns: RowNode[]) => void }

export function rowSpread(gap: number): RowSpreadForce {
  let nodes: RowNode[] = []
  const force = () => {
    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i]
      const ay = a.fy ?? a.y ?? 0
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j]
        if (Math.abs((b.fy ?? b.y ?? 0) - ay) > 1e-6) continue
        let dx = (b.x ?? 0) - (a.x ?? 0)
        if (dx === 0) dx = 1e-3 * ((b.index ?? j) - (a.index ?? i) || 1)
        const overlap = gap - Math.abs(dx)
        if (overlap <= 0) continue
        const push = (overlap / 2) * Math.sign(dx)
        a.vx = (a.vx ?? 0) - push
        b.vx = (b.vx ?? 0) + push
      }
    }
  }
  return Object.assign(force, {
    initialize: (ns: RowNode[]) => {
      nodes = ns
    },
  }) as unknown as RowSpreadForce
}


type Pt = { x?: number; y?: number }
type Vec3 = { x: number; y: number; z: number }
export type Frame = { position: Vec3; lookAt: Vec3 }

/**
 * Camera frame that shows every node straight on (camera on the +z normal). z backs off until the
 * bounding box fits the view, but not past maxZ; when clamped, the root row is kept at the top so a
 * tall tree is read from its roots down.
 */
export function frameFor(nodes: Pt[], view: { w: number; h: number }, fovDeg: number, opts: { pad: number; maxZ: number }): Frame {
  const xs = nodes.map(n => n.x ?? 0)
  const ys = nodes.map(n => n.y ?? 0)
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys)
  const tan = Math.tan((fovDeg * Math.PI) / 360)
  const usable = 1 - 2 * opts.pad
  const aspect = view.w / view.h
  const halfW = (maxX - minX) / 2, halfH = (maxY - minY) / 2
  const zForH = halfH / (tan * usable)
  const zForW = halfW / (tan * aspect * usable)
  const z = Math.min(Math.max(zForH, zForW, 1), opts.maxZ)
  const cx = (minX + maxX) / 2
  const halfVisible = z * tan
  // Fits: centre it. Clamped: put the top of the box at the top of the padded view.
  const cy = z < opts.maxZ || halfH <= halfVisible * usable ? (minY + maxY) / 2 : maxY + opts.pad * 2 * halfVisible - halfVisible
  const lookAt = { x: cx, y: cy, z: 0 }
  return { position: { x: cx, y: cy, z }, lookAt }
}

export type FrameHost = {
  nodes(): Pt[]
  fov(): number
  view(): { w: number; h: number }
  move(position: Vec3, lookAt: Vec3, ms: number): unknown
}

/** Returns an onEngineStop handler that frames the whole tree once, then leaves the camera to the user. */
export function fitOnce(host: FrameHost): () => void {
  let done = false
  return () => {
    if (done) return
    const nodes = host.nodes()
    if (nodes.length === 0) return
    done = true
    const view = host.view()
    const tan = Math.tan((host.fov() * Math.PI) / 360)
    const maxZ = view.h / (2 * tan * TREE.minPxPerUnit)
    const { position, lookAt } = frameFor(nodes, view, host.fov(), { pad: TREE.fitPad, maxZ })
    host.move(position, lookAt, TREE.fitMs)
  }
}
