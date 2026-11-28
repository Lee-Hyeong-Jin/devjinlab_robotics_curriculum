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
  // `roadmap.courseTitle` names the course first, and the English word is lower-case there.
  { path: '/roadmap', heading: /로드맵|roadmap/i },
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

test('every page response carries the security headers, and the CSP breaks nothing', async ({
  page,
}) => {
  const problems: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') problems.push(message.text())
  })
  page.on('pageerror', (error) => problems.push(String(error)))

  const response = await page.goto('/')
  const headers = response?.headers() ?? {}
  expect(headers['x-content-type-options']).toBe('nosniff')
  expect(headers['x-frame-options']).toBe('DENY')
  expect(headers['referrer-policy']).toBe('strict-origin-when-cross-origin')
  expect(headers['permissions-policy']).toContain('camera=()')
  expect(headers['cross-origin-opener-policy']).toBe('same-origin')

  const csp = headers['content-security-policy'] ?? ''
  expect(csp).toContain("frame-ancestors 'none'")
  expect(csp).toContain("object-src 'none'")
  expect(csp).toContain("base-uri 'self'")
  expect(csp).toMatch(/script-src [^;]*'nonce-[^']+'/)
  expect(csp).not.toContain("'unsafe-eval'")
  // HSTS is for HTTPS only, and the suite runs over plain HTTP.
  expect(headers['strict-transport-security']).toBeUndefined()

  // The nonce-based policy must not block Next's own bundles: hydration is what makes the
  // theme toggle work, and the pre-paint inline script is what sets `data-theme`.
  await page.getByRole('button', { name: /^다크$|^Dark$/ }).click()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  expect(problems, 'console errors (a blocked script shows up here)').toEqual([])
})

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

test('every course is reachable from the roadmap and the dashboard', async ({ page }) => {
  await page.goto('/roadmap')
  const tabs = page.locator('a[href^="/roadmap?course="]')
  const count = await tabs.count()
  if (count === 0) {
    // A single-course deployment shows no tab bar; nothing else to check.
    return
  }
  expect(count, 'a tab bar means more than one course').toBeGreaterThan(1)
  await expect(page.locator('a[aria-current="page"][href^="/roadmap?course="]')).toHaveCount(1)

  // Switching to the last course shows that course's modules, not the default one's.
  const before = await page.locator('a[href^="/modules/"]').count()
  await tabs.last().click()
  await page.waitForURL(/\/roadmap\?course=/)
  await expect(page.locator('a[aria-current="page"][href^="/roadmap?course="]')).toHaveCount(1)
  const modules = page.locator('a[href^="/modules/"]')
  expect(await modules.count(), 'the second course has modules of its own').toBeGreaterThan(0)
  await modules.first().click()
  await page.waitForURL(/\/modules\//)
  await expect(page.locator('h1')).toHaveCount(1)
  expect(before).toBeGreaterThan(0)

  // The dashboard links each course too, so the switcher is not the only way in.
  await page.goto('/')
  expect(await page.locator('a[href^="/roadmap?course="]').count()).toBeGreaterThan(1)
})

test('no lesson or module is locked: every card links through (ADR 0015)', async ({ page }) => {
  await page.goto('/roadmap')
  // Every module card is a link, including ones nothing has been started in.
  const moduleHrefs = await page.evaluate(() =>
    [...document.querySelectorAll('a[href]')]
      .map((a) => new URL((a as HTMLAnchorElement).href).pathname)
      .filter((path) => /^\/modules\/[^/]+$/.test(path)),
  )
  expect(moduleHrefs.length, 'linked module cards').toBeGreaterThan(1)
  expect(await page.locator('text=🔒').count(), 'lock glyphs').toBe(0)
  expect(await page.locator('[data-locked]').count(), 'locked rows').toBe(0)
  expect(await page.locator('[data-state="locked"]').count(), 'locked status dots').toBe(0)
  await expect(page.getByText(/잠김|Locked/)).toHaveCount(0)

  // The last module on the roadmap has no finished prerequisites, and still opens — and so
  // does every lesson in it.
  const last = moduleHrefs[moduleHrefs.length - 1] as string
  await page.goto(last)
  const moduleId = last.split('/')[2]
  const lessons = page.locator(`a[href^="/modules/${moduleId}/"]`)
  expect(await lessons.count(), 'linked lessons in the last module').toBeGreaterThan(0)
  await lessons.first().click()
  await page.waitForURL(/\/modules\/[^/]+\/[^/]+$/)
  await expect(page.locator('h1')).toHaveCount(1)
  await expect(page.getByText(/잠김|Locked/)).toHaveCount(0)
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

/**
 * How large a page's HTML may be, uncompressed (#57). The resource library once reached
 * 830 KB because it carried the whole catalogue twice; nothing noticed, because nothing
 * measured. The budgets sit well above today's sizes and far below that.
 */
const HTML_BUDGET_BYTES = 350_000

test('public pages stay within their size budget', async ({ page }) => {
  await page.goto('/roadmap')
  const lesson = await page.locator('a[href^="/modules/"]').first().getAttribute('href')
  for (const path of ['/', '/roadmap', '/resources', '/resources?page=2', lesson ?? '/roadmap']) {
    const response = await page.request.get(path)
    expect(response.ok(), path).toBe(true)
    const bytes = (await response.body()).byteLength
    expect(bytes, `${path} is ${Math.round(bytes / 1024)} KB`).toBeLessThan(HTML_BUDGET_BYTES)
  }
})

test('the resource library filters and pages through the address', async ({ page }) => {
  await page.goto('/resources')
  const table = page.getByRole('table')
  // One page of rows, not the whole catalogue.
  const rows = table.getByRole('row')
  expect(await rows.count()).toBeLessThanOrEqual(26) // the header plus 25
  await expect(page.getByRole('status').first()).toContainText(/1–25/)

  // Paging keeps to the address, so a page can be linked to.
  await page.getByRole('link', { name: /다음 페이지|Next page/ }).click()
  await page.waitForURL(/page=2/)
  await expect(page.getByRole('status').first()).toContainText(/26–50/)

  // A kind is a link, and it resets the page.
  const kinds = page.getByRole('navigation', { name: /종류|Kind/ })
  await kinds.getByRole('link').nth(1).click()
  await page.waitForURL(/kind=/)
  expect(new URL(page.url()).searchParams.has('page')).toBe(false)
  await expect(kinds.locator('[aria-current="page"]')).toHaveCount(1)

  // Searching keeps the kind and works without JavaScript (a plain GET form).
  await page.locator('#resource-search').fill('zzzz-no-such-resource')
  await page.locator('#resource-search').press('Enter')
  await page.waitForURL(/q=zzzz/)
  expect(new URL(page.url()).searchParams.has('kind')).toBe(true)
  await expect(page.getByText(/조건에 맞는 자료가 없습니다|No resource matches/)).toBeVisible()
  await expect(page.getByRole('table')).toHaveCount(0)
})
