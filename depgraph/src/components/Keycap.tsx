import type { ReactNode } from 'react'

export default function Keycap({ children }: { children: ReactNode }) {
  return (
    <kbd aria-hidden="true" className="rounded border border-white/15 bg-white/5 px-1 font-mono text-[10px] leading-4 text-white/50">
      {children}
    </kbd>
  )
}
