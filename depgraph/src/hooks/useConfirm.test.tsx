// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { act, cleanup, renderHook } from '@testing-library/react'
import { useConfirm } from './useConfirm'

beforeEach(() => {
  vi.useFakeTimers()
})
afterEach(() => {
  cleanup()
  vi.useRealTimers()
})

describe('useConfirm', () => {
  it('first press arms only that key; second press runs the action once and disarms', () => {
    const { result } = renderHook(() => useConfirm(3000))
    const action = vi.fn()
    act(() => result.current.press('a', action))
    expect(result.current.isArmed('a')).toBe(true)
    expect(result.current.isArmed('b')).toBe(false)
    expect(action).not.toHaveBeenCalled()
    act(() => result.current.press('a', action))
    expect(action).toHaveBeenCalledTimes(1)
    expect(result.current.isArmed('a')).toBe(false)
  })

  it('disarms by itself after 3 s without acting', () => {
    const { result } = renderHook(() => useConfirm())
    const action = vi.fn()
    act(() => result.current.press('a', action))
    act(() => {
      vi.advanceTimersByTime(2999)
    })
    expect(result.current.isArmed('a')).toBe(true)
    act(() => {
      vi.advanceTimersByTime(1)
    })
    expect(result.current.isArmed('a')).toBe(false)
    expect(action).not.toHaveBeenCalled()
  })

  it('pressing another key re-arms for that key without acting', () => {
    const { result } = renderHook(() => useConfirm())
    const action = vi.fn()
    act(() => result.current.press('a', action))
    act(() => result.current.press('b', action))
    expect(result.current.isArmed('a')).toBe(false)
    expect(result.current.isArmed('b')).toBe(true)
    expect(action).not.toHaveBeenCalled()
  })

  it('reset() disarms and cancels the pending timer', () => {
    const { result } = renderHook(() => useConfirm())
    const action = vi.fn()
    act(() => result.current.press('a', action))
    act(() => result.current.reset())
    expect(result.current.isArmed('a')).toBe(false)
    act(() => result.current.press('a', action))
    act(() => {
      vi.advanceTimersByTime(2999)
    })
    expect(result.current.isArmed('a')).toBe(true)
    expect(action).not.toHaveBeenCalled()
  })
})
