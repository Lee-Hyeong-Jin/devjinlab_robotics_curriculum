import { Card } from './Card'

export interface FaqProps {
  id: string
  title: string
  /** `[question, answer]` pairs. The same pairs go into the page's `FAQPage` JSON-LD. */
  items: ReadonlyArray<[string, string]>
}

/**
 * Questions and answers, written out in full.
 *
 * Not an accordion: the answers are the content a reader (and a search engine) came for, and
 * text that needs a click to appear is text some of them never see.
 */
export function Faq({ id, title, items }: FaqProps) {
  return (
    <Card as="section" aria-labelledby={id}>
      <h2 id={id} className="text-primary text-xl font-bold">
        {title}
      </h2>
      <dl className="mt-3 flex flex-col">
        {items.map(([question, answer]) => (
          <div
            key={question}
            className="border-border-default border-b py-4 first:pt-1 last:border-b-0 last:pb-0"
          >
            <dt className="text-primary font-semibold">{question}</dt>
            <dd className="text-muted mt-1 max-w-3xl text-sm">{answer}</dd>
          </div>
        ))}
      </dl>
    </Card>
  )
}
