'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useActionState, useState } from 'react'

import { rateCard, type ReviewState } from '@/lib/actions/quiz'
import type { Rating, ReviewCard } from '@/lib/api/types'
import { RATINGS } from '@/lib/quiz'

import { Card } from './Card'
import { Chip } from './Chip'
import { EmptyState } from './EmptyState'
import { FormMessage } from './form/FormMessage'

const EMPTY: ReviewState = {}

const TONE: Record<Rating, string> = {
  again: 'bg-surface text-danger border-danger',
  hard: 'bg-surface text-warning border-border-default',
  good: 'bg-surface text-primary border-border-default',
  easy: 'bg-accent-solid text-on-accent border-transparent',
}

/**
 * The review deck: front → flip → rate, one card at a time
 * (`POST /review/{card_id}`, frontend.md §2).
 *
 * The due list is fetched on the server; rating advances to the next card here
 * so the reader is not re-rendered back to the top of the deck each time.
 */
export function ReviewDeck({ cards }: { cards: ReviewCard[] }) {
  const t = useTranslations('review')
  const [rated, setRated] = useState<string[]>([])
  const [revealedId, setRevealedId] = useState<string | null>(null)
  const [state, formAction, pending] = useActionState(rateCard, EMPTY)

  // A saved rating drops its card from the deck; a failure leaves it in place.
  // Adjusted during render rather than in an effect, so there is no second pass.
  const justRated = state.result?.card_id
  if (justRated && !rated.includes(justRated)) {
    setRated([...rated, justRated])
  }

  const remaining = cards.filter((entry) => !rated.includes(entry.card_id))
  const card = remaining[0]
  const revealed = !!card && revealedId === card.card_id

  if (!card) {
    return (
      <EmptyState
        title={t('none')}
        action={
          <Link href="/" className="text-accent text-sm underline underline-offset-2">
            {t('title')}
          </Link>
        }
      />
    )
  }

  return (
    <div className="mx-auto max-w-xl">
      <p className="text-muted mb-3 text-sm" role="status">
        {t('due', { count: remaining.length })}
      </p>

      {state.error ? <FormMessage tone="error">{state.error}</FormMessage> : null}
      {state.message && !state.error ? (
        <p className="text-success mb-3 text-sm" role="status">
          {state.message}
        </p>
      ) : null}

      <Card aria-labelledby="review-card-front">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <Chip tone="neutral">
            {card.source === 'quiz' ? t('sourceQuiz') : t('sourceConcept')}
          </Chip>
          <Link
            href={`/lessons/${encodeURIComponent(card.lesson_id)}`}
            className="text-accent font-mono text-xs underline underline-offset-2"
          >
            {card.lesson_id}
          </Link>
        </div>

        <h2 id="review-card-front" className="text-muted text-xs font-semibold">
          {t('front')}
        </h2>
        <p className="text-primary mt-1 text-lg">{card.front}</p>

        {revealed ? (
          <>
            <h3 className="text-muted mt-5 text-xs font-semibold">{t('back')}</h3>
            <p className="text-primary mt-1">{card.back}</p>
          </>
        ) : null}

        <div className="border-border-default mt-5 border-t pt-4">
          {revealed ? (
            <form action={formAction}>
              <input type="hidden" name="cardId" value={card.card_id} />
              <fieldset>
                <legend className="text-muted mb-2 text-xs font-semibold">{t('rate')}</legend>
                <div className="flex flex-wrap gap-2">
                  {RATINGS.map((rating) => (
                    <button
                      key={rating}
                      type="submit"
                      name="rating"
                      value={rating}
                      disabled={pending}
                      className={`rounded-lg border px-4 py-2 text-sm font-medium disabled:opacity-50 ${TONE[rating]}`}
                    >
                      {t(rating)}
                    </button>
                  ))}
                </div>
              </fieldset>
            </form>
          ) : (
            <button
              type="button"
              onClick={() => setRevealedId(card.card_id)}
              className="bg-accent-solid text-on-accent rounded-lg border border-transparent px-4 py-2 text-sm font-medium"
            >
              {t('reveal')}
            </button>
          )}
        </div>
      </Card>
    </div>
  )
}
