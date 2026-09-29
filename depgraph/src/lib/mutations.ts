import { slugify, uniqueId, type Plan, type PlanNode } from '@/lib/schema'

export function addNode(plan: Plan, title = 'Untitled'): { plan: Plan; id: string } {
  const id = uniqueId(slugify(title), plan.nodes.map(n => n.id))
  const node: PlanNode = { id, title, description: '', status: 'todo', tags: [], depends_on: [] }
  return { plan: { ...plan, nodes: [...plan.nodes, node] }, id }
}

export function updateNode(plan: Plan, id: string, patch: Partial<Omit<PlanNode, 'id'>>): Plan {
  return { ...plan, nodes: plan.nodes.map(n => (n.id === id ? { ...n, ...patch, id } : n)) }
}

export function deleteNode(plan: Plan, id: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.filter(n => n.id !== id).map(n => ({ ...n, depends_on: n.depends_on.filter(d => d !== id) })),
  }
}

export function addDependency(plan: Plan, dependencyId: string, dependentId: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.map(n =>
      n.id === dependentId && !n.depends_on.includes(dependencyId)
        ? { ...n, depends_on: [...n.depends_on, dependencyId] }
        : n,
    ),
  }
}

export function removeDependency(plan: Plan, dependencyId: string, dependentId: string): Plan {
  return {
    ...plan,
    nodes: plan.nodes.map(n =>
      n.id === dependentId ? { ...n, depends_on: n.depends_on.filter(d => d !== dependencyId) } : n,
    ),
  }
}

export function addNextNode(plan: Plan, fromId: string, title = 'Untitled'): { plan: Plan; id: string } {
  const added = addNode(plan, title)
  return { plan: addDependency(added.plan, fromId, added.id), id: added.id }
}
