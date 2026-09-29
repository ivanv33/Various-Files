// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import { LABEL_MAX, truncateTitle } from './nodeLabel'

describe('truncateTitle', () => {
  it('keeps titles of up to 24 characters', () => {
    expect(LABEL_MAX).toBe(24)
    expect(truncateTitle('Schema + validator')).toBe('Schema + validator')
    expect(truncateTitle('x'.repeat(24))).toBe('x'.repeat(24))
  })

  it('cuts longer titles to 24 characters ending in an ellipsis', () => {
    const out = truncateTitle('Write the migration for the billing tables')
    expect(out).toBe('Write the migration for…')
    expect(Array.from(out)).toHaveLength(24)
  })

  it('drops trailing whitespace before the ellipsis', () => {
    expect(truncateTitle('Write the migration fo xxxxxxxx')).toBe('Write the migration fo…')
  })

  it('counts an emoji as one character', () => {
    expect(truncateTitle('🚀'.repeat(30))).toBe('🚀'.repeat(23) + '…')
  })

  it('accepts a custom max', () => {
    expect(truncateTitle('abcdef', 4)).toBe('abc…')
  })
})
