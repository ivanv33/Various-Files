'use client'
import InlineText from '@/components/InlineText'
import Keycap from '@/components/Keycap'
import StatusPips from '@/components/StatusPips'
import type { Plan, PlanNode } from '@/lib/schema'

export type NodePatch = Partial<Omit<PlanNode, 'id'>>

export interface NodeHudProps {
  plan: Plan
  node: PlanNode
  armed: boolean
  editTitle: boolean
  deleteArmed: boolean
  onChange: (patch: NodePatch) => void
  onToggleLink: () => void
  onFocusNode: (id: string) => void
  onRemoveDependency: (dependencyId: string) => void
  onDelete: () => void
  onClose: () => void
}

const chip = 'inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs transition-colors hover:bg-white/10'
const btn = 'inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/5 px-2 py-1 text-xs transition-colors hover:bg-white/10'

export default function NodeHud(p: NodeHudProps) {
  const { node, plan } = p
  const titleOf = (id: string) => plan.nodes.find(n => n.id === id)?.title || id
  const unlocks = plan.nodes.filter(n => n.depends_on.includes(node.id))

  return (
    <section
      data-testid="node-hud"
      aria-label="Selected node"
      className="hud-in glass fixed bottom-4 left-1/2 z-10 flex w-[560px] max-w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-2 rounded-xl p-3"
    >
      <div className="flex items-center gap-3">
        <InlineText
          testId="hud-title"
          buttonLabel="Rename"
          inputLabel="Title"
          value={node.title}
          startEditing={p.editTitle}
          onCommit={title => p.onChange({ title })}
          className="min-w-0 flex-1 text-sm font-semibold"
        />
        <StatusPips value={node.status} onChange={status => p.onChange({ status })} />
        <button type="button" data-testid="hud-close" aria-label="Close" className="inline-flex items-center gap-1 text-xs text-white/50 hover:text-white" onClick={p.onClose}>
          ✕ <Keycap>Esc</Keycap>
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 text-xs">
        {node.tags.map(t => (
          <button
            key={t}
            type="button"
            data-testid={`tag-${t}`}
            aria-label={`Remove tag ${t}`}
            className={chip}
            onClick={() => p.onChange({ tags: node.tags.filter(x => x !== t) })}
          >
            #{t} <span aria-hidden="true">×</span>
          </button>
        ))}
        <InlineText
          testId="add-tag"
          buttonLabel="Add tag"
          inputLabel="New tag"
          value=""
          placeholder="+"
          icon=""
          onCommit={t => {
            if (!node.tags.includes(t)) p.onChange({ tags: [...node.tags, t] })
          }}
          className="text-xs"
        />
        <span className="ml-2 text-white/50">needs:</span>
        {node.depends_on.map(id => (
          <span key={id} data-testid={`dep-${id}`} className={chip}>
            <button type="button" className="hover:text-white" onClick={() => p.onFocusNode(id)}>
              {titleOf(id)}
            </button>
            <button type="button" aria-label={`Remove dependency ${titleOf(id)}`} className="text-white/50 hover:text-red-300" onClick={() => p.onRemoveDependency(id)}>
              ×
            </button>
          </span>
        ))}
        <button
          type="button"
          data-testid="link-button"
          aria-label="Add dependency"
          aria-pressed={p.armed}
          className={`${chip} ${p.armed ? 'border-sky-400/60 bg-sky-500/20 text-sky-100' : ''}`}
          onClick={p.onToggleLink}
        >
          + <Keycap>L</Keycap>
        </button>
        {unlocks.length > 0 && <span className="ml-2 text-white/50">unlocks:</span>}
        {unlocks.map(n => (
          <button key={n.id} type="button" data-testid={`unlock-${n.id}`} aria-label={`Select ${n.title}`} className={`${chip} text-white/70`} onClick={() => p.onFocusNode(n.id)}>
            {n.title || n.id}
          </button>
        ))}
      </div>

      {p.armed && (
        <p role="status" data-testid="link-hint" className="text-xs text-sky-200">
          Pick what {node.title} needs
        </p>
      )}

      <div className="flex items-center gap-2">
        <InlineText
          testId="hud-description"
          buttonLabel="Edit description"
          inputLabel="Description"
          value={node.description}
          placeholder="▸ description…"
          multiline
          onCommit={description => p.onChange({ description })}
          className="min-w-0 flex-1 text-xs text-white/70"
        />
        <button
          type="button"
          data-testid="delete-node"
          aria-label={p.deleteArmed ? 'Confirm delete' : 'Delete node'}
          className={`${btn} ${p.deleteArmed ? 'border-red-400/60 bg-red-950/60 text-red-100' : 'text-red-200/80'}`}
          onClick={p.onDelete}
        >
          {p.deleteArmed ? 'Confirm delete' : 'del'} <Keycap>Del</Keycap>
        </button>
      </div>
    </section>
  )
}
