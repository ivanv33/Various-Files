// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, within } from '@testing-library/react'
import StatusPips from './StatusPips'

afterEach(cleanup)

describe('StatusPips', () => {
  it('is a Status radiogroup with one radio per status and the current one checked', () => {
    render(<StatusPips value="doing" onChange={() => {}} />)
    const group = screen.getByRole('radiogroup', { name: 'Status' })
    const radios = within(group).getAllByRole('radio')
    expect(radios.map(r => r.getAttribute('aria-label'))).toEqual(['todo', 'doing', 'done', 'blocked'])
    expect(screen.getByRole('radio', { name: 'doing' })).toBe(screen.getByTestId('status-pip-doing'))
    expect(screen.getByTestId('status-pip-doing').getAttribute('aria-checked')).toBe('true')
    expect(screen.getByTestId('status-pip-todo').getAttribute('aria-checked')).toBe('false')
    expect(screen.getByTestId('status-pip-done').textContent).toContain('3')
  })

  it('clicking another pip reports it; clicking the current one does nothing', () => {
    const onChange = vi.fn()
    render(<StatusPips value="doing" onChange={onChange} />)
    fireEvent.click(screen.getByRole('radio', { name: 'done' }))
    fireEvent.click(screen.getByRole('radio', { name: 'doing' }))
    expect(onChange.mock.calls).toEqual([['done']])
  })
})
