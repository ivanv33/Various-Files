'use client'
import { useEffect, useRef, useState, type KeyboardEvent } from 'react'

export interface InlineTextProps {
  value: string
  onCommit: (next: string) => void
  buttonLabel: string
  inputLabel: string
  testId: string
  placeholder?: string
  icon?: string
  multiline?: boolean
  startEditing?: boolean
  className?: string
}

const field = 'w-full rounded-md border border-sky-400/40 bg-black/40 px-2 py-1 outline-none'

export default function InlineText({
  value,
  onCommit,
  buttonLabel,
  inputLabel,
  testId,
  placeholder = '',
  icon = '✎',
  multiline = false,
  startEditing = false,
  className = '',
}: InlineTextProps) {
  const [editing, setEditing] = useState(startEditing)
  const [draft, setDraft] = useState(value)
  // Set once an edit is committed or cancelled, so a blur that follows Enter/Esc cannot commit again.
  const closed = useRef(false)
  // Latest edit state for the unmount cleanup, which must not see stale closures.
  const live = useRef({ editing: startEditing, draft: value, value, multiline, onCommit })

  useEffect(() => {
    live.current = { editing, draft, value, multiline, onCommit }
  })

  // An unmount mid-edit (HUD remount, canvas click) may skip blur; save the pending edit like blur would.
  useEffect(
    () => () => {
      const l = live.current
      if (!l.editing || closed.current) return
      const next = l.multiline ? l.draft : l.draft.trim()
      if (next !== l.value && (l.multiline || next !== '')) l.onCommit(next)
    },
    [],
  )

  const open = () => {
    closed.current = false
    setDraft(value)
    setEditing(true)
  }

  const commit = () => {
    if (closed.current) return
    closed.current = true
    setEditing(false)
    const next = multiline ? draft : draft.trim()
    if (next !== value && (multiline || next !== '')) onCommit(next)
  }

  const cancel = () => {
    closed.current = true
    setEditing(false)
  }

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    if (e.key === 'Escape') {
      e.preventDefault()
      cancel()
    } else if (e.key === 'Enter' && !multiline) {
      e.preventDefault()
      commit()
    }
  }

  return (
    <span data-testid={testId} className={className}>
      {editing ? (
        multiline ? (
          <textarea
            aria-label={inputLabel}
            rows={6}
            autoFocus
            className={field}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onBlur={commit}
            onKeyDown={onKeyDown}
          />
        ) : (
          <input
            aria-label={inputLabel}
            autoFocus
            className={field}
            value={draft}
            onChange={e => setDraft(e.target.value)}
            onFocus={e => e.currentTarget.select()}
            onBlur={commit}
            onKeyDown={onKeyDown}
          />
        )
      ) : (
        <button type="button" aria-label={buttonLabel} className="max-w-full truncate text-left hover:text-white" onClick={open}>
          {value || <span className="text-white/40">{placeholder}</span>}
          {icon && (
            <span aria-hidden="true" className="ml-1 text-white/30">
              {icon}
            </span>
          )}
        </button>
      )}
    </span>
  )
}
