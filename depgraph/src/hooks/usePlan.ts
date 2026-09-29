'use client'
import { useCallback, useEffect, useRef, useState } from 'react'
import { validatePlan, type Plan } from '@/lib/schema'

export type SaveState = 'idle' | 'saving' | 'saved' | 'error'

const DEBOUNCE_MS = 300

export function usePlan(slug: string | null) {
  const [plan, setPlan] = useState<Plan | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [saveError, setSaveError] = useState<string | null>(null)
  const planRef = useRef<Plan | null>(null)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const dirty = useRef(false)
  const gen = useRef(0)
  const edits = useRef(0)

  const reload = useCallback(async () => {
    if (!slug) return
    if (dirty.current) return // local edits pending; they will overwrite the file anyway
    const g = gen.current
    const e0 = edits.current
    try {
      const res = await fetch(`/api/plans/${slug}`, { cache: 'no-store' })
      if (!res.ok) throw new Error((await res.json()).errors?.join('; ') ?? res.statusText)
      const next = (await res.json()) as Plan
      if (g !== gen.current || e0 !== edits.current) return // slug changed or a local edit landed meanwhile
      planRef.current = next
      setPlan(next)
      setLoadError(null)
    } catch (e) {
      if (g !== gen.current) return
      setLoadError((e as Error).message)
    }
  }, [slug])

  const flush = useCallback(async () => {
    if (!slug || !planRef.current) return
    dirty.current = false
    const g = gen.current
    setSaveState('saving')
    try {
      const res = await fetch(`/api/plans/${slug}`, {
        method: 'PUT',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify(planRef.current),
        keepalive: true,
      })
      if (!res.ok) throw new Error(((await res.json()).errors as string[]).join('; '))
      if (g !== gen.current) return
      setSaveState('saved')
      setSaveError(null)
    } catch (e) {
      if (g !== gen.current) return
      setSaveState('error')
      setSaveError((e as Error).message)
    }
  }, [slug])

  const apply = useCallback(
    (mutate: (plan: Plan) => Plan): string[] => {
      if (!planRef.current) return ['no plan loaded']
      const next = mutate(planRef.current)
      const errors = validatePlan(next)
      if (errors.length) return errors
      planRef.current = next
      setPlan(next)
      dirty.current = true
      edits.current += 1
      if (timer.current) clearTimeout(timer.current)
      timer.current = setTimeout(flush, DEBOUNCE_MS)
      return []
    },
    [flush],
  )

  useEffect(() => {
    gen.current += 1
    planRef.current = null
    // eslint-disable-next-line react-hooks/set-state-in-effect -- state reset is tied to the gen/ref reset for the new slug subscription
    setPlan(null)
    setLoadError(null)
    setSaveState('idle')
    setSaveError(null)
    dirty.current = false
    void reload()
    if (!slug) return
    const es = new EventSource(`/api/plans/${slug}/events`)
    es.addEventListener('changed', () => void reload())
    return () => {
      es.close()
      if (timer.current) clearTimeout(timer.current)
      timer.current = null
      if (dirty.current) void flush() // body is built synchronously from planRef; gen check blocks later state writes
    }
  }, [slug, reload, flush])

  return { plan, loadError, saveState, saveError, apply, reload }
}
