'use client'
import dynamic from 'next/dynamic'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense, useEffect, useState } from 'react'
import NodeHud from '@/components/NodeHud'
import SaveIndicator from '@/components/SaveIndicator'
import Toast, { useToast } from '@/components/Toast'
import Toolbar from '@/components/Toolbar'
import { useConfirm } from '@/hooks/useConfirm'
import { useHotkeys } from '@/hooks/useHotkeys'
import { usePlan } from '@/hooks/usePlan'
import { addDependency, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan } from '@/lib/schema'
import {
  initialSelection,
  nextSignal,
  selectionStep,
  type NodeSignal,
  type SelectionEvent,
  type SelectionState,
} from '@/lib/selection'
import type { PlanSummary } from '@/lib/store'

const Graph = dynamic(() => import('@/components/Graph'), { ssr: false })

function Workspace() {
  const params = useSearchParams()
  const router = useRouter()
  const slug = params.get('plan')
  const [plans, setPlans] = useState<PlanSummary[]>([])
  const [selection, setSelection] = useState<SelectionState>(initialSelection)
  const [editTitleFor, setEditTitleFor] = useState<string | null>(null)
  const [fly, setFly] = useState<NodeSignal | null>(null)
  const toast = useToast()
  const confirmDelete = useConfirm(3000)
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

  // A pending delete confirmation belongs to one node in one plan; drop it when either changes.
  const resetConfirm = confirmDelete.reset
  useEffect(() => {
    resetConfirm()
  }, [activeId, slug, resetConfirm])

  const report = (errors: string[]) => {
    if (errors.length) toast.show(errors.join('; '))
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (state.selectedId !== activeId) setEditTitleFor(null)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') report(apply(p => addDependency(p, effect.dependencyId, effect.dependentId)))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  const focusNode = (id: string) => {
    dispatch({ type: 'focusNode', id })
    setFly(f => nextSignal(f, id))
  }

  const addAndEdit = (make: (p: Plan) => { plan: Plan; id: string }) => {
    let newId = ''
    const errors = apply(p => {
      const r = make(p)
      newId = r.id
      return r.plan
    })
    report(errors)
    if (errors.length || !newId) return
    setSelection({ selectedId: newId, arming: false })
    setEditTitleFor(newId)
  }

  const handleAddNode = () => addAndEdit(p => addNode(p))

  const handleDelete = () => {
    if (!activeId) return
    const id = activeId
    confirmDelete.press(id, () => {
      report(apply(p => deleteNode(p, id)))
      dispatch({ type: 'clear' })
    })
  }

  useHotkeys({
    l: toggleLink,
    escape: () => dispatch({ type: 'escape' }),
  })

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
        flyTo={fly}
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
      {activeNode && (
        <NodeHud
          key={activeNode.id}
          plan={plan}
          node={activeNode}
          armed={armed}
          editTitle={editTitleFor === activeNode.id}
          deleteArmed={confirmDelete.isArmed(activeNode.id)}
          onChange={patch => report(apply(p => updateNode(p, activeNode.id, patch)))}
          onToggleLink={toggleLink}
          onFocusNode={focusNode}
          onRemoveDependency={dep => report(apply(p => removeDependency(p, dep, activeNode.id)))}
          onDelete={handleDelete}
          onClose={() => dispatch({ type: 'clear' })}
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
