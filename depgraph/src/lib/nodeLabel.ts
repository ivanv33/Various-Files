import type { Status } from '@/lib/schema'

export const LABEL_MAX = 24

export interface LabelView {
  title: string
  status: Status
  selected: boolean
  dim: boolean
}

export interface LabelNode extends LabelView {
  id: string
}

export function truncateTitle(title: string, max = LABEL_MAX): string {
  const chars = Array.from(title)
  if (chars.length <= max) return title
  return chars.slice(0, max - 1).join('').trimEnd() + '…'
}

export function createLabelElement(id: string, onPick: (id: string) => void): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'node-label'
  el.setAttribute('data-testid', 'node-label')
  el.setAttribute('data-node-id', id)
  el.setAttribute('role', 'button')
  el.tabIndex = 0
  const title = document.createElement('span')
  title.className = 'node-label-title'
  const idLine = document.createElement('span')
  idLine.className = 'node-label-id'
  idLine.textContent = id
  el.append(title, idLine)
  // The graph container starts a click on pointerdown; stopping it here keeps a label click from also
  // registering as a background click (which would deselect).
  el.addEventListener('pointerdown', e => e.stopPropagation())
  el.addEventListener('click', e => {
    e.stopPropagation()
    onPick(id)
  })
  el.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      onPick(id)
    }
  })
  return el
}

export function renderLabel(el: HTMLElement, view: LabelView): void {
  const name = view.title || el.getAttribute('data-node-id') || ''
  el.setAttribute('aria-label', name)
  el.title = name
  el.dataset.status = view.status
  el.dataset.selected = String(view.selected)
  el.dataset.dim = String(view.dim)
  const title = el.querySelector('.node-label-title')
  if (title) title.textContent = truncateTitle(name)
}

export function labelFor(labels: Map<string, HTMLDivElement>, id: string, onPick: (id: string) => void): HTMLDivElement {
  let el = labels.get(id)
  if (!el) {
    el = createLabelElement(id, onPick)
    labels.set(id, el)
  }
  return el
}

export function syncLabels(labels: Map<string, HTMLDivElement>, nodes: LabelNode[], onPick: (id: string) => void): void {
  const ids = new Set(nodes.map(n => n.id))
  for (const [id, el] of labels) {
    if (!ids.has(id)) {
      el.remove()
      labels.delete(id)
    }
  }
  for (const n of nodes) renderLabel(labelFor(labels, n.id, onPick), n)
}
