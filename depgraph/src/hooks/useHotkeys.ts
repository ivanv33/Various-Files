'use client'
import { useEffect, useEffectEvent } from 'react'

export type HotkeyMap = Partial<Record<string, () => void>>

export function hotkeyName(e: Pick<KeyboardEvent, 'key' | 'shiftKey' | 'metaKey' | 'ctrlKey' | 'altKey'>): string | null {
  if (e.metaKey || e.ctrlKey || e.altKey) return null
  if (e.key === 'Escape') return 'escape'
  if (e.key === 'Delete' || e.key === 'Backspace') return 'delete'
  if (/^[1-9]$/.test(e.key)) return e.key
  if (/^[a-z]$/i.test(e.key)) return (e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()
  return null
}

export function isTypingTarget(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.tagName === 'SELECT') return true
  // jsdom lacks isContentEditable, so check the attribute on the element or an ancestor.
  return target.closest('[contenteditable]:not([contenteditable="false"])') !== null
}

export function useHotkeys(map: HotkeyMap): void {
  const onKey = useEffectEvent((e: KeyboardEvent) => {
    if (e.repeat || e.defaultPrevented || isTypingTarget(e.target)) return
    const name = hotkeyName(e)
    const handler = name ? map[name] : undefined
    if (!handler) return
    e.preventDefault()
    handler()
  })
  useEffect(() => {
    const listener = (e: KeyboardEvent) => onKey(e)
    window.addEventListener('keydown', listener)
    return () => window.removeEventListener('keydown', listener)
  }, [])
}
