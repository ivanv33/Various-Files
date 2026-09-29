// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, renderHook } from '@testing-library/react'
import { hotkeyName, isTypingTarget, useHotkeys } from './useHotkeys'

afterEach(() => {
  cleanup()
  document.body.innerHTML = ''
})

type Mods = Partial<Record<'shiftKey' | 'metaKey' | 'ctrlKey' | 'altKey', boolean>>
const k = (key: string, mods: Mods = {}) =>
  hotkeyName({ key, shiftKey: false, metaKey: false, ctrlKey: false, altKey: false, ...mods })

describe('hotkeyName', () => {
  it('names letters (lower-cased), shifted letters and digits', () => {
    expect(k('l')).toBe('l')
    expect(k('L')).toBe('l')
    expect(k('N', { shiftKey: true })).toBe('shift+n')
    expect(k('1')).toBe('1')
    expect(k('4')).toBe('4')
  })

  it('names Escape and both delete keys', () => {
    expect(k('Escape')).toBe('escape')
    expect(k('Delete')).toBe('delete')
    expect(k('Backspace')).toBe('delete')
  })

  it('ignores other keys and any Meta/Ctrl/Alt chord', () => {
    expect(k('Enter')).toBeNull()
    expect(k('ArrowUp')).toBeNull()
    expect(k('l', { metaKey: true })).toBeNull()
    expect(k('l', { ctrlKey: true })).toBeNull()
    expect(k('l', { altKey: true })).toBeNull()
  })
})

describe('isTypingTarget', () => {
  it('is true for text entry elements and false otherwise', () => {
    const make = (html: string) => {
      document.body.innerHTML = html
      return document.body.firstElementChild
    }
    expect(isTypingTarget(make('<input />'))).toBe(true)
    expect(isTypingTarget(make('<textarea></textarea>'))).toBe(true)
    expect(isTypingTarget(make('<select><option>a</option></select>'))).toBe(true)
    expect(isTypingTarget(make('<div contenteditable="true"><b>x</b></div>')?.firstElementChild ?? null)).toBe(true)
    expect(isTypingTarget(make('<button>x</button>'))).toBe(false)
    expect(isTypingTarget(window)).toBe(false)
    expect(isTypingTarget(null)).toBe(false)
  })
})

describe('useHotkeys', () => {
  it('calls the bound handler and prevents the default action', () => {
    const l = vi.fn()
    renderHook(() => useHotkeys({ l }))
    expect(fireEvent.keyDown(window, { key: 'l' })).toBe(false)
    expect(l).toHaveBeenCalledTimes(1)
  })

  it('ignores keys typed into inputs and keys with no binding', () => {
    const l = vi.fn()
    renderHook(() => useHotkeys({ l }))
    const input = document.createElement('input')
    document.body.append(input)
    expect(fireEvent.keyDown(input, { key: 'l' })).toBe(true)
    expect(fireEvent.keyDown(window, { key: 'x' })).toBe(true)
    expect(l).not.toHaveBeenCalled()
  })

  it('uses the latest handlers after a rerender and detaches on unmount', () => {
    const first = vi.fn()
    const second = vi.fn()
    const { rerender, unmount } = renderHook(({ fn }) => useHotkeys({ escape: fn }), { initialProps: { fn: first } })
    rerender({ fn: second })
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(first).not.toHaveBeenCalled()
    expect(second).toHaveBeenCalledTimes(1)
    unmount()
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(second).toHaveBeenCalledTimes(1)
  })
})
