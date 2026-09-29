import { describe, expect, it } from 'vitest'
import { linkModeStep, type LinkModeState } from './linkMode'

const off: LinkModeState = { active: false, pendingId: null }
const on: LinkModeState = { active: true, pendingId: null }

describe('linkModeStep', () => {
  it('inactive: click passes through', () => {
    expect(linkModeStep(off, 'a')).toEqual({ state: off, effect: { type: 'none' } })
  })

  it('active, first click: sets pending and hints', () => {
    expect(linkModeStep(on, 'a')).toEqual({
      state: { active: true, pendingId: 'a' },
      effect: { type: 'toast', message: 'pick the node that depends on a' },
    })
  })

  it('active, second click on a different node: link, pending cleared', () => {
    expect(linkModeStep({ active: true, pendingId: 'a' }, 'b')).toEqual({
      state: on,
      effect: { type: 'link', dependencyId: 'a', dependentId: 'b' },
    })
  })

  it('active, same node twice: toast and pending cleared', () => {
    expect(linkModeStep({ active: true, pendingId: 'a' }, 'a')).toEqual({
      state: on,
      effect: { type: 'toast', message: 'pick a different node' },
    })
  })

  it('active, background click: pending cleared, no effect', () => {
    expect(linkModeStep({ active: true, pendingId: 'a' }, null)).toEqual({ state: on, effect: { type: 'none' } })
  })
})
