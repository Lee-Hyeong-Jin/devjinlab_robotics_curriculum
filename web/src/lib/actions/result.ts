/** The shape every form Server Action returns, so one component can render it. */
export interface ActionState {
  /** A problem message to show above the form, already localised by the API. */
  error?: string
  /** A success message for flows that stay on the page. */
  message?: string
  /** Per-field messages, keyed by input name. */
  fields?: Record<string, string>
}

export const EMPTY_ACTION_STATE: ActionState = {}
