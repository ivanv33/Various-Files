'use client'
import type { SaveState } from '@/hooks/usePlan'

const LABEL: Record<SaveState, string> = { idle: '', saving: 'saving…', saved: 'saved', error: 'save failed' }

export default function SaveIndicator({ state, error }: { state: SaveState; error: string | null }) {
  if (state === 'idle') return null
  return (
    <div
      data-testid="save-indicator"
      data-state={state}
      className={`fixed bottom-4 right-4 glass rounded-lg px-3 py-1.5 font-mono text-xs ${
        state === 'error' ? 'border-red-400/40 text-red-200' : 'text-white/60'
      }`}
    >
      {LABEL[state]}
      {state === 'error' && error ? `: ${error}` : ''}
    </div>
  )
}
