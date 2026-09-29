'use client'
import type { PlanNode } from '@/lib/schema'

export interface NodeHudProps {
  node: PlanNode
  armed: boolean
  onToggleLink: () => void
  onClose: () => void
}

const chip = 'inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs transition-colors hover:bg-white/10'

export default function NodeHud({ node, armed, onToggleLink, onClose }: NodeHudProps) {
  return (
    <section
      data-testid="node-hud"
      aria-label="Selected node"
      className="glass fixed bottom-4 left-1/2 z-10 flex w-[560px] max-w-[calc(100vw-2rem)] -translate-x-1/2 flex-col gap-2 rounded-xl p-3"
    >
      <div className="flex items-center gap-3">
        <span className="min-w-0 flex-1 truncate text-sm font-semibold">{node.title}</span>
        <button
          type="button"
          data-testid="link-button"
          aria-label="Add dependency"
          aria-pressed={armed}
          className={`${chip} ${armed ? 'border-sky-400/60 bg-sky-500/20 text-sky-100' : ''}`}
          onClick={onToggleLink}
        >
          +L
        </button>
        <button type="button" data-testid="hud-close" aria-label="Close" className="text-xs text-white/50 hover:text-white" onClick={onClose}>
          ✕
        </button>
      </div>
      {armed && (
        <p role="status" data-testid="link-hint" className="text-xs text-sky-200">
          Pick what {node.title} needs
        </p>
      )}
    </section>
  )
}
