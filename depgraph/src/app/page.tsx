'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import NodePanel from '@/components/NodePanel'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import { initialSelection, selectionStep, type SelectionEvent, type SelectionState } from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
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

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') report(apply(p => addDependency(p, effect.dependencyId, effect.dependentId)))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
  })

  const handleAddNode = () => {
    let newId = ''
    const errors = apply(p => {
      const r = addNode(p)
      newId = r.id
      return r.plan
    })
    report(errors)
    if (!errors.length && newId) setSelection({ selectedId: newId, arming: false })
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
        selectedId={activeId}
        arming={armed}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => report(apply(p => removeDependency(p, dep, dependent)))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {activeId && !armed && (
        <NodePanel
          key={activeId}
          plan={plan}
          nodeId={activeId}
          onChange={patch => apply(p => updateNode(p, activeId, patch))}
          onDelete={() => {
            report(apply(p => deleteNode(p, activeId)))
            dispatch({ type: 'clear' })
          }}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      {activeNode && (
        <NodeHud node={activeNode} armed={armed} onToggleLink={toggleLink} onClose={() => dispatch({ type: 'clear' })} />
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
