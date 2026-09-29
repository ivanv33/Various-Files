'use client'
import { useRouter } from 'next/navigation'
import Keycap from '@/components/Keycap'
import type { PlanSummary } from '@/lib/store'

interface ToolbarProps {
  plans: PlanSummary[]
  slug: string
  planName: string
  nodeCount: number
  onAddNode: () => void
  onNewPlan: () => void
}

const btn = 'inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-medium transition-colors hover:bg-white/10'

export default function Toolbar(p: ToolbarProps) {
  const router = useRouter()
  return (
    <div className="fixed left-4 top-4 z-10 flex items-center gap-2 glass rounded-xl p-2">
      <select
        data-testid="plan-select"
        aria-label="Plan"
        className="rounded-md border border-white/10 bg-black/40 px-2 py-1 text-xs"
        value={p.slug}
        onChange={e => router.push(`/?plan=${e.target.value}`)}
      >
        {p.plans.map(pl => (
          <option key={pl.slug} value={pl.slug}>
            {pl.name}
          </option>
        ))}
      </select>
      <span data-testid="node-count" className="font-mono text-xs text-white/50">
        {p.nodeCount} nodes
      </span>
      <button type="button" data-testid="add-node" aria-label="Add node" className={btn} onClick={p.onAddNode}>
        + Node <Keycap>N</Keycap>
      </button>
      <button type="button" data-testid="new-plan" aria-label="New plan" className={btn} onClick={p.onNewPlan}>
        New plan
      </button>
    </div>
  )
}
