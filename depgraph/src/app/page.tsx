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
import { addDependency, addNextNode, addNode, deleteNode, removeDependency, updateNode } from '@/lib/mutations'
import type { Plan, Status } from '@/lib/schema'
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
  const [shake, setShake] = useState<NodeSignal | null>(null)
  const toast = useToast()
  const confirmDelete = useConfirm(3000)
  const { plan, loadError, saveState, saveError, apply } = usePlan(slug)

  // A reload failure with a plan on screen keeps the last good plan; tell the user the file is invalid.
  const showToast = toast.show
  const planLoaded = plan !== null
  useEffect(() => {
    if (loadError && planLoaded) showToast(`plan file invalid: ${loadError}`, 'error')
  }, [loadError, planLoaded, showToast])

  useEffect(() => {
    fetch('/api/plans', { cache: 'no-store' })
      .then(r => {
        if (!r.ok) throw new Error(r.statusText)
        return r.json()
      })
      .then((list: PlanSummary[]) => {
        setPlans(list)
        if (!slug && list[0]) router.replace(`/?plan=${list[0].slug}`)
      })
      .catch(() => setPlans([]))
  }, [slug, router])

  const activeNode = plan?.nodes.find(n => n.id === selection.selectedId) ?? null
  const activeId = activeNode?.id ?? null
  const armed = selection.arming && activeId !== null

  // A pending delete confirmation belongs to one node in one plan; drop it when either changes.
  const resetConfirm = confirmDelete.reset
  useEffect(() => {
    resetConfirm()
  }, [activeId, slug, resetConfirm])

  // Apply a mutation. On refusal, show a red toast and shake the node it targeted.
  const attempt = (targetId: string | null, mutate: (p: Plan) => Plan): boolean => {
    const errors = apply(mutate)
    if (errors.length === 0) return true
    toast.show(errors.join('; '), 'error')
    if (targetId) setShake(s => nextSignal(s, targetId))
    return false
  }

  const dispatch = (event: SelectionEvent) => {
    const { state, effect } = selectionStep({ selectedId: activeId, arming: armed }, event)
    setSelection(state)
    if (state.selectedId !== activeId) setEditTitleFor(null)
    if (effect.type === 'toast') toast.show(effect.message)
    if (effect.type === 'link') attempt(effect.dependencyId, p => addDependency(p, effect.dependencyId, effect.dependentId))
  }

  const toggleLink = () => dispatch(armed ? { type: 'disarm' } : { type: 'armLink' })

  const focusNode = (id: string) => {
    dispatch({ type: 'focusNode', id })
    setFly(f => nextSignal(f, id))
  }

  const addAndEdit = (make: (p: Plan) => { plan: Plan; id: string }) => {
    let newId = ''
    const ok = attempt(null, p => {
      const r = make(p)
      newId = r.id
      return r.plan
    })
    if (!ok || !newId) return
    setSelection({ selectedId: newId, arming: false })
    setEditTitleFor(newId)
  }

  const handleAddNode = () => addAndEdit(p => addNode(p))

  const handleAddNext = () => {
    if (!activeId) {
      toast.show('select a node first')
      return
    }
    const from = activeId
    addAndEdit(p => addNextNode(p, from))
  }

  const setStatus = (status: Status) => {
    if (activeId) attempt(activeId, p => updateNode(p, activeId, { status }))
  }

  const handleDelete = () => {
    if (!activeId) return
    const id = activeId
    confirmDelete.press(id, () => {
      if (attempt(id, p => deleteNode(p, id))) dispatch({ type: 'clear' })
    })
  }

  useHotkeys({
    l: toggleLink,
    escape: () => {
      if (activeId && confirmDelete.isArmed(activeId)) confirmDelete.reset()
      else dispatch({ type: 'escape' })
    },
    n: handleAddNode,
    'shift+n': handleAddNext,
    '1': () => setStatus('todo'),
    '2': () => setStatus('doing'),
    '3': () => setStatus('done'),
    '4': () => setStatus('blocked'),
    delete: handleDelete,
    f: () => {
      if (activeId) setFly(f => nextSignal(f, activeId))
    },
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
      toast.show((body.errors as string[]).join('; '), 'error')
      return
    }
    router.push(`/?plan=${body.slug}`)
  }

  if (!slug) return <Empty text={plans.length ? 'redirecting…' : 'no plans yet — add a JSON file to plans/'} />
  if (loadError && !plan) return <Empty text={loadError} />
  if (!plan) return <Empty text="loading…" />

  return (
    <>
      <Graph
        plan={plan}
        selectedId={activeId}
        arming={armed}
        flyTo={fly}
        shake={shake}
        onSelect={id => dispatch(id ? { type: 'selectNode', id } : { type: 'background' })}
        onLinkRightClick={(dep, dependent) => attempt(dependent, p => removeDependency(p, dep, dependent))}
      />
      <Toolbar
        plans={plans}
        slug={slug}
        planName={plan.name}
        nodeCount={plan.nodes.length}
        onAddNode={handleAddNode}
        onNewPlan={handleNewPlan}
      />
      {plan.nodes.length === 0 && (
        <p data-testid="empty-hint" className="pointer-events-none fixed inset-x-0 top-1/2 -translate-y-1/2 text-center text-sm text-white/60">
          Press N or click + Node to place your first step.
        </p>
      )}
      {activeNode && (
        <NodeHud
          key={activeNode.id}
          plan={plan}
          node={activeNode}
          armed={armed}
          editTitle={editTitleFor === activeNode.id}
          deleteArmed={confirmDelete.isArmed(activeNode.id)}
          onChange={patch => attempt(activeNode.id, p => updateNode(p, activeNode.id, patch))}
          onToggleLink={toggleLink}
          onFocusNode={focusNode}
          onRemoveDependency={dep => attempt(activeNode.id, p => removeDependency(p, dep, activeNode.id))}
          onDelete={handleDelete}
          onAddNext={handleAddNext}
          onClose={() => dispatch({ type: 'clear' })}
        />
      )}
      <Toast message={toast.message} tone={toast.tone} />
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
