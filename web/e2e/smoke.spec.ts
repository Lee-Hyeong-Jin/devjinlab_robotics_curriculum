import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

/**
 * Smoke + accessibility pass over the read screens.
 *
 * Needs the web app built and started against an API in **local** mode (the
 * default, `RC_AUTH_MODE=local`): these screens are visited signed-out, and a
 * server-mode API would correctly redirect every one of them to `/login`.
 * The signed-in flow of AC-WEB.1 lives in `journey.spec.ts`, which needs a
 * server-mode API instead.
 */

const AXE_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']

/** Serious and critical axe violations, as `id: help` strings (AC-A11Y.1). */
async function blockingViolations(page: Page): Promise<string[]> {
  const results = await new AxeBuilder({ page }).withTags(AXE_TAGS).analyze()
  return results.violations
    .filter((violation) => ['serious', 'critical'].includes(violation.impact ?? ''))
    .map((violation) => `${violation.id}: ${violation.help}`)
}

const SCREENS = [
  { path: '/', heading: /대시보드|Dashboard/ },
  { path: '/roadmap', heading: /로드맵|Roadmap/ },
  { path: '/resources', heading: /자료실|Resources/ },
  { path: '/login', heading: /로그인|Sign in/ },
]

for (const screen of SCREENS) {
  test(`${screen.path} renders and has no serious axe violation`, async ({ page }) => {
    await page.goto(screen.path)
    await expect(page.getByRole('heading', { level: 1, name: screen.heading })).toBeVisible()

    expect(await blockingViolations(page), `axe violations on ${screen.path}`).toEqual([])
  })

  test(`${screen.path} has no serious axe violation in dark mode (AC-A11Y.2)`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'dark' })
    await page.goto(screen.path)
    expect(await blockingViolations(page), `dark-mode axe violations on ${screen.path}`).toEqual([])
  })
}

test('the skip link is the first thing a keyboard reaches', async ({ page }) => {
  await page.goto('/')
  await page.keyboard.press('Tab')
  const focused = page.locator(':focus')
  await expect(focused).toHaveAttribute('href', '#main')
})

test('the top navigation reaches the roadmap by keyboard only', async ({ page }) => {
  await page.goto('/')
  const roadmap = page.getByRole('link', { name: /로드맵|Roadmap/ })
  await roadmap.focus()
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/\/roadmap$/)
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
})

test('opening a module leads to a lesson with its study-method card', async ({ page }) => {
  await page.goto('/roadmap')
  await page.locator('a[href^="/modules/"]').first().click()
  await page.waitForURL(/\/modules\/[^/]+$/)

  const moduleId = new URL(page.url()).pathname.split('/')[2]
  await page.locator(`a[href^="/modules/${moduleId}/"]`).first().click()
  await page.waitForURL(/\/modules\/[^/]+\/[^/]+$/)
  await expect(page.getByRole('heading', { name: /이 단계 공부법|How to study/ })).toBeVisible()

  // The lesson body renders KaTeX as MathML and highlights code (AC-WEB.2).
  await expect(page.locator('.markdown-body').first()).toBeVisible()
  // The lesson screen is one of the screens AC-A11Y.1 names.
  expect(await blockingViolations(page), 'axe violations on the lesson screen').toEqual([])
})

/**
 * Regression for the display-math break: a `$$` block written with content on the
 * marker line used to leave the rest of the lesson as raw TeX on the page.
 */
test('every "핵심 수식" lesson renders its formulas, with no TeX left on the page', async ({
  page,
}) => {
  const lessons = [
    'm1-coordinate-transforms',
    'm2-inverse-kinematics',
    'm3-pid-control',
    'm5-kalman-filter-ekf',
  ]
  for (const lessonId of lessons) {
    await page.goto(`/lessons/${lessonId}`)
    const body = page.locator('.markdown-body').last()
    await expect(body).toBeVisible()

    // KaTeX renders to MathML; a failed formula would carry `katex-error`.
    expect(await page.locator('.katex-error').count(), `${lessonId}: katex errors`).toBe(0)
    expect(await body.locator('math').count(), `${lessonId}: formulas`).toBeGreaterThan(5)
    expect(
      await body.locator('math[display="block"]').count(),
      `${lessonId}: display formulas`,
    ).toBeGreaterThan(0)

    // Visible text, with the MathML TeX annotation (never displayed) removed.
    const leftover = await body.evaluate((node) => {
      const clone = node.cloneNode(true) as HTMLElement
      clone.querySelectorAll('annotation, annotation-xml, pre').forEach((n) => n.remove())
      const text = clone.textContent ?? ''
      return [...text.matchAll(/\$[^$\n]{1,60}\$|\\(begin|end|frac|qquad|mathbf)/g)].map(
        (m) => m[0],
      )
    })
    expect(leftover, `${lessonId}: raw TeX on the page`).toEqual([])
  }
})

test('the lesson screen passes axe in dark mode too', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' })
  await page.goto('/roadmap')
  await page.locator('a[href^="/modules/"]').first().click()
  await page.waitForURL(/\/modules\/[^/]+$/)
  const moduleId = new URL(page.url()).pathname.split('/')[2]
  await page.locator(`a[href^="/modules/${moduleId}/"]`).first().click()
  await page.waitForURL(/\/modules\/[^/]+\/[^/]+$/)
  expect(await blockingViolations(page), 'dark-mode axe violations on the lesson').toEqual([])
})

test('dark mode keeps the page readable', async ({ page }) => {
  await page.emulateMedia({ colorScheme: 'dark' })
  await page.goto('/')
  const background = await page.evaluate(() =>
    getComputedStyle(document.body).getPropertyValue('background-color'),
  )
  // The dark token is a near-black; light would be near-white.
  expect(background).not.toBe('rgb(247, 248, 250)')
})
