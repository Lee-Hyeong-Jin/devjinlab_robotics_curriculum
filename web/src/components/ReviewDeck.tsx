'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useActionState, useEffect, useRef, useState, type ReactNode } from 'react'

import { rateCard, type ReviewState } from '@/lib/actions/quiz'
import type { Rating, ReviewCard } from '@/lib/api/types'
import { RATINGS } from '@/lib/quiz'

import { Card } from './Card'
import { Chip } from './Chip'
import { EmptyState } from './EmptyState'
import { FormMessage } from './form/FormMessage'
import { MarkdownBody } from './MarkdownBody'

/**
 * A due card whose two sides were rendered on the server with the lesson
 * Markdown pipeline — they carry inline KaTeX (`잡음은 $1/\sqrt{N}$ 로 감소`).
 */
export interface DeckCard extends ReviewCard {
  frontBody: ReactNode
  backBody: ReactNode
  /** The lesson's title; the id is shown only when the title could not be looked up. */
  lessonTitle?: string
}

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
export function ReviewDeck({ cards }: { cards: DeckCard[] }) {
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

  // Keyboard focus follows the card. Flipping removes the button that was pressed, and the
  // browser then drops focus to the top of the document: every card started with a walk back
  // through the whole page (QA B-27). Flipping moves focus to the first rating, and rating
  // moves it to the next card's flip button.
  const revealRef = useRef<HTMLButtonElement>(null)
  const firstRatingRef = useRef<HTMLButtonElement>(null)
  const interacted = useRef(false)
  const cardId = card?.card_id
  useEffect(() => {
    if (!interacted.current) return // never steal focus on the first render
    if (revealed) firstRatingRef.current?.focus()
    else revealRef.current?.focus()
  }, [revealed, cardId])

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
            className={`text-accent text-xs underline underline-offset-2 ${card.lessonTitle ? '' : 'font-mono'}`}
          >
            {card.lessonTitle ?? card.lesson_id}
          </Link>
        </div>

        <h2 id="review-card-front" className="text-muted text-xs font-semibold">
          {t('front')}
        </h2>
        <MarkdownBody className="mt-1 text-lg">{card.frontBody ?? card.front}</MarkdownBody>

        {revealed ? (
          <>
            <h3 className="text-muted mt-5 text-xs font-semibold">{t('back')}</h3>
            <MarkdownBody className="mt-1">{card.backBody ?? card.back}</MarkdownBody>
          </>
        ) : null}

        <div className="border-border-default mt-5 border-t pt-4">
          {revealed ? (
            <form action={formAction}>
              <input type="hidden" name="cardId" value={card.card_id} />
              <fieldset>
                <legend className="text-muted mb-2 text-xs font-semibold">{t('rate')}</legend>
                <div className="flex flex-wrap gap-2">
                  {RATINGS.map((rating, index) => (
                    <button
                      key={rating}
                      ref={index === 0 ? firstRatingRef : undefined}
                      type="submit"
                      name="rating"
                      value={rating}
                      disabled={pending}
                      className={`min-h-11 rounded-lg border px-4 py-2 text-sm font-medium disabled:opacity-50 ${TONE[rating]}`}
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
              ref={revealRef}
              onClick={() => {
                interacted.current = true
                setRevealedId(card.card_id)
              }}
              className="bg-accent-solid text-on-accent min-h-11 rounded-lg border border-transparent px-4 py-2 text-sm font-medium"
            >
              {t('reveal')}
            </button>
          )}
        </div>
      </Card>
    </div>
  )
}
