import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

/**
 * Responsive layout (frontend.md §4.2). Runs in the smoke leg, against a **local**-mode API.
 *
 * Each screen is opened at a small phone, a large phone, a tablet in portrait and a tablet in
 * landscape. Two things must hold at every width: the page never scrolls sideways, and the
 * navigation is reachable.
 */

const VIEWPORTS = [
  { name: 'small phone', width: 320, height: 640 },
  { name: 'phone', width: 390, height: 844 },
  { name: 'tablet portrait', width: 768, height: 1024 },
  { name: 'tablet landscape', width: 1024, height: 768 },
] as const

const SCREENS = ['/', '/roadmap', '/resources', '/search?q=slam', '/review', '/reports', '/login']

async function overflow(page: Page): Promise<number> {
  return page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
}

/** The first lesson of the first module on the roadmap: a real lesson body with formulas. */
async function openFirstLesson(page: Page): Promise<void> {
  await page.goto('/roadmap')
  await page.locator('main a[href^="/modules/"]').first().click()
  await page.waitForURL(/\/modules\/[^/]+$/)
  const modulePath = new URL(page.url()).pathname
  await page.locator(`main a[href^="${modulePath}/"]`).first().click()
  await page.waitForURL(/\/modules\/[^/]+\/[^/]+$/)
}

for (const viewport of VIEWPORTS) {
  test.describe(`${viewport.name} (${viewport.width}px)`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    for (const path of SCREENS) {
      test(`${path} does not scroll sideways`, async ({ page }) => {
        await page.goto(path)
        await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
        expect(await overflow(page), `horizontal overflow on ${path}`).toBeLessThanOrEqual(0)
      })
    }

    test('a lesson and its quiz do not scroll sideways', async ({ page }) => {
      await openFirstLesson(page)
      expect(await overflow(page), `overflow on ${page.url()}`).toBeLessThanOrEqual(0)
      await page.goto(`${page.url()}/quiz`)
      await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
      expect(await overflow(page), `overflow on ${page.url()}`).toBeLessThanOrEqual(0)
    })

    test('the menu reaches every destination and closes after navigating', async ({ page }) => {
      await page.goto('/')
      const nav = page.getByRole('navigation', { name: /주요 메뉴|Main navigation/ })
      const toggle = nav.getByRole('button', { name: /메뉴 열기|Open menu/ })
      await expect(toggle).toBeVisible()
      const roadmap = nav.getByRole('link', { name: /^(로드맵|Roadmap)$/ })
      const theme = nav.getByRole('group', { name: /테마|Theme/ })

      // From the tablet width up the page links are in the bar; on a phone they are in the menu.
      if (viewport.width >= 768) await expect(roadmap).toBeVisible()
      else await expect(roadmap).toBeHidden()
      await expect(theme).toBeHidden()

      await toggle.click()
      await expect(nav.getByRole('button', { name: /메뉴 닫기|Close menu/ })).toHaveAttribute(
        'aria-expanded',
        'true',
      )
      await expect(roadmap).toBeVisible()
      await expect(theme).toBeVisible()
      expect(await overflow(page), 'overflow with the menu open').toBeLessThanOrEqual(0)

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
        .analyze()
      const blocking = results.violations
        .filter((violation) => ['serious', 'critical'].includes(violation.impact ?? ''))
        .map((violation) => `${violation.id}: ${violation.help}`)
      expect(blocking, 'axe violations with the menu open').toEqual([])

      await roadmap.click()
      await page.waitForURL(/\/roadmap/)
      await expect(nav.getByRole('button', { name: /메뉴 열기|Open menu/ })).toHaveAttribute(
        'aria-expanded',
        'false',
      )
    })

    test('Escape closes the menu', async ({ page }) => {
      await page.goto('/')
      const nav = page.getByRole('navigation', { name: /주요 메뉴|Main navigation/ })
      await nav.getByRole('button', { name: /메뉴 열기|Open menu/ }).click()
      await page.keyboard.press('Escape')
      await expect(nav.getByRole('button', { name: /메뉴 열기|Open menu/ })).toBeFocused()
    })
  })
}

test('at the desktop width everything is in the bar and there is no menu button', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 800 })
  await page.goto('/')
  const nav = page.getByRole('navigation', { name: /주요 메뉴|Main navigation/ })
  await expect(nav.getByRole('button', { name: /메뉴 열기|Open menu/ })).toBeHidden()
  await expect(nav.getByRole('link', { name: /^(로드맵|Roadmap)$/ })).toBeVisible()
  await expect(nav.getByRole('group', { name: /테마|Theme/ })).toBeVisible()
  expect(await overflow(page)).toBeLessThanOrEqual(0)
})

test('the resources table keeps its table semantics in the stacked phone layout', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/resources')
  const table = page.getByRole('table')
  await expect(table).toBeVisible()
  expect(await table.getByRole('columnheader').count()).toBeGreaterThan(1)
  await expect(table.getByRole('row').nth(1).getByRole('cell').first()).toBeVisible()
})
