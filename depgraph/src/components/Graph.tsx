'use client'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import { CSS2DObject, CSS2DRenderer } from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import ForceGraph3D, { type ForceGraphMethods } from 'react-force-graph-3d'
import { cameraFor } from '@/lib/camera'
import { applyTreeForces, fitOnce, TREE } from '@/lib/treeLayout'
import { burstFrame, prefersReducedMotion, takeNewlyDone } from '@/lib/effects'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
import { labelFor, shakeLabel, syncLabels } from '@/lib/nodeLabel'
import type { Plan, Status } from '@/lib/schema'
import { pulseBlocked, type Pulsable } from '@/lib/pulse'
import type { NodeSignal } from '@/lib/selection'

export const STATUS_COLORS: Record<Status, string> = {
  todo: '#8b95a7',
  doing: '#5ac8fa',
  done: '#3a4152',
  blocked: '#ff6b6b',
}

interface GraphProps {
  plan: Plan
  selectedId: string | null
  arming: boolean
  flyTo: NodeSignal | null
  shake: NodeSignal | null
  onSelect: (id: string | null) => void
  onLinkRightClick: (dependencyId: string, dependentId: string) => void
}

const idOf = (end: unknown) => (typeof end === 'string' ? end : (end as GraphNode).id)

export default function Graph({ plan, selectedId, arming, flyTo, shake, onSelect, onLinkRightClick }: GraphProps) {
  const [cache] = useState(() => new Map<string, GraphNode>())
  const [labels] = useState(() => new Map<string, HTMLDivElement>())
  const [seenStatus] = useState(() => new Map<string, Status>())
  const [extraRenderers] = useState(() => [new CSS2DRenderer()])
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined)
  const [size, setSize] = useState({ w: 800, h: 600 })
  const pick = useRef(onSelect)

  useEffect(() => {
    pick.current = onSelect
  })
  const onPick = useCallback((id: string) => pick.current(id), [])

  useEffect(() => {
    const update = () => setSize({ w: window.innerWidth, h: window.innerHeight })
    update()
    window.addEventListener('resize', update)
    return () => window.removeEventListener('resize', update)
  }, [])

  const blocked = useRef(new Set<Pulsable>())

  useEffect(() => {
    let raf = 0
    const tick = (t: number) => {
      pulseBlocked(blocked.current, t)
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [])

  useEffect(() => {
    const fg = fgRef.current
    // Light haze only: the framed tree sits ~600 units out, where the old 0.002 density hid every edge.
    if (fg) fg.scene().fog = new THREE.FogExp2(0x05060a, 0.0005)
  }, [])

  // The plan lives on the z = 0 plane and is viewed straight on: no orbiting, only pan (any drag) and zoom (wheel).
  useEffect(() => {
    const fg = fgRef.current
    if (!fg) return
    const controls = fg.controls() as unknown as {
      enableRotate: boolean
      mouseButtons: { LEFT: THREE.MOUSE; MIDDLE: THREE.MOUSE; RIGHT: THREE.MOUSE }
      touches: { ONE: THREE.TOUCH; TWO: THREE.TOUCH }
      update: () => void
    }
    controls.enableRotate = false
    controls.mouseButtons = { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN }
    controls.touches = { ONE: THREE.TOUCH.PAN, TWO: THREE.TOUCH.DOLLY_PAN }
    controls.update()
  }, [])

  // Top-down tree: rows are pinned by dagMode, the forces spread siblings so labels do not overprint.
  // The first settle frames the whole tree; after that the camera is the user's.
  const sizeRef = useRef(size)
  useEffect(() => {
    sizeRef.current = size
  }, [size])
  const fitter = useRef<() => void>(() => {})
  useEffect(() => {
    fitter.current = fitOnce({
      nodes: () => [...cache.values()],
      fov: () => (fgRef.current?.camera() as THREE.PerspectiveCamera | undefined)?.fov ?? 75,
      view: () => sizeRef.current,
      move: (position, lookAt, ms) => fgRef.current?.cameraPosition(position, lookAt, ms),
    })
  }, [cache])
  const onEngineStop = useCallback(() => fitter.current(), [])
  useEffect(() => {
    if (fgRef.current) applyTreeForces(fgRef.current)
  }, [])

  const structureKey = plan.nodes.map(n => `${n.id}:${n.depends_on.join(',')}`).join('|')
  const data = useMemo(() => {
    return toGraphData(plan, cache)
  }, [structureKey]) // eslint-disable-line react-hooks/exhaustive-deps

  // Status/title changes must not rebuild graphData (that reheats the force layout); patch the cached
  // nodes in place instead. nodeThreeObject reads them when it rebuilds the meshes on this render.
  useMemo(() => {
    for (const n of plan.nodes) {
      const cached = cache.get(n.id)
      if (cached) {
        cached.status = n.status
        cached.title = n.title
      }
    }
  }, [plan, cache])

  const neighbors = useMemo(() => {
    const set = new Set<string>()
    if (!selectedId) return set
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId) set.add(idOf(l.target))
      if (l.target === selectedId || idOf(l.target) === selectedId) set.add(idOf(l.source))
    }
    return set
  }, [data, selectedId])

  useEffect(() => {
    syncLabels(
      labels,
      plan.nodes.map(n => ({
        id: n.id,
        title: n.title,
        status: n.status,
        selected: n.id === selectedId,
        dim: !!selectedId && n.id !== selectedId && !neighbors.has(n.id),
      })),
      onPick,
    )
  }, [labels, plan, selectedId, neighbors, onPick])

  useEffect(() => {
    const fg = fgRef.current
    const node = flyTo ? cache.get(flyTo.id) : undefined
    if (!fg || !node) return
    const { position, lookAt } = cameraFor(node)
    fg.cameraPosition(position, lookAt, 800)
  }, [flyTo, cache])

  useEffect(() => {
    const el = shake ? labels.get(shake.id) : undefined
    if (el) shakeLabel(el)
  }, [shake, labels])

  useEffect(() => {
    const ids = takeNewlyDone(seenStatus, plan.nodes)
    const fg = fgRef.current
    if (!fg || ids.length === 0 || prefersReducedMotion()) return
    const scene = fg.scene()
    const camera = fg.camera()
    const rings = ids.flatMap(id => {
      const node = cache.get(id)
      if (!node) return []
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(7, 8.5, 48),
        new THREE.MeshBasicMaterial({ color: 0xcfe8ff, transparent: true, opacity: 0.9, side: THREE.DoubleSide }),
      )
      ring.position.set(node.x ?? 0, node.y ?? 0, node.z ?? 0)
      ring.quaternion.copy(camera.quaternion)
      scene.add(ring)
      return [ring]
    })
    const start = performance.now()
    // No cleanup: the burst is one-shot and removes itself. Under StrictMode the effect re-runs,
    // and a cleanup would cancel the ring on the first run while the second run sees no change.
    const tick = (t: number) => {
      const f = burstFrame(t - start)
      for (const r of rings) {
        r.scale.setScalar(f.scale)
        r.material.opacity = f.opacity
      }
      if (!f.done) {
        requestAnimationFrame(tick)
        return
      }
      for (const r of rings) {
        scene.remove(r)
        r.geometry.dispose()
        r.material.dispose()
      }
    }
    requestAnimationFrame(tick)
  }, [plan, seenStatus, cache])

  return (
    <div data-arming={arming} style={{ cursor: arming ? 'crosshair' : 'default' }}>
      <ForceGraph3D<GraphNode, GraphLink>
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#05060a"
        numDimensions={2}
        dagMode={TREE.dagMode}
        dagLevelDistance={TREE.levelDistance}
        onDagError={(loop: (string | number)[]) => console.warn("dag layout skipped a cycle", loop)}
        showNavInfo={false}
        onEngineStop={onEngineStop}
        extraRenderers={extraRenderers}
        nodeThreeObject={(n: GraphNode) => {
          const selected = n.id === selectedId
          const dim = !!selectedId && !selected && !neighbors.has(n.id)
          const radius = selected ? 6.5 : 5
          const color = new THREE.Color(STATUS_COLORS[n.status])
          const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: n.status === 'done' ? 0.15 : 0.7, transparent: true, opacity: dim ? 0.18 : 1, roughness: 0.4 })
          const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 24, 24), mat)
          if (n.status === 'blocked') blocked.current.add(mesh as unknown as Pulsable)
          if (selected) {
            const ringMat = new THREE.MeshBasicMaterial({ color: 0x5ac8fa, transparent: true, opacity: 0.85 })
            mesh.add(new THREE.Mesh(new THREE.TorusGeometry(radius + 3, 0.45, 8, 48), ringMat))
          }
          const label = new CSS2DObject(labelFor(labels, n.id, onPick))
          label.center.set(0.5, 0)
          label.position.set(0, -radius, 0)
          mesh.add(label)
          return mesh
        }}
        nodeThreeObjectExtend={false}
        linkColor={() => '#7a8399'}
        linkOpacity={0.5}
        linkWidth={(l: GraphLink) => (selectedId && (idOf(l.source) === selectedId || idOf(l.target) === selectedId) ? 2 : 0.6)}
        linkDirectionalArrowLength={5}
        linkDirectionalArrowRelPos={1}
        linkDirectionalParticles={(l: GraphLink) => (selectedId && idOf(l.target) === selectedId ? 2 : 0)}
        onNodeClick={(n: GraphNode) => onSelect(n.id)}
        onBackgroundClick={() => onSelect(null)}
        onLinkRightClick={(l: GraphLink) => onLinkRightClick(idOf(l.source), idOf(l.target))}
      />
    </div>
  )
}
