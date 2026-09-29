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
      if (state.arming && state.selectedId) {
        if (event.id === state.selectedId) {
          return { state, effect: { type: 'toast', message: 'a node cannot depend on itself' } }
        }
        return { state, effect: { type: 'link', dependencyId: event.id, dependentId: state.selectedId } }
      }
      return { state: { selectedId: event.id, arming: false }, effect: none }
    case 'background':
    case 'escape':
      if (state.arming) return { state: { ...state, arming: false }, effect: none }
      return { state: initialSelection, effect: none }
    case 'armLink':
      if (!state.selectedId) return { state, effect: { type: 'toast', message: 'select a node first' } }
      return { state: { ...state, arming: true }, effect: none }
    case 'disarm':
      return { state: { ...state, arming: false }, effect: none }
    case 'clear':
      return { state: initialSelection, effect: none }
  }
}
