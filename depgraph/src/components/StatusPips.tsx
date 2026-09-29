'use client'
import Keycap from '@/components/Keycap'
import { STATUSES, type Status } from '@/lib/schema'

const ON: Record<Status, string> = {
  todo: 'border-slate-300/50 text-slate-200',
  doing: 'border-sky-400/60 text-sky-200',
  done: 'border-slate-400/50 text-slate-300',
  blocked: 'border-red-400/60 text-red-200',
}

export default function StatusPips({ value, onChange }: { value: Status; onChange: (status: Status) => void }) {
  return (
    <div role="radiogroup" aria-label="Status" className="flex items-center gap-1">
      {STATUSES.map((s, i) => {
        const on = s === value
        return (
          <button
            key={s}
            type="button"
            role="radio"
            aria-checked={on}
            aria-label={s}
            data-testid={`status-pip-${s}`}
            className={`inline-flex items-center gap-1 rounded-full border px-1.5 py-0.5 text-[11px] transition-colors ${
              on ? ON[s] : 'border-transparent text-white/40 hover:text-white/70'
            }`}
            onClick={() => {
              if (!on) onChange(s)
            }}
          >
            <span aria-hidden="true">{on ? '●' : '○'}</span>
            <span aria-hidden="true">{s}</span>
            <Keycap>{i + 1}</Keycap>
          </button>
        )
      })}
    </div>
  )
}
