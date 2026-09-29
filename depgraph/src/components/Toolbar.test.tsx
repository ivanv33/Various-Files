// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import Toolbar from './Toolbar'

const { push } = vi.hoisted(() => ({ push: vi.fn() }))
vi.mock('next/navigation', () => ({ useRouter: () => ({ push }) }))

afterEach(() => {
  cleanup()
  push.mockReset()
})

const plans = [
  { slug: 'a', name: 'Plan A', nodeCount: 2 },
  { slug: 'b', name: 'Plan B', nodeCount: 0 },
]

function setup() {
  const onAddNode = vi.fn()
  const onNewPlan = vi.fn()
  render(<Toolbar plans={plans} slug="a" planName="Plan A" nodeCount={2} onAddNode={onAddNode} onNewPlan={onNewPlan} />)
  return { onAddNode, onNewPlan }
}

describe('Toolbar', () => {
  it('exposes the contract controls and no Link-mode toggle', () => {
    setup()
    expect(screen.getByTestId('plan-select')).toBe(screen.getByRole('combobox', { name: 'Plan' }))
    expect(screen.getByTestId('node-count').textContent).toBe('2 nodes')
    expect(screen.getByTestId('add-node')).toBe(screen.getByRole('button', { name: 'Add node' }))
    expect(screen.getByTestId('new-plan')).toBe(screen.getByRole('button', { name: 'New plan' }))
    expect(screen.queryByRole('button', { name: 'Link mode' })).toBeNull()
  })

  it('buttons call their handlers and the select navigates', () => {
    const { onAddNode, onNewPlan } = setup()
    fireEvent.click(screen.getByRole('button', { name: 'Add node' }))
    fireEvent.click(screen.getByRole('button', { name: 'New plan' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Plan' }), { target: { value: 'b' } })
    expect(onAddNode).toHaveBeenCalledTimes(1)
    expect(onNewPlan).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith('/?plan=b')
  })
})
