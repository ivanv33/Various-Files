import type { Plan, Status } from '@/lib/schema'

export interface GraphNode { id: string; title: string; status: Status; x?: number; y?: number; z?: number }
export interface GraphLink { source: string; target: string }
export interface GraphData { nodes: GraphNode[]; links: GraphLink[] }

export function toGraphData(plan: Plan, cache: Map<string, GraphNode>): GraphData {
  const ids = new Set(plan.nodes.map(n => n.id))
  for (const id of [...cache.keys()]) if (!ids.has(id)) cache.delete(id)
  const nodes = plan.nodes.map(n => {
    const existing = cache.get(n.id)
    if (existing) {
      existing.title = n.title
      existing.status = n.status
      return existing
    }
    const fresh: GraphNode = { id: n.id, title: n.title, status: n.status }
    cache.set(n.id, fresh)
    return fresh
  })
  const links: GraphLink[] = []
  for (const n of plan.nodes) for (const d of n.depends_on) links.push({ source: d, target: n.id })
  return { nodes, links }
}
