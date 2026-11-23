/** Pure helpers for attaching an API validation error to a form field (QA B-11). */

export type FieldMessageKey =
  'invalid' | 'required' | 'tooLong' | 'tooShort' | 'format' | 'range' | 'type'

/** `display_name` -> `displayName`: the API's field name as the form's input name. */
export function camelCase(name: string): string {
  return name.replace(/_([a-z0-9])/g, (_match, letter: string) => letter.toUpperCase())
}

/** Which `form.*` message a pydantic error type gets; anything unknown is "invalid". */
export function fieldMessageKey(type: string | undefined): FieldMessageKey {
  if (!type) return 'invalid'
  if (type === 'missing') return 'required'
  if (type === 'string_too_long' || type === 'too_long') return 'tooLong'
  if (type === 'string_too_short' || type === 'too_short') return 'tooShort'
  if (type === 'string_pattern_mismatch') return 'format'
  if (/^(greater|less)_than/.test(type)) return 'range'
  if (/_(parsing|type)$/.test(type)) return 'type'
  return 'invalid'
}
