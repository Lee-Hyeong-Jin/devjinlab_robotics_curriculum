import { headers } from 'next/headers'

import { NONCE_HEADER } from '@/middleware'

export interface JsonLdProps {
  /** A schema.org object (or a list of them) to embed. */
  data: Record<string, unknown> | Record<string, unknown>[]
}

/**
 * A schema.org block as `application/ld+json`.
 *
 * It carries the request nonce: the CSP is nonce-based (frontend.md §5.2) and browsers apply
 * `script-src` to a `<script>` element whatever its type, so without the nonce the block is
 * dropped and the structured data never ships.
 *
 * `JSON.stringify` is the only thing that reaches the page, and `<` is escaped so a title
 * containing `</script>` cannot break out of the block.
 */
export async function JsonLd({ data }: JsonLdProps) {
  const nonce = (await headers()).get(NONCE_HEADER) ?? undefined
  const json = JSON.stringify(data).replace(/</g, '\\u003c')
  return (
    <script type="application/ld+json" nonce={nonce} dangerouslySetInnerHTML={{ __html: json }} />
  )
}
