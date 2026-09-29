export type LinkModeState = { active: boolean; pendingId: string | null }
export type LinkModeEffect =
  | { type: 'none' }
  | { type: 'toast'; message: string }
  | { type: 'link'; dependencyId: string; dependentId: string }

export function linkModeStep(
  state: LinkModeState,
  clickedId: string | null,
): { state: LinkModeState; effect: LinkModeEffect } {
  if (!state.active) return { state, effect: { type: 'none' } }
  if (!clickedId) return { state: { active: true, pendingId: null }, effect: { type: 'none' } }
  if (!state.pendingId) {
    return {
      state: { active: true, pendingId: clickedId },
      effect: { type: 'toast', message: `pick the node that depends on ${clickedId}` },
    }
  }
  if (clickedId !== state.pendingId) {
    return {
      state: { active: true, pendingId: null },
      effect: { type: 'link', dependencyId: state.pendingId, dependentId: clickedId },
    }
  }
  return {
    state: { active: true, pendingId: null },
    effect: { type: 'toast', message: 'pick a different node' },
  }
}
