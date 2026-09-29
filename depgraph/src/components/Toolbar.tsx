'use client'
import { useRouter } from 'next/navigation'
import type { PlanSummary } from '@/lib/store'

interface ToolbarProps {
  plans: PlanSummary[]
  slug: string
  planName: string
  nodeCount: number
  linkMode: boolean
  onToggleLinkMode: () => void
  onAddNode: () => void
  onNewPlan: () => void
}

const btn = 'rounded-md border border-white/10 bg-white/5 px-2.5 py-1 text-xs hover:bg-white/10'

export default function Toolbar(p: ToolbarProps) {
  const router = useRouter()
  return (
    <div className="fixed left-4 top-4 flex items-center gap-2 rounded-lg border border-white/10 bg-black/40 p-2 backdrop-blur">
      <select
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
      <button className={btn} onClick={p.onNewPlan}>New plan</button>
      <button className={btn} onClick={p.onAddNode}>Add node</button>
      <button className={`${btn} ${p.linkMode ? 'border-sky-400/60 bg-sky-500/20' : ''}`} aria-pressed={p.linkMode} onClick={p.onToggleLinkMode}>
        Link mode
      </button>
      <span className="ml-2 font-mono text-xs text-white/50">
        <span data-testid="node-count">{p.nodeCount} nodes</span>
      </span>
    </div>
  )
}
