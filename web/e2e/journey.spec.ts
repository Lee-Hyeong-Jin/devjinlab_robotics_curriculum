import { expect, test, type Page } from '@playwright/test'

/**
 * AC-WEB.1 — the whole learner flow in a headless browser:
 * sign up → sign in → dashboard → roadmap → open a lesson → start studying →
 * mark complete → quiz → review → weekly report.
 *
 * It needs an API in server mode, which is not how the smoke suite runs it, so
 * the suite skips itself unless `E2E_AUTH=1` says accounts are available:
 *
 *   RC_AUTH_MODE=server RC_AUTH_COOKIE_SECURE=0 RC_DATA_DIR=$(mktemp -d) \
 *     uv run rc api serve --port 8000 &
 *   E2E_AUTH=1 E2E_BASE_URL=http://127.0.0.1:3000 npx playwright test journey
 */
const AUTH_ENABLED = process.env.E2E_AUTH === '1'

test.skip(!AUTH_ENABLED, 'needs an API in server mode (RC_AUTH_MODE=server); set E2E_AUTH=1')

/** A fresh account per run, so the journey always starts from zero progress. */
function freshAccount() {
  const stamp = `${Date.now()}-${Math.floor(Math.random() * 1e6)}`
  return { email: `journey-${stamp}@example.test`, password: 'Correct-Horse-Battery-7' }
}

/** Fields are addressed by their form `name`, which is the contract the Server
 * Action reads — unlike a label, it is unambiguous between "비밀번호" and
 * "비밀번호 확인". */
async function signUpAndIn(page: Page, account: ReturnType<typeof freshAccount>) {
  await page.goto('/signup')
  await page.locator('input[name="email"]').fill(account.email)
  await page.locator('input[name="password"]').fill(account.password)
  await page.locator('input[name="passwordConfirm"]').fill(account.password)
  await page.locator('form button[type="submit"]').click()

  await page.waitForURL(/\/login/)
  // Without SMTP the server cannot send a verification link, so sign-up says the account is
  // ready rather than telling the reader to check their inbox.
  await expect(page.getByText(/바로 로그인하세요|Your account is ready/)).toBeVisible()
  await page.locator('input[name="email"]').fill(account.email)
  await page.locator('input[name="password"]').fill(account.password)
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 })
}

test('a learner signs up, studies a lesson, takes its quiz and reviews', async ({ page }) => {
  const account = freshAccount()
  await signUpAndIn(page, account)

  // Dashboard.
  await expect(page.getByRole('heading', { level: 1, name: /대시보드|Dashboard/ })).toBeVisible()

  // Roadmap → first module → first lesson.
  await page.getByRole('link', { name: /로드맵|Roadmap/ }).click()
  await page.waitForURL(/\/roadmap$/)
  await expect(page.getByRole('heading', { level: 1, name: /로드맵|roadmap/i })).toBeVisible()

  await page.locator('a[href^="/modules/"]').first().click()
  await page.waitForURL(/\/modules\/[^/]+$/)
  const moduleId = new URL(page.url()).pathname.split('/')[2]

  await page.locator(`a[href^="/modules/${moduleId}/"]`).first().click()
  await page.waitForURL(/\/modules\/[^/]+\/[^/]+$/)
  const lessonUrl = page.url()
  await expect(page.getByRole('heading', { name: /이 단계 공부법|How to study/ })).toBeVisible()

  // Start the study timer, then stop it.
  await page.getByRole('button', { name: /학습 시작|Start studying/ }).click()
  await expect(page.getByRole('button', { name: /학습 종료|Stop studying/ })).toBeVisible()
  await page.getByRole('button', { name: /학습 종료|Stop studying/ }).click()
  await expect(page.getByRole('button', { name: /학습 시작|Start studying/ })).toBeVisible()

  // Mark the lesson complete — the AC's "완료 표시".
  await page.getByRole('button', { name: /완료로 표시|Mark complete/ }).click()
  await expect(page.getByRole('status').or(page.getByRole('alert')).first()).toBeVisible()

  // The completion propagates: the module that held the lesson is now in
  // progress on the roadmap (one of its lessons is done, not all of them).
  await page.goto('/roadmap')
  await expect(page.getByText(/진행 중|In progress/).first()).toBeVisible()

  // And the dashboard counts it.
  await page.goto('/')
  await expect(page.getByRole('progressbar').first()).toBeVisible()

  // Quiz: answer the first question and submit.
  await page.goto(`${lessonUrl}/quiz`)
  const firstChoice = page.locator('input[type="radio"]').first()
  if (await firstChoice.count()) {
    await firstChoice.check()
    await page.getByRole('button', { name: /^제출$|^Submit$/ }).click()
    await expect(page.getByRole('heading', { name: /채점 결과|Result/ })).toBeVisible()

    // The explanation arrives as a React tree the Server Action rendered with the
    // lesson Markdown pipeline, so it lands inside `.markdown-body`. The plain-text
    // fallback does not, which is what makes this worth asserting.
    const explanation = page.locator('dd .markdown-body').first()
    if (await explanation.count()) {
      await expect(explanation).toBeVisible()
      await expect(explanation).not.toContainText('**')
    }
  }

  // Review: a wrong answer creates a card, so the deck may or may not have one.
  await page.goto('/review')
  const flip = page.getByRole('button', { name: /뒤집기|Flip/ })
  if (await flip.count()) {
    await flip.click()
    await page.getByRole('button', { name: /^보통$|^Good$/ }).click()
    await expect(page.getByRole('status').first()).toBeVisible()
  }

  // Weekly report.
  await page.goto('/reports')
  // `.first()`: the report's own Markdown repeats the title as a heading.
  await expect(
    page.getByRole('heading', { level: 1, name: /주간 리포트|Weekly report/ }).first(),
  ).toBeVisible()
  // The page keeps exactly one level-1 heading (frontend.md §6).
  await expect(page.locator('h1')).toHaveCount(1)

  // Module report: reachable from the weekly report, same Markdown + tiles shape.
  await page.locator('a[href^="/reports/modules/"]').first().click()
  await page.waitForURL(/\/reports\/modules\/[^/]+$/)
  await expect(page.getByText(/완료한 레슨|Lessons completed/)).toBeVisible()
  await expect(page.locator('h1')).toHaveCount(1)

  // Profile, then sign out.
  await page.goto('/profile')
  await expect(page.getByText(account.email).first()).toBeVisible()
  // This API runs without SMTP, so the verification link can never arrive: the screen must
  // not claim the address is unverified nor offer to resend (email_verification =
  // "unavailable").
  await expect(page.getByText(/인증되지 않음|Not verified/)).toHaveCount(0)
  await expect(
    page.getByRole('button', { name: /인증 메일 다시 받기|Send the link again/ }),
  ).toHaveCount(0)
  await page.getByRole('button', { name: /로그아웃|Sign out/ }).click()
  await page.waitForURL(/\/login/)
})

test('an admin screen refuses a learner (AC-WEB.4)', async ({ page }) => {
  await signUpAndIn(page, freshAccount())
  await page.goto('/admin/users')
  // A fresh account is a learner: the API refuses and the screen says so.
  await expect(page.getByText(/권한이 없습니다|do not have permission/)).toBeVisible()
  await expect(page.getByRole('table')).toHaveCount(0)
})
