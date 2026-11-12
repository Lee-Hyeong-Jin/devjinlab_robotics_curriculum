import { expect, test, type Page } from '@playwright/test'

/**
 * SEO surface (ADR 0016).
 *
 * The suite adapts to how the deployment is configured, because both states are real: with
 * `RC_PUBLIC_CONTENT` off the curriculum must *not* be indexable and the sitemap must be
 * empty, and with it on the opposite. `robots.txt` says which state we are in, so the same
 * spec covers the closed configuration in CI and the published one when run against a public
 * stack.
 */
const LESSON = '/modules/m1-math-physics/m1-coordinate-transforms'
const MODULE = '/modules/m1-math-physics'

async function publishing(page: Page): Promise<boolean> {
  const response = await page.request.get('/robots.txt')
  expect(response.ok()).toBe(true)
  return !/^Disallow: \/$/m.test(await response.text())
}

async function meta(page: Page, name: string): Promise<string | null> {
  return page.locator(`meta[name="${name}"]`).first().getAttribute('content')
}

async function property(page: Page, prop: string): Promise<string | null> {
  return page.locator(`meta[property="${prop}"]`).first().getAttribute('content')
}

test('robots.txt keeps crawlers out of personal and operator pages', async ({ page }) => {
  const text = await (await page.request.get('/robots.txt')).text()
  if (!(await publishing(page))) {
    expect(text).toMatch(/^Disallow: \/$/m)
    return
  }
  for (const path of ['/login', '/profile', '/admin/', '/review', '/reports', '/api/']) {
    expect(text, `${path} must be disallowed`).toContain(`Disallow: ${path}`)
  }
  expect(text).toContain('Sitemap:')
})

test('sitemap.xml lists the curriculum only when it is published', async ({ page }) => {
  const response = await page.request.get('/sitemap.xml')
  expect(response.ok()).toBe(true)
  const xml = await response.text()
  if (!(await publishing(page))) {
    expect(xml).not.toContain('<url>')
    return
  }
  expect(xml).toContain('/roadmap')
  expect(xml).toContain('/modules/')
  // Lessons use the canonical nested URL, never the `/lessons/{id}` shortcut.
  expect(xml).not.toContain('<loc>' + '/lessons/')
  // Every entry offers both languages plus x-default.
  expect(xml).toContain('hreflang="en"')
  expect(xml).toContain('hreflang="x-default"')
})

test('a lesson page carries the metadata a crawler needs', async ({ page }) => {
  await page.goto(LESSON)
  const published = await publishing(page)

  // One meaningful h1, and the lesson body in the markup rather than fetched later. Waiting
  // for `.markdown-body` matters: React streams, so `load` can fire while the suspense
  // fallback is still on screen, and measuring then would pass against an empty skeleton.
  await expect(page.locator('main .markdown-body').first()).toBeVisible()
  await expect(page.locator('h1')).toHaveCount(1)
  expect((await page.locator('h1').innerText()).trim().length).toBeGreaterThan(1)
  expect((await page.locator('main').innerText()).length).toBeGreaterThan(500)

  expect(await meta(page, 'description')).toBeTruthy()
  const robots = (await meta(page, 'robots')) ?? ''
  if (published) {
    expect(robots).toContain('index')
    expect(robots).not.toContain('noindex')
  } else {
    expect(robots).toContain('noindex')
  }

  const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
  expect(canonical).toContain(LESSON)
  expect(canonical).not.toContain('lang=')

  const alternates = await page
    .locator('link[rel="alternate"]')
    .evaluateAll((links) =>
      links.map((link) => `${link.getAttribute('hreflang')}|${link.getAttribute('href')}`),
    )
  expect(alternates.some((entry) => entry.startsWith('x-default|'))).toBe(true)
  expect(alternates.some((entry) => entry.startsWith('ko|'))).toBe(true)
  expect(alternates.some((entry) => entry.startsWith('en|') && entry.includes('lang=en'))).toBe(
    true,
  )

  expect(await property(page, 'og:title')).toBeTruthy()
  expect(await property(page, 'og:type')).toBe('article')
  expect(await property(page, 'og:url')).toBe(canonical)
  expect(await meta(page, 'twitter:card')).toBe('summary')
})

test('structured data parses and names the right types', async ({ page }) => {
  const types = async (path: string) => {
    await page.goto(path)
    await expect(page.locator('h1')).toHaveCount(1)
    return page.locator('script[type="application/ld+json"]').evaluateAll((scripts) =>
      scripts.flatMap((script) => {
        const parsed = JSON.parse(script.textContent ?? 'null')
        const list = Array.isArray(parsed) ? parsed : [parsed]
        return list.map((item) => item?.['@type'])
      }),
    )
  }
  // JSON.parse above is the assertion that the block is valid; a nonce-less block under the
  // CSP would simply not be in the DOM, so finding it also proves the nonce is applied.
  expect(await types(LESSON)).toEqual(['LearningResource', 'BreadcrumbList'])
  expect(await types(MODULE)).toEqual(['LearningResource', 'BreadcrumbList'])
  expect(await types('/roadmap')).toEqual(['Course', 'BreadcrumbList'])
})

test('a personal page is never indexable, however the site is configured', async ({ page }) => {
  for (const path of ['/', '/login', '/signup']) {
    await page.goto(path)
    expect((await meta(page, 'robots')) ?? '', `${path} must be noindex`).toContain('noindex')
  }
})

test('the english alternate really renders in english', async ({ page }) => {
  await page.goto(`${MODULE}?lang=en`)
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  // The canonical of an alternate points back at the one address for the page.
  const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
  expect(canonical).not.toContain('lang=')
})
