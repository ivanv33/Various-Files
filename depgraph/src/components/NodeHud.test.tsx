// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import NodeHud, { type NodeHudProps } from './NodeHud'
import type { PlanNode } from '@/lib/schema'

afterEach(cleanup)

const node: PlanNode = { id: 'b', title: 'Beta', description: '', status: 'doing', tags: [], depends_on: [] }

function setup(overrides: Partial<NodeHudProps> = {}) {
  const props: NodeHudProps = { node, armed: false, onToggleLink: vi.fn(), onClose: vi.fn(), ...overrides }
  render(<NodeHud {...props} />)
  return props
}

describe('NodeHud shell', () => {
  it('is the "Selected node" region', () => {
    setup()
    expect(screen.getByRole('region', { name: 'Selected node' })).toBe(screen.getByTestId('node-hud'))
  })

  it('Add dependency is a toggle button', () => {
    const props = setup()
    const arm = screen.getByRole('button', { name: 'Add dependency' })
    expect(arm).toBe(screen.getByTestId('link-button'))
    expect(arm.getAttribute('aria-pressed')).toBe('false')
    expect(screen.queryByTestId('link-hint')).toBeNull()
    fireEvent.click(arm)
    expect(props.onToggleLink).toHaveBeenCalledTimes(1)
  })

  it('while armed, the button is pressed and a status hint names the node', () => {
    setup({ armed: true })
    expect(screen.getByTestId('link-button').getAttribute('aria-pressed')).toBe('true')
    const hint = screen.getByTestId('link-hint')
    expect(hint.getAttribute('role')).toBe('status')
    expect(hint.textContent).toBe('Pick what Beta needs')
  })

  it('Close calls onClose', () => {
    const props = setup()
    fireEvent.click(screen.getByRole('button', { name: 'Close' }))
    expect(screen.getByTestId('hud-close')).toBeTruthy()
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })
})
