'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import * as THREE from 'three'
import ForceGraph3D, { type ForceGraphMethods } from 'react-force-graph-3d'
import { toGraphData, type GraphLink, type GraphNode } from '@/lib/graphData'
import type { Plan, Status } from '@/lib/schema'
import { pulseBlocked, type Pulsable } from '@/lib/pulse'

export const STATUS_COLORS: Record<Status, string> = {
  todo: '#8b95a7',
  doing: '#5ac8fa',
  done: '#3a4152',
  blocked: '#ff6b6b',
}

interface GraphProps {
  plan: Plan
  selectedId: string | null
  linkMode: boolean
  onSelect: (id: string | null) => void
  onLinkRightClick: (dependencyId: string, dependentId: string) => void
}

const idOf = (end: unknown) => (typeof end === 'string' ? end : (end as GraphNode).id)

export default function Graph({ plan, selectedId, linkMode, onSelect, onLinkRightClick }: GraphProps) {
  const [cache] = useState(() => new Map<string, GraphNode>())
  const fgRef = useRef<ForceGraphMethods<GraphNode, GraphLink> | undefined>(undefined)
  const [size, setSize] = useState({ w: 800, h: 600 })

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
    if (fg) fg.scene().fog = new THREE.FogExp2(0x05060a, 0.002)
  }, [])

  const structureKey = plan.nodes.map(n => `${n.id}:${n.status}:${n.title}:${n.depends_on.join(',')}`).join('|')
  const data = useMemo(() => {
    return toGraphData(plan, cache)
  }, [structureKey]) // eslint-disable-line react-hooks/exhaustive-deps

  const neighbors = useMemo(() => {
    const set = new Set<string>()
    if (!selectedId) return set
    for (const l of data.links) {
      if (l.source === selectedId || idOf(l.source) === selectedId) set.add(idOf(l.target))
      if (l.target === selectedId || idOf(l.target) === selectedId) set.add(idOf(l.source))
    }
    return set
  }, [data, selectedId])

  return (
    <div style={{ cursor: linkMode ? 'crosshair' : 'default' }}>
      <ForceGraph3D<GraphNode, GraphLink>
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#05060a"
        nodeLabel={(n: GraphNode) => `${n.title} · ${n.status}`}
        nodeThreeObject={(n: GraphNode) => {
          const dim = !!selectedId && n.id !== selectedId && !neighbors.has(n.id)
          const color = new THREE.Color(STATUS_COLORS[n.status])
          const mat = new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: n.status === 'done' ? 0.15 : 0.7, transparent: true, opacity: dim ? 0.18 : 1, roughness: 0.4 })
          const mesh = new THREE.Mesh(new THREE.SphereGeometry(n.id === selectedId ? 6.5 : 5, 24, 24), mat)
          if (n.status === 'blocked') blocked.current.add(mesh as unknown as Pulsable)
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
