'use client'
import { useCallback, useRef, useState } from 'react'

export type ToastTone = 'info' | 'error'

export function useToast() {
  const [state, setState] = useState<{ message: string | null; tone: ToastTone }>({ message: null, tone: 'info' })
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const show = useCallback((message: string, tone: ToastTone = 'info') => {
    setState({ message, tone })
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setState(s => ({ ...s, message: null })), 3500)
  }, [])
  return { message: state.message, tone: state.tone, show }
}

export default function Toast({ message, tone = 'info' }: { message: string | null; tone?: ToastTone }) {
  if (!message) return null
  const colors = tone === 'error' ? 'border-red-400/50 text-red-100' : 'border-amber-400/40 text-amber-100'
  return (
    <div
      role="status"
      data-testid="toast"
      data-tone={tone}
      className={`fixed left-1/2 top-4 z-20 -translate-x-1/2 glass rounded-lg px-4 py-2 text-xs ${colors}`}
    >
      {message}
    </div>
  )
}
