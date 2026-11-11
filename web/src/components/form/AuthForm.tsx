'use client'

import { useActionState, type ReactNode } from 'react'

import { EMPTY_ACTION_STATE, type ActionState } from '@/lib/actions/result'

import { FormMessage } from './FormMessage'

export interface AuthFormProps {
  action: (previous: ActionState, form: FormData) => Promise<ActionState>
  /** Rendered with the current state so fields can show their own errors. */
  children: (state: ActionState) => ReactNode
  /** Shown above the form before the first submit (e.g. "가입이 완료됐습니다"). */
  notice?: string
}

/**
 * Client wrapper around a form Server Action: keeps the returned `ActionState`
 * and renders form-level and per-field messages.
 */
export function AuthForm({ action, children, notice }: AuthFormProps) {
  const [state, formAction] = useActionState(action, EMPTY_ACTION_STATE)
  return (
    <form action={formAction} className="flex flex-col gap-4" noValidate>
      {notice && !state.error && !state.message ? (
        <FormMessage tone="success">{notice}</FormMessage>
      ) : null}
      {state.error ? <FormMessage tone="error">{state.error}</FormMessage> : null}
      {state.message ? <FormMessage tone="success">{state.message}</FormMessage> : null}
      {children(state)}
    </form>
  )
}
