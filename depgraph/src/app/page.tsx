'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import SaveIndicator from '@/components/SaveIndicator'
import { usePlan } from '@/hooks/usePlan'
import { removeDependency } from '@/lib/mutations'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => r.json())
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
  }, [slug, router])

  useEffect(() => {
    if (plan && selectedId && !plan.nodes.some(n => n.id === selectedId)) setSelectedId(null)
  }, [plan, selectedId])

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onLinkRightClick={(dep, dependent) => apply(p => removeDependency(p, dep, dependent))}
      />
      <div className="pointer-events-none fixed left-4 top-4 font-mono text-xs text-white/60">
        {plan.name} · <span data-testid="node-count">{plan.nodes.length} nodes</span>
        {selectedId ? ` · selected ${selectedId}` : ''}
      </div>
      <SaveIndicator state={saveState} error={saveError} />
    </>
  )
}

function Empty({ text }: { text: string }) {
  return <div className="flex h-full items-center justify-center font-mono text-sm text-white/50">{text}</div>
}

export default function Page() {
  return (
    <Suspense>
      <Workspace />
    </Suspense>
  )
}
