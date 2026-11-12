import { useTranslations } from 'next-intl'

import type { Paper } from '@/lib/api/types'

import { Chip } from './Chip'

export interface PaperListProps {
  /** `Lesson.papers`, already ordered required-first by the API. */
  papers: readonly Paper[]
}

/**
 * The papers a lesson assigns (ADR 0014).
 *
 * The registry's bibliography is already merged in, so each row only has to be laid out:
 * required/optional and the role as chips, the one-line citation underneath, and the note
 * saying what to read. A paper whose link nobody has checked says so, rather than looking
 * as trustworthy as the rest.
 */
export function PaperList({ papers }: PaperListProps) {
  const t = useTranslations('paper')
  if (papers.length === 0) return null

  return (
    <ul className="flex flex-col gap-3">
      {papers.map((paper) => (
        <li
          key={paper.id}
          className="border-border-default border-t pt-3 first:border-t-0 first:pt-0"
        >
          <div className="mb-1 flex flex-wrap items-center gap-1.5">
            <Chip tone={paper.required ? 'accent' : 'neutral'}>
              {paper.required ? t('required') : t('optional')}
            </Chip>
            {paper.role ? <Chip>{t(`role.${paper.role}`)}</Chip> : null}
            {paper.url && !paper.verified ? <Chip tone="warning">{t('unverified')}</Chip> : null}
          </div>
          {paper.url ? (
            <a
              href={paper.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent text-sm font-medium underline underline-offset-2"
            >
              {paper.title}
            </a>
          ) : (
            <span className="text-primary text-sm font-medium">{paper.title}</span>
          )}
          {paper.citation ? <p className="text-muted mt-0.5 text-xs">{paper.citation}</p> : null}
          {paper.note ? <p className="text-muted mt-1 text-xs">{paper.note}</p> : null}
        </li>
      ))}
    </ul>
  )
}
