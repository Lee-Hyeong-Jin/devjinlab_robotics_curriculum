import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'

import { EmptyState } from '@/components/EmptyState'
import { PageHeader } from '@/components/PageHeader'
import { ReviewDeck, type DeckCard } from '@/components/ReviewDeck'
import { getDueCards, getLessonNames } from '@/lib/api/queries'
import { signInIfRequired } from '@/lib/auth'
import { renderInlineMarkdown } from '@/lib/markdown/render'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('review')
  return { title: t('title') }
}

/** Review — `GET /review/due` then `POST /review/{card_id}` (frontend.md §2). */
export default async function ReviewPage() {
  const t = await getTranslations('review')
  const cards = await getDueCards()

  if (!cards) {
    // Nothing to show an anonymous reader but the way in (QA B-25).
    await signInIfRequired('/review')
    return (
      <>
        <PageHeader title={t('title')} subtitle={t('subtitle')} />
        <EmptyState title={t('unavailable')} />
      </>
    )
  }

  const names = cards.length > 0 ? await getLessonNames() : {}
  const deck: DeckCard[] = cards.map((card) => ({
    ...card,
    lessonTitle: names[card.lesson_id]?.title,
    frontBody: renderInlineMarkdown(card.front),
    backBody: renderInlineMarkdown(card.back),
  }))

  return (
    <>
      <PageHeader title={t('title')} subtitle={t('subtitle')} />
      <ReviewDeck cards={deck} />
    </>
  )
}
