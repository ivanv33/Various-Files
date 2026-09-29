// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest'
import { cleanup } from '@testing-library/react'
import { hotkeyName, isTypingTarget } from './useHotkeys'

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
