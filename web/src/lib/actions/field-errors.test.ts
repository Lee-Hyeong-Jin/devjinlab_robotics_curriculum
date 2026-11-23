import { describe, expect, it } from 'vitest'

import { camelCase, fieldMessageKey } from './field-errors'

describe('field errors', () => {
  it('names the form input for an API field', () => {
    expect(camelCase('display_name')).toBe('displayName')
    expect(camelCase('expires_in_days')).toBe('expiresInDays')
    expect(camelCase('email')).toBe('email')
  })

  it('picks a message for each kind of refusal', () => {
    expect(fieldMessageKey('string_pattern_mismatch')).toBe('format')
    expect(fieldMessageKey('string_too_long')).toBe('tooLong')
    expect(fieldMessageKey('string_too_short')).toBe('tooShort')
    expect(fieldMessageKey('less_than_equal')).toBe('range')
    expect(fieldMessageKey('greater_than_equal')).toBe('range')
    expect(fieldMessageKey('int_parsing')).toBe('type')
    expect(fieldMessageKey('missing')).toBe('required')
    expect(fieldMessageKey('value_error')).toBe('invalid')
    expect(fieldMessageKey(undefined)).toBe('invalid')
  })
})
