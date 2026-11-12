import { expect, test, type Page } from '@playwright/test'

/**
 * FR-9 — the English UI shows no Korean.
 *
 * Runs against the same stack as `smoke.spec.ts` (web app + API in local mode), with the
 * locale cookie set to `en`. The pages checked here are the ones whose text is either UI
 * chrome or already-translated content, so any Korean on them is a bug: a missing message
 * key, a label that renders a stored id, or an API response fetched without the reader's
 * language.
 *
 * Lesson, module and resource detail screens are deliberately not in the list: they show
 * activity titles, resource notes and quiz questions, which are translated per lesson in
 * `<lesson>.en.yaml` and still fall back to Korean where that file is missing. The Python
 * suite covers those with a content-derived allowance (`tests/test_i18n_english_build.py`).
 */

/** Hangul syllables, Jamo and compatibility Jamo — the same range the Python detector uses. */
const HANGUL = /[가-힣ᄀ-ᇿ㄰-㆏]/gu

const SCREENS = ['/login', '/', '/roadmap']

/** The locale switcher, whose own labels are autonyms and stay in their own language. */
const LANGUAGE_PICKER = '[data-locale-switcher]'

test.use({ storageState: { cookies: [], origins: [] } })

/**
 * The page's visible text with the language picker removed: its options name each
 * language in that language ("한국어"), which is the point of an autonym and is not a
 * translation gap.
 */
async function visibleText(page: Page): Promise<string> {
  return page.evaluate((selector) => {
    const clone = document.body.cloneNode(true) as HTMLElement
    clone.querySelectorAll(selector).forEach((node) => node.remove())
    // innerText needs layout, which a detached clone has none of; put it on the page.
    clone.style.position = 'absolute'
    clone.style.left = '-99999px'
    document.body.append(clone)
    const text = clone.innerText
    clone.remove()
    return text
  }, LANGUAGE_PICKER)
}

test.beforeEach(async ({ context, baseURL }) => {
  await context.addCookies([
    { name: 'NEXT_LOCALE', value: 'en', url: baseURL ?? 'http://127.0.0.1:3000' },
  ])
})

for (const path of SCREENS) {
  test(`${path} contains no Korean when the locale is English`, async ({ page }) => {
    await page.goto(path)
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()

    const text = await visibleText(page)
    const korean = [...new Set(text.match(HANGUL) ?? [])]
    expect(korean, `Korean characters on ${path}: ${korean.join(' ')}`).toEqual([])
  })
}

test('the roadmap shows translated stage labels, not the stored level ids', async ({ page }) => {
  await page.goto('/roadmap')
  const headings = await page.locator('h2').allInnerTexts()
  expect(headings.join(' ')).toMatch(/Foundation|Intermediate|Advanced|No stage/)
  expect(headings.join(' ')).not.toMatch(HANGUL)
})

test('switching the locale back to Korean still works', async ({ context, page, baseURL }) => {
  await context.clearCookies()
  await context.addCookies([
    { name: 'NEXT_LOCALE', value: 'ko', url: baseURL ?? 'http://127.0.0.1:3000' },
  ])
  await page.goto('/roadmap')
  await expect(page.getByRole('heading', { level: 1, name: '로드맵' })).toBeVisible()
})
