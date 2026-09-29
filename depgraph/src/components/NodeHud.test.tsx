// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import NodeHud, { type NodeHudProps } from './NodeHud'
import type { Plan } from '@/lib/schema'

afterEach(cleanup)

const plan: Plan = {
  name: 'P',
  nodes: [
    { id: 'a', title: 'Alpha', description: '', status: 'todo', tags: [], depends_on: [] },
    { id: 'b', title: 'Beta', description: 'Some words', status: 'doing', tags: ['core'], depends_on: ['a'] },
    { id: 'c', title: 'Gamma', description: '', status: 'todo', tags: [], depends_on: ['b'] },
  ],
}
const beta = plan.nodes[1]

function setup(overrides: Partial<NodeHudProps> = {}) {
  const props: NodeHudProps = {
    plan,
    node: beta,
    armed: false,
    editTitle: false,
    deleteArmed: false,
    onChange: vi.fn(),
    onToggleLink: vi.fn(),
    onFocusNode: vi.fn(),
    onRemoveDependency: vi.fn(),
    onDelete: vi.fn(),
    onAddNext: vi.fn(),
    onClose: vi.fn(),
    ...overrides,
  }
  render(<NodeHud {...props} />)
  return props
}

const button = (name: string) => screen.getByRole('button', { name })

describe('NodeHud', () => {
  it('is the "Selected node" region with a Rename button showing the title', () => {
    setup()
    expect(screen.getByRole('region', { name: 'Selected node' })).toBe(screen.getByTestId('node-hud'))
    expect(button('Rename').textContent).toContain('Beta')
    expect(screen.getByTestId('hud-title').contains(button('Rename'))).toBe(true)
  })

  it('renaming commits the new title', () => {
    const props = setup()
    fireEvent.click(button('Rename'))
    const title = screen.getByRole('textbox', { name: 'Title' })
    fireEvent.change(title, { target: { value: 'Beta 2' } })
    fireEvent.keyDown(title, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledWith({ title: 'Beta 2' })
  })

  it('editTitle opens the title textbox focused', () => {
    setup({ editTitle: true })
    expect(document.activeElement).toBe(screen.getByRole('textbox', { name: 'Title' }))
  })

  it('status pips report the clicked status', () => {
    const props = setup()
    expect(screen.getByRole('radiogroup', { name: 'Status' })).toBeTruthy()
    fireEvent.click(screen.getByRole('radio', { name: 'done' }))
    expect(props.onChange).toHaveBeenCalledWith({ status: 'done' })
  })

  it('tag chips remove their tag; + adds a new, non-duplicate tag', () => {
    const props = setup()
    expect(screen.getByTestId('tag-core')).toBe(button('Remove tag core'))
    fireEvent.click(button('Remove tag core'))
    expect(props.onChange).toHaveBeenCalledWith({ tags: [] })
    expect(screen.getByTestId('add-tag').contains(button('Add tag'))).toBe(true)
    fireEvent.click(button('Add tag'))
    const input = screen.getByRole('textbox', { name: 'New tag' })
    fireEvent.change(input, { target: { value: 'api' } })
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledWith({ tags: ['core', 'api'] })
    fireEvent.click(button('Add tag'))
    const again = screen.getByRole('textbox', { name: 'New tag' })
    fireEvent.change(again, { target: { value: 'core' } })
    fireEvent.keyDown(again, { key: 'Enter' })
    expect(props.onChange).toHaveBeenCalledTimes(2)
  })

  it('description previews in a button and expands into a 6-row textarea that saves on blur', () => {
    const props = setup()
    expect(button('Edit description').textContent).toContain('Some words')
    expect(screen.getByTestId('hud-description').contains(button('Edit description'))).toBe(true)
    fireEvent.click(button('Edit description'))
    const area = screen.getByRole('textbox', { name: 'Description' }) as HTMLTextAreaElement
    expect(area.rows).toBe(6)
    fireEvent.change(area, { target: { value: 'New words' } })
    fireEvent.blur(area)
    expect(props.onChange).toHaveBeenCalledWith({ description: 'New words' })
  })

  it('needs chips select the dependency or remove it', () => {
    const props = setup()
    const chip = screen.getByTestId('dep-a')
    fireEvent.click(within(chip).getByRole('button', { name: 'Alpha' }))
    expect(props.onFocusNode).toHaveBeenCalledWith('a')
    fireEvent.click(within(chip).getByRole('button', { name: 'Remove dependency Alpha' }))
    expect(props.onRemoveDependency).toHaveBeenCalledWith('a')
  })

  it('unlocks chips list dependents and select them', () => {
    const props = setup()
    const chip = screen.getByTestId('unlock-c')
    expect(chip.textContent).toBe('Gamma')
    fireEvent.click(chip)
    expect(props.onFocusNode).toHaveBeenCalledWith('c')
  })

  it('names unlock chips "Select <title>"', () => {
    setup()
    expect(screen.getByRole('button', { name: 'Select Gamma' })).toBe(screen.getByTestId('unlock-c'))
  })

  it('names an unlock chip by id when the dependent has an empty title', () => {
    const untitled: Plan = { ...plan, nodes: plan.nodes.map(n => (n.id === 'c' ? { ...n, title: '' } : n)) }
    setup({ plan: untitled })
    expect(screen.getByRole('button', { name: 'Select c' })).toBe(screen.getByTestId('unlock-c'))
  })

  it('Add dependency toggles and shows a hint while armed', () => {
    const props = setup()
    expect(button('Add dependency').getAttribute('aria-pressed')).toBe('false')
    fireEvent.click(button('Add dependency'))
    expect(props.onToggleLink).toHaveBeenCalledTimes(1)
    cleanup()
    setup({ armed: true })
    expect(screen.getByTestId('link-button').getAttribute('aria-pressed')).toBe('true')
    expect(screen.getByTestId('link-hint').textContent).toBe('Pick what Beta needs')
  })

  it('delete is two-step: "Delete node", then "Confirm delete"', () => {
    const props = setup()
    expect(screen.getByTestId('delete-node')).toBe(button('Delete node'))
    fireEvent.click(button('Delete node'))
    expect(props.onDelete).toHaveBeenCalledTimes(1)
    cleanup()
    setup({ deleteArmed: true })
    expect(screen.getByTestId('delete-node')).toBe(button('Confirm delete'))
  })

  it('Close calls onClose', () => {
    const props = setup()
    fireEvent.click(screen.getByTestId('hud-close'))
    expect(button('Close')).toBe(screen.getByTestId('hud-close'))
    expect(props.onClose).toHaveBeenCalledTimes(1)
  })

  it('Add next step calls onAddNext', () => {
    const props = setup()
    expect(screen.getByTestId('add-next')).toBe(button('Add next step'))
    fireEvent.click(button('Add next step'))
    expect(props.onAddNext).toHaveBeenCalledTimes(1)
  })
})
