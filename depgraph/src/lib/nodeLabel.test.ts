// @vitest-environment jsdom
import { describe, expect, it, vi } from 'vitest'
import { LABEL_MAX, SHAKE_MS, createLabelElement, labelFor, renderLabel, shakeLabel, syncLabels, truncateTitle } from './nodeLabel'

describe('truncateTitle', () => {
  it('keeps titles of up to 24 characters', () => {
    expect(LABEL_MAX).toBe(24)
    expect(truncateTitle('Schema + validator')).toBe('Schema + validator')
    expect(truncateTitle('x'.repeat(24))).toBe('x'.repeat(24))
  })

  it('cuts longer titles to 24 characters ending in an ellipsis', () => {
    const out = truncateTitle('Write the migration for the billing tables')
    expect(out).toBe('Write the migration for…')
    expect(Array.from(out)).toHaveLength(24)
  })

  it('drops trailing whitespace before the ellipsis', () => {
    expect(truncateTitle('Write the migration fo xxxxxxxx')).toBe('Write the migration fo…')
  })

  it('counts an emoji as one character', () => {
    expect(truncateTitle('🚀'.repeat(30))).toBe('🚀'.repeat(23) + '…')
  })

  it('accepts a custom max', () => {
    expect(truncateTitle('abcdef', 4)).toBe('abc…')
  })
})

describe('createLabelElement', () => {
  it('is a focusable button tagged with the node id', () => {
    const el = createLabelElement('schema', () => {})
    expect(el.getAttribute('data-testid')).toBe('node-label')
    expect(el.getAttribute('data-node-id')).toBe('schema')
    expect(el.getAttribute('role')).toBe('button')
    expect(el.tabIndex).toBe(0)
    expect(el.querySelector('.node-label-id')?.textContent).toBe('schema')
  })

  it('click and Enter pick the node; pointerdown does not reach the graph container', () => {
    const onPick = vi.fn()
    const graphDown = vi.fn()
    const container = document.createElement('div')
    container.addEventListener('pointerdown', graphDown)
    const el = createLabelElement('schema', onPick)
    container.append(el)
    el.dispatchEvent(new MouseEvent('click', { bubbles: true }))
    el.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }))
    el.dispatchEvent(new Event('pointerdown', { bubbles: true }))
    expect(onPick.mock.calls).toEqual([['schema'], ['schema']])
    expect(graphDown).not.toHaveBeenCalled()
  })
})

describe('renderLabel', () => {
  it('shows the cut title, uses the full title as name and tooltip, and exposes status and flags', () => {
    const el = createLabelElement('mig', () => {})
    renderLabel(el, { title: 'Write the migration for the billing tables', status: 'doing', selected: true, dim: false })
    expect(el.getAttribute('aria-label')).toBe('Write the migration for the billing tables')
    expect(el.title).toBe('Write the migration for the billing tables')
    expect(el.querySelector('.node-label-title')?.textContent).toBe('Write the migration for…')
    expect(el.dataset.status).toBe('doing')
    expect(el.dataset.selected).toBe('true')
    expect(el.dataset.dim).toBe('false')
  })

  it('falls back to the id when the title is empty', () => {
    const el = createLabelElement('mig', () => {})
    renderLabel(el, { title: '', status: 'todo', selected: false, dim: true })
    expect(el.getAttribute('aria-label')).toBe('mig')
    expect(el.querySelector('.node-label-title')?.textContent).toBe('mig')
    expect(el.dataset.dim).toBe('true')
  })
})

describe('labelFor / syncLabels', () => {
  const view = { status: 'todo' as const, selected: false, dim: false }

  it('creates one element per id and reuses it', () => {
    const labels = new Map<string, HTMLDivElement>()
    const first = labelFor(labels, 'a', () => {})
    expect(labelFor(labels, 'a', () => {})).toBe(first)
    expect(labels.size).toBe(1)
  })

  it('renders current nodes and removes labels of deleted nodes from the map and the DOM', () => {
    const labels = new Map<string, HTMLDivElement>()
    const overlay = document.createElement('div')
    syncLabels(labels, [{ id: 'a', title: 'A', ...view }, { id: 'b', title: 'B', ...view }], () => {})
    overlay.append(labels.get('a')!, labels.get('b')!)
    syncLabels(labels, [{ id: 'a', title: 'A2', ...view }], () => {})
    expect([...labels.keys()]).toEqual(['a'])
    expect(overlay.children).toHaveLength(1)
    expect(labels.get('a')!.getAttribute('aria-label')).toBe('A2')
  })
})

describe('shakeLabel', () => {
  it('sets data-shake for 600 ms and restarts when repeated', () => {
    vi.useFakeTimers()
    try {
      expect(SHAKE_MS).toBe(600)
      const el = createLabelElement('a', () => {})
      shakeLabel(el)
      expect(el.dataset.shake).toBe('true')
      vi.advanceTimersByTime(400)
      shakeLabel(el)
      vi.advanceTimersByTime(400)
      expect(el.dataset.shake).toBe('true')
      vi.advanceTimersByTime(200)
      expect(el.dataset.shake).toBeUndefined()
    } finally {
      vi.useRealTimers()
    }
  })
})
