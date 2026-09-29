'use client'
import { useEffect, useRef, useState } from 'react'
import { STATUSES, type Plan, type PlanNode, type Status } from '@/lib/schema'

interface NodePanelProps {
  plan: Plan
  nodeId: string
  onChange: (patch: Partial<Omit<PlanNode, 'id'>>) => string[]
  onDelete: () => void
  onClose: () => void
}

const field = 'w-full rounded-md border border-white/10 bg-white/5 px-2 py-1.5 text-sm outline-none focus:border-sky-400/60'

export default function NodePanel({ plan, nodeId, onChange, onDelete, onClose }: NodePanelProps) {
  const node = plan.nodes.find(n => n.id === nodeId)
  const [filter, setFilter] = useState('')
  const [tagDraft, setTagDraft] = useState('')
  const [error, setError] = useState<string | null>(null)
  const titleRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (node?.title === 'Untitled') titleRef.current?.select()
  }, [nodeId]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!node) return null

  const change = (patch: Partial<Omit<PlanNode, 'id'>>) => {
    const errors = onChange(patch)
    setError(errors.length ? errors.join('; ') : null)
  }

  const others = plan.nodes.filter(n => n.id !== nodeId && (n.title + n.id).toLowerCase().includes(filter.toLowerCase()))

  return (
    <aside
      data-testid="node-panel"
      className="fixed right-4 top-4 bottom-4 flex w-80 flex-col gap-3 overflow-y-auto glass rounded-xl p-4"
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-white/50">{node.id}</span>
        <button className="text-xs text-white/50 hover:text-white" onClick={onClose} aria-label="Close panel">✕</button>
      </div>

      <label className="text-xs text-white/60">
        Title
        <input ref={titleRef} aria-label="Title" className={field} value={node.title} onChange={e => change({ title: e.target.value })} />
      </label>

      <label className="text-xs text-white/60">
        Description
        <textarea aria-label="Description" className={`${field} min-h-24`} value={node.description} onChange={e => change({ description: e.target.value })} />
      </label>

      <label className="text-xs text-white/60">
        Status
        <select aria-label="Status" className={field} value={node.status} onChange={e => change({ status: e.target.value as Status })}>
          {STATUSES.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </label>

      <div className="text-xs text-white/60">
        Tags
        <div className="mt-1 flex flex-wrap gap-1">
          {node.tags.map(t => (
            <button key={t} className="rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs" onClick={() => change({ tags: node.tags.filter(x => x !== t) })} title="Remove tag">
              {t} ✕
            </button>
          ))}
        </div>
        <input
          aria-label="Add tag"
          className={`${field} mt-1`}
          placeholder="add tag, press Enter"
          value={tagDraft}
          onChange={e => setTagDraft(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && tagDraft.trim()) {
              if (!node.tags.includes(tagDraft.trim())) change({ tags: [...node.tags, tagDraft.trim()] })
              setTagDraft('')
            }
          }}
        />
      </div>

      <div className="text-xs text-white/60">
        Depends on
        <input aria-label="Filter dependencies" className={`${field} mt-1`} placeholder="filter…" value={filter} onChange={e => setFilter(e.target.value)} />
        <ul className="mt-1 max-h-48 overflow-y-auto">
          {others.map(o => (
            <li key={o.id}>
              <label className="flex cursor-pointer items-center gap-2 py-0.5">
                <input
                  type="checkbox"
                  aria-label={o.id}
                  checked={node.depends_on.includes(o.id)}
                  onChange={e =>
                    change({ depends_on: e.target.checked ? [...node.depends_on, o.id] : node.depends_on.filter(d => d !== o.id) })
                  }
                />
                <span className="truncate">{o.title}</span>
                <span className="font-mono text-white/40">{o.id}</span>
              </label>
            </li>
          ))}
        </ul>
      </div>

      {error && <div role="alert" className="rounded-md border border-red-400/40 bg-red-950/40 p-2 text-xs text-red-200">{error}</div>}

      <button
        className="mt-auto rounded-md border border-red-400/30 bg-red-950/30 px-2 py-1.5 text-xs text-red-200 hover:bg-red-950/60"
        onClick={onDelete}
      >
        Delete node
      </button>
    </aside>
  )
}
