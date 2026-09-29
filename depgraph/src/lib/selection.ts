export interface SelectionState {
  selectedId: string | null
  arming: boolean
}

export type SelectionEvent =
  | { type: 'selectNode'; id: string }
  | { type: 'background' }
  | { type: 'armLink' }
  | { type: 'disarm' }
  | { type: 'escape' }
  | { type: 'clear' }

export type SelectionEffect =
  | { type: 'none' }
  | { type: 'toast'; message: string }
  | { type: 'link'; dependencyId: string; dependentId: string }

export const initialSelection: SelectionState = { selectedId: null, arming: false }

const none: SelectionEffect = { type: 'none' }

export function selectionStep(state: SelectionState, event: SelectionEvent): { state: SelectionState; effect: SelectionEffect } {
  switch (event.type) {
    case 'selectNode':
      return { state: { selectedId: event.id, arming: false }, effect: none }
    case 'background':
    case 'clear':
      return { state: initialSelection, effect: none }
    default:
      return { state, effect: none }
  }
}
