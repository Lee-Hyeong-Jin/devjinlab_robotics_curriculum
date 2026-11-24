/**
 * Regenerate the raster icons from `src/app/icon.svg`, the one source of the site's mark.
 *
 *   node scripts/make-icons.mjs            # writes the PNGs listed below
 *   python3 scripts/make-favicon.py        # then packs favicon.ico (16, 32, 48)
 *
 * Search engines and phones do not all take an SVG: Google's search results want a favicon
 * whose side is a multiple of 48px, iOS wants a 180px PNG, the manifest 192 and 512. Chromium
 * (already here for the end-to-end tests) does the rasterising, so no image library is needed.
 */
import { readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

import { chromium } from '@playwright/test'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const svg = readFileSync(join(root, 'src/app/icon.svg'), 'utf8')

/** [file, side in px, opaque background or null for transparent corners]. */
const TARGETS = [
  ['src/app/icon1.png', 96, null],
  ['src/app/icon2.png', 192, null],
  // iOS paints transparency black, so this one is filled. A PNG cannot read a CSS variable:
  // the colour is the mark's own, as written in icon.svg.
  // eslint-disable-next-line no-restricted-syntax
  ['src/app/apple-icon.png', 180, '#0b7a6b'],
  ['public/icon-192.png', 192, null],
  ['public/icon-512.png', 512, null],
  ['public/favicon-16.png', 16, null],
  ['public/favicon-32.png', 32, null],
  ['public/favicon-48.png', 48, null],
]

const browser = await chromium.launch()
try {
  for (const [file, side, background] of TARGETS) {
    const page = await browser.newPage({ viewport: { width: side, height: side } })
    await page.setContent(
      `<body style="margin:0;background:${background ?? 'transparent'}">` +
        svg.replace('<svg ', `<svg width="${side}" height="${side}" style="display:block" `) +
        '</body>',
    )
    await page.screenshot({ path: join(root, file), omitBackground: background === null })
    await page.close()
    console.log(`${file} ${side}x${side}`)
  }
} finally {
  await browser.close()
}
