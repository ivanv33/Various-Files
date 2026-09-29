// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import InlineText, { type InlineTextProps } from './InlineText'

afterEach(cleanup)

function setup(overrides: Partial<InlineTextProps> = {}) {
  const onCommit = vi.fn()
  const { unmount } = render(<InlineText value="Alpha" onCommit={onCommit} buttonLabel="Rename" inputLabel="Title" testId="hud-title" {...overrides} />)
  return { onCommit, unmount }
}

const open = (name = 'Rename') => fireEvent.click(screen.getByRole('button', { name }))
const box = (name = 'Title') => screen.getByRole('textbox', { name }) as HTMLInputElement

describe('InlineText', () => {
  it('shows the value in a button that opens a focused textbox inside the same test id', () => {
    setup()
    expect(screen.getByRole('button', { name: 'Rename' }).textContent).toContain('Alpha')
    open()
    expect(box().value).toBe('Alpha')
    expect(document.activeElement).toBe(box())
    expect(screen.getByTestId('hud-title').contains(box())).toBe(true)
  })

  it('Enter commits the trimmed value once and closes', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: '  Beta ' } })
    fireEvent.keyDown(box(), { key: 'Enter' })
    expect(onCommit.mock.calls).toEqual([['Beta']])
    expect(screen.queryByRole('textbox', { name: 'Title' })).toBeNull()
  })

  it('Esc reverts without committing', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Beta' } })
    fireEvent.keyDown(box(), { key: 'Escape' })
    expect(onCommit).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Rename' }).textContent).toContain('Alpha')
    open()
    expect(box().value).toBe('Alpha')
  })

  it('blur commits', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Gamma' } })
    fireEvent.blur(box())
    expect(onCommit.mock.calls).toEqual([['Gamma']])
  })

  it('does not commit an empty or unchanged single-line value', () => {
    const { onCommit } = setup()
    open()
    fireEvent.change(box(), { target: { value: '   ' } })
    fireEvent.keyDown(box(), { key: 'Enter' })
    open()
    fireEvent.keyDown(box(), { key: 'Enter' })
    expect(onCommit).not.toHaveBeenCalled()
  })

  it('startEditing opens the textbox immediately', () => {
    setup({ startEditing: true })
    expect(document.activeElement).toBe(box())
  })

  it('multiline: shows the placeholder, edits in a 6-row textarea, Enter adds a line, blur saves', () => {
    const { onCommit } = setup({ value: '', multiline: true, buttonLabel: 'Edit description', inputLabel: 'Description', placeholder: '▸ description…', testId: 'hud-description' })
    expect(screen.getByRole('button', { name: 'Edit description' }).textContent).toContain('▸ description…')
    open('Edit description')
    const area = box('Description') as unknown as HTMLTextAreaElement
    expect(area.tagName).toBe('TEXTAREA')
    expect(area.rows).toBe(6)
    fireEvent.change(area, { target: { value: 'line one' } })
    fireEvent.keyDown(area, { key: 'Enter' })
    expect(onCommit).not.toHaveBeenCalled()
    fireEvent.blur(area)
    expect(onCommit.mock.calls).toEqual([['line one']])
  })

  it('commits a pending edit when unmounted mid-edit without blur', () => {
    const { onCommit, unmount } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Delta' } })
    unmount()
    expect(onCommit.mock.calls).toEqual([['Delta']])
  })

  it('does not commit on unmount after Esc', () => {
    const { onCommit, unmount } = setup()
    open()
    fireEvent.change(box(), { target: { value: 'Delta' } })
    fireEvent.keyDown(box(), { key: 'Escape' })
    unmount()
    expect(onCommit).not.toHaveBeenCalled()
  })
})
