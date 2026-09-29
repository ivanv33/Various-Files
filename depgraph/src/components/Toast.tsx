'use client'
import { useCallback, useRef, useState } from 'react'

export function useToast() {
  const [message, setMessage] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const show = useCallback((m: string) => {
    setMessage(m)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setMessage(null), 3500)
  }, [])
  return { message, show }
}

export default function Toast({ message }: { message: string | null }) {
  if (!message) return null
  return (
    <div
      role="status"
      data-testid="toast"
      className="fixed bottom-4 left-1/2 -translate-x-1/2 rounded-md border border-amber-400/40 bg-amber-950/60 px-4 py-2 font-mono text-xs text-amber-100 backdrop-blur"
    >
      {message}
    </div>
  )
}
