import AxeBuilder from '@axe-core/playwright'
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
  expect(await meta(page, 'twitter:card')).toBe('summary_large_image')
  // `og:locale` carries a territory and follows the language the page is rendered in (which
  // depends on the browser's `Accept-Language` here, so it is compared with `<html lang>`).
  const lang = await page.locator('html').getAttribute('lang')
  expect(await property(page, 'og:locale')).toBe(lang === 'en' ? 'en_US' : 'ko_KR')

  // A snippet shows the description as it is, so no TeX or Markdown source may be left in it.
  const description = (await meta(page, 'description')) ?? ''
  expect(description).not.toMatch(/[$\\`]|\*\*/)
})

test('every page offers a card image, icons and a manifest that resolve', async ({ page }) => {
  await page.goto(LESSON)
  await expect(page.locator('h1')).toHaveCount(1)

  const image = await property(page, 'og:image')
  expect(image, 'og:image must be an absolute URL').toMatch(/^https?:\/\//)
  // The absolute URL names the public host, which a test stack is not; fetch its path here.
  const imagePath = new URL(image ?? '').pathname
  const imageResponse = await page.request.get(imagePath)
  expect(imageResponse.ok()).toBe(true)
  expect(imageResponse.headers()['content-type']).toContain('image/png')
  expect(await property(page, 'og:image:width')).toBe('1200')
  expect(await property(page, 'og:image:height')).toBe('630')
  expect(await property(page, 'og:image:alt')).toBeTruthy()

  const icons = await page
    .locator('link[rel="icon"], link[rel="apple-touch-icon"]')
    .evaluateAll((links) => links.map((link) => link.getAttribute('href') ?? ''))
  expect(icons.length).toBeGreaterThanOrEqual(2)
  for (const href of [...icons, '/favicon.ico']) {
    expect((await page.request.get(href)).ok(), `${href} must resolve`).toBe(true)
  }

  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href')
  const manifest = await (await page.request.get(manifestHref ?? '')).json()
  expect(manifest.name).toBeTruthy()
  for (const icon of manifest.icons as { src: string }[]) {
    expect((await page.request.get(icon.src)).ok(), `${icon.src} must resolve`).toBe(true)
  }
})

test('the home page is the front door when the curriculum is published', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('main h1')).toHaveCount(1)
  const robots = (await meta(page, 'robots')) ?? ''
  if (!(await publishing(page))) {
    // Closed deployment: `/` is a reader's dashboard and stays out of the index.
    expect(robots).toContain('noindex')
    return
  }
  expect(robots).toContain('index')
  expect(robots).not.toContain('noindex')
  const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
  expect(new URL(canonical ?? '').pathname).toBe('/')

  // It links every course's roadmap and its modules, so a crawler reaches the curriculum from
  // the root in one step.
  // The page streams: wait for the first module link before counting them.
  await expect(page.locator('main a[href^="/modules/"]').first()).toBeVisible()
  expect(await page.locator('main a[href^="/modules/"]').count()).toBeGreaterThan(5)
  await expect(page.locator('main a[href^="/roadmap"]').first()).toBeVisible()

  const types = await page.locator('script[type="application/ld+json"]').evaluateAll((scripts) =>
    scripts.flatMap((script) => {
      const parsed = JSON.parse(script.textContent ?? 'null')
      return (Array.isArray(parsed) ? parsed : [parsed]).map((item) => item?.['@type'])
    }),
  )
  expect(types).toEqual(
    expect.arrayContaining(['WebSite', 'Organization', 'ItemList', 'Course', 'FAQPage']),
  )

  // The landing page is new markup, so it gets the same accessibility bar as the read screens.
  const axe = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze()
  const blocking = axe.violations
    .filter((violation) => ['serious', 'critical'].includes(violation.impact ?? ''))
    .map((violation) => `${violation.id}: ${violation.help}`)
  expect(blocking, 'axe violations on the landing page').toEqual([])
  await page.setViewportSize({ width: 360, height: 740 })
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  )
  expect(overflow, 'the landing page must not scroll sideways on a phone').toBeLessThanOrEqual(0)

  const sitemap = await (await page.request.get('/sitemap.xml')).text()
  const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1] ?? '')
  expect(locs.some((loc) => new URL(loc).pathname === '/' && !loc.includes('?'))).toBe(true)
  // One address per page: no entry is listed twice.
  expect(new Set(locs).size).toBe(locs.length)
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
  expect(await types('/resources')).toEqual(['CollectionPage', 'BreadcrumbList'])
})

test('a personal page is never indexable, however the site is configured', async ({ page }) => {
  // `/` is not in this list: on a published deployment it is the public landing page for a
  // visitor without a session (covered above), and a reader's dashboard only once signed in.
  for (const path of ['/login', '/signup', '/search', '/review']) {
    await page.goto(path)
    expect((await meta(page, 'robots')) ?? '', `${path} must be noindex`).toContain('noindex')
  }
})

test('the english alternate really renders in english', async ({ page }) => {
  await page.goto(`${MODULE}?lang=en`)
  await expect(page.locator('html')).toHaveAttribute('lang', 'en')
  // Each language version is its own canonical. Pointing the English page at the Korean
  // address would tell a search engine it is a copy, and only the Korean one would be indexed.
  const canonical = await page.locator('link[rel="canonical"]').getAttribute('href')
  expect(canonical).toContain(`${MODULE}?lang=en`)
  expect(await property(page, 'og:url')).toBe(canonical)
  const alternates = await page
    .locator('link[rel="alternate"][hreflang]')
    .evaluateAll((links) =>
      links.map((link) => `${link.getAttribute('hreflang')}|${link.getAttribute('href')}`),
    )
  expect(alternates.some((entry) => entry.startsWith('ko|') && !entry.includes('lang='))).toBe(true)
  expect(alternates).toContain(`en|${canonical}`)
  expect(await property(page, 'og:locale')).toBe('en_US')
  expect(await property(page, 'og:locale:alternate')).toBe('ko_KR')
})

test('the titles carry the words people search with', async ({ page }) => {
  if (!(await publishing(page))) test.skip(true, 'the curriculum is not published here')
  const title = async (path: string) => {
    await page.goto(path)
    await expect(page.locator('main h1')).toHaveCount(1)
    return page.title()
  }
  expect(await title('/?lang=ko')).toMatch(/로보틱스 강의/)
  expect(await title('/?lang=en')).toMatch(/Learn Robotics/)
  expect(await title('/?lang=en')).toMatch(/Robotics Tutorials/)
  // A lesson with a short name, so the label fits (a long name drops it: `composeTitle`).
  const short = '/modules/m2-kinematics/m2-forward-kinematics'
  expect(await title(`${short}?lang=ko`)).toMatch(/로보틱스 강의/)
  // A lesson title says what kind of page it is (the label is dropped only when the lesson's
  // own name leaves no room for it).
  expect(await title(`${short}?lang=en`)).toBe(
    'Forward kinematics — Robotics Tutorial | Learn Robotics',
  )
  expect(await title('/guide?lang=en')).toMatch(/How to Learn Robotics/)
  // The words are in the visible heading too, not only in the tab title.
  await page.goto('/?lang=en')
  await expect(page.locator('main h1')).toContainText(/Learn robotics/i)
  await page.goto('/?lang=ko')
  await expect(page.locator('main h1')).toContainText('로보틱스 강의')
})

test('the study guide is a published page built from the curriculum', async ({ page }) => {
  const response = await page.goto('/guide?lang=ko')
  expect(response?.status()).toBe(200)
  await expect(page.locator('main h1')).toHaveCount(1)
  if (!(await publishing(page))) {
    expect((await meta(page, 'robots')) ?? '').toContain('noindex')
    return
  }
  expect((await meta(page, 'robots')) ?? '').not.toContain('noindex')
  // The learning path links real modules, and the FAQ is on the page as text.
  await expect(page.locator('main a[href^="/modules/"]').first()).toBeVisible()
  expect(await page.locator('main dl dt').count()).toBeGreaterThanOrEqual(4)
  const types = await page.locator('script[type="application/ld+json"]').evaluateAll((scripts) =>
    scripts.flatMap((script) => {
      const parsed = JSON.parse(script.textContent ?? 'null')
      return (Array.isArray(parsed) ? parsed : [parsed]).map((item) => item?.['@type'])
    }),
  )
  expect(types).toEqual(['Article', 'BreadcrumbList', 'FAQPage'])
  expect(await (await page.request.get('/sitemap.xml')).text()).toContain('/guide</loc>')
  // Every page links to it from the footer.
  await page.goto(LESSON)
  await expect(page.locator('footer a[href="/guide"]')).toBeVisible()
})

test('missing content answers 404 and the lesson shortcut redirects', async ({ page }) => {
  // Statuses a crawler reads from the first line of the response, not from the page text.
  if (!(await publishing(page))) test.skip(true, 'an anonymous request gets no answer here')
  for (const path of ['/modules/no-such-module', `${MODULE}/no-such-lesson`]) {
    const response = await page.request.get(path, { maxRedirects: 0 })
    expect(response.status(), path).toBe(404)
  }
  const lessonId = LESSON.split('/').pop() ?? ''
  const shortcut = await page.request.get(`/lessons/${lessonId}`, { maxRedirects: 0 })
  expect(shortcut.status()).toBe(308)
  expect(new URL(shortcut.headers()['location'] ?? '', 'http://x').pathname).toBe(LESSON)
  expect((await page.request.get(LESSON, { maxRedirects: 0 })).status()).toBe(200)
})
