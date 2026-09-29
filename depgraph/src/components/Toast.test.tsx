// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, render, renderHook, screen } from '@testing-library/react'
import Toast, { useToast } from './Toast'

afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('Toast', () => {
  it('renders nothing without a message', () => {
    render(<Toast message={null} />)
    expect(screen.queryByTestId('toast')).toBeNull()
  })

  it('exposes its tone, info by default', () => {
    render(<Toast message="hello" />)
    expect(screen.getByTestId('toast').getAttribute('data-tone')).toBe('info')
    cleanup()
    render(<Toast message="cycle: a -> b -> a" tone="error" />)
    const toast = screen.getByRole('status')
    expect(toast.getAttribute('data-tone')).toBe('error')
    expect(toast.textContent).toBe('cycle: a -> b -> a')
  })
})

describe('useToast', () => {
  it('shows info by default, error on request, and clears after 3.5 s', () => {
    vi.useFakeTimers()
    const { result } = renderHook(() => useToast())
    act(() => result.current.show('hi'))
    expect(result.current).toMatchObject({ message: 'hi', tone: 'info' })
    act(() => result.current.show('bad', 'error'))
    expect(result.current).toMatchObject({ message: 'bad', tone: 'error' })
    act(() => {
      vi.advanceTimersByTime(3500)
    })
    expect(result.current.message).toBeNull()
  })
})
