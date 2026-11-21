import type { MetadataRoute } from 'next'
import { getTranslations } from 'next-intl/server'

/**
 * Web app manifest: the name and icons a phone uses when the site is added to the home screen,
 * and what a search result or a browser tab falls back to for the site's identity.
 */
export default async function manifest(): Promise<MetadataRoute.Manifest> {
  const t = await getTranslations('app')
  return {
    name: t('title'),
    short_name: t('shortTitle'),
    description: t('description'),
    start_url: '/',
    display: 'standalone',
    background_color: 'white',
    theme_color: 'white',
    icons: [
      { src: '/icon.svg', type: 'image/svg+xml', sizes: 'any' },
      { src: '/icon-192.png', type: 'image/png', sizes: '192x192' },
      { src: '/icon-512.png', type: 'image/png', sizes: '512x512' },
    ],
  }
}
