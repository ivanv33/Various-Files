'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import SaveIndicator from '@/components/SaveIndicator'
import NodePanel from '@/components/NodePanel'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { usePlan } from '@/hooks/usePlan'
import { addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const toast = useToast()
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

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const handleAddNode = () => {
    let newId = ''
    report(
      apply(p => {
        const r = addNode(p)
        newId = r.id
        return r.plan
      }),
    )
    if (newId) setSelectedId(newId)
  }

  const handleNewPlan = async () => {
    const name = window.prompt('Plan name')
    if (!name) return
    const res = await fetch('/api/plans', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ name }),
    })
    const body = await res.json()
    if (!res.ok) {
      toast.show((body.errors as string[]).join('; '))
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={selectedId}
        onSelect={setSelectedId}
        onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        linkMode={false}
        onToggleLinkMode={() => {
          // wired in Slice 4
        }}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {selectedId && (
        <NodePanel
          plan={plan}
          nodeId={selectedId}
          onChange={patch => apply(p => updateNode(p, selectedId, patch))}
          onDelete={() => {
            report(apply(p => deleteNode(p, selectedId)))
            setSelectedId(null)
          }}
          onClose={() => setSelectedId(null)}
        />
      )}
      <Toast message={toast.message} />
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
