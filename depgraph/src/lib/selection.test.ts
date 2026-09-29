import { describe, expect, it } from 'vitest'
import { initialSelection, selectionStep, type SelectionState } from './selection'

const none = { type: 'none' }
const selected = (id: string): SelectionState => ({ selectedId: id, arming: false })
const armed = (id: string): SelectionState => ({ selectedId: id, arming: true })

describe('selectionStep: selecting', () => {
  it('selectNode selects the node', () => {
    expect(selectionStep(initialSelection, { type: 'selectNode', id: 'a' })).toEqual({ state: selected('a'), effect: none })
    expect(selectionStep(selected('a'), { type: 'selectNode', id: 'b' })).toEqual({ state: selected('b'), effect: none })
  })

  it('background deselects', () => {
    expect(selectionStep(selected('a'), { type: 'background' })).toEqual({ state: initialSelection, effect: none })
  })

  it('clear resets everything, even while arming', () => {
    expect(selectionStep(armed('a'), { type: 'clear' })).toEqual({ state: initialSelection, effect: none })
  })
})
