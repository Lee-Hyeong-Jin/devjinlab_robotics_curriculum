/**
 * Serializable description of a form control.
 *
 * Forms are Client Components (they hold the action state) while the pages that
 * use them are Server Components, so everything crossing that boundary must be
 * serializable — a render prop is not. The page passes already-translated
 * labels in these specs.
 */
export type FieldKind =
  'text' | 'email' | 'password' | 'number' | 'checkbox' | 'select' | 'checkboxGroup'

export interface FieldOption {
  value: string
  label: string
  /** Rendered in a monospace span — for scopes and other literal values. */
  mono?: boolean
}

export interface FieldSpec {
  name: string
  label: string
  kind?: FieldKind
  defaultValue?: string
  required?: boolean
  autoComplete?: string
  minLength?: number
  min?: number
  max?: number
  hint?: string
  placeholder?: string
  /** For `select` and `checkboxGroup`. */
  options?: FieldOption[]
  /**
   * For `checkboxGroup`: each option becomes an input named
   * `${name}:${option.value}`, which is what the Server Action reads.
   */
  optionNamePrefix?: boolean
}
