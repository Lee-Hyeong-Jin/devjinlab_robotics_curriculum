/**
 * Only a same-origin path is accepted as a post-login destination, so a crafted
 * `?next=https://evil.example` cannot turn the login screen into an open redirect.
 */
export function safeNext(next: string | null | undefined): string {
  if (!next || !next.startsWith('/') || next.startsWith('//')) return '/'
  return next
}
