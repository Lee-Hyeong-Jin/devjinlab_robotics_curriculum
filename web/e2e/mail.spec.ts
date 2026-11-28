import { readFileSync } from 'node:fs'

import { expect, test, type Page } from '@playwright/test'

/**
 * The flows that depend on a mailed link, followed to the end in a browser (#37).
 *
 * A reset mail once pointed at a page that does not exist, and nothing noticed: the unit tests
 * checked the link's path, not that a reader could get from the mail to a new password. This
 * suite needs an API in server mode that sends mail to the test sink
 * (`scripts/dev/smtp_sink.py`), and the sink's output file:
 *
 *   python3 scripts/dev/smtp_sink.py --port 2525 --out /tmp/outbox.jsonl &
 *   RC_AUTH_MODE=server RC_AUTH_COOKIE_SECURE=0 RC_SMTP_HOST=127.0.0.1 RC_SMTP_PORT=2525 \
 *     RC_SMTP_STARTTLS=0 RC_DATA_DIR=$(mktemp -d) uv run rc api serve --port 8000 &
 *   E2E_MAIL_OUTBOX=/tmp/outbox.jsonl E2E_BASE_URL=http://127.0.0.1:3000 npx playwright test mail
 */
const OUTBOX = process.env.E2E_MAIL_OUTBOX

test.skip(!OUTBOX, 'needs a mail sink; set E2E_MAIL_OUTBOX to its output file')

interface Mail {
  to: string[]
  subject: string
  body: string
}

function mailsTo(address: string): Mail[] {
  return readFileSync(OUTBOX ?? '', 'utf8')
    .split('\n')
    .filter((line) => line.trim() !== '')
    .map((line) => JSON.parse(line) as Mail)
    .filter((mail) => mail.to.includes(address))
}

/** The path and query of the link in the newest mail to `address` (the host is the site's). */
async function latestLink(address: string, expectedCount: number): Promise<string> {
  await expect
    .poll(() => mailsTo(address).length, { message: `mail number ${expectedCount} to ${address}` })
    .toBe(expectedCount)
  const mail = mailsTo(address).at(-1)
  const match = /https?:\/\/\S+/.exec(mail?.body ?? '')
  expect(match, `a link in: ${mail?.body}`).not.toBeNull()
  const url = new URL(match![0])
  return `${url.pathname}${url.search}`
}

function freshAccount() {
  const stamp = `${Date.now()}-${Math.floor(Math.random() * 1e6)}`
  return { email: `mail-${stamp}@example.test`, password: 'Correct-Horse-Battery-7' }
}

async function signIn(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.locator('input[name="email"]').fill(email)
  await page.locator('input[name="password"]').fill(password)
  await page.locator('form button[type="submit"]').click()
}

test('a reader verifies their email and resets a forgotten password through the mailed links', async ({
  page,
}) => {
  const account = freshAccount()

  // Sign up: the server can send mail, so it says to look for the verification link.
  await page.goto('/signup')
  await page.locator('input[name="email"]').fill(account.email)
  await page.locator('input[name="password"]').fill(account.password)
  await page.locator('input[name="passwordConfirm"]').fill(account.password)
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL(/\/login\?registered=verify/)

  // The verification link opens a real screen and verifies the address.
  const verify = await latestLink(account.email, 1)
  const verifyResponse = await page.goto(verify)
  expect(verifyResponse?.status()).toBe(200)
  await page.locator('form button[type="submit"]').click()
  await expect(page.getByRole('alert').filter({ hasText: /인증됐습니다|verified/i })).toBeVisible()

  // Forgot the password: ask for a link.
  await page.goto('/password/forgot')
  await page.locator('input[name="email"]').fill(account.email)
  await page.locator('form button[type="submit"]').click()
  await expect(page.getByRole('alert').first()).toBeVisible()

  // Follow the reset link from the mail, all the way to a new password.
  const reset = await latestLink(account.email, 2)
  const resetResponse = await page.goto(reset)
  expect(resetResponse?.status(), `the mailed link ${reset}`).toBe(200)
  const newPassword = 'Another-Horse-Battery-9'
  await page.locator('input[name="password"]').fill(newPassword)
  await page.locator('input[name="passwordConfirm"]').fill(newPassword)
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL(/\/login\?reset=1/)

  // The old password is dead, the new one works.
  await signIn(page, account.email, account.password)
  await expect(page.getByRole('alert').filter({ hasText: /올바르지|Invalid/ })).toBeVisible()
  await signIn(page, account.email, newPassword)
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 })

  // And the link cannot be used a second time.
  await page.context().clearCookies()
  await page.goto(reset)
  await page.locator('input[name="password"]').fill('Third-Horse-Battery-11')
  await page.locator('input[name="passwordConfirm"]').fill('Third-Horse-Battery-11')
  await page.locator('form button[type="submit"]').click()
  await expect(page.getByRole('alert').filter({ hasText: /토큰|token/i })).toBeVisible()
  expect(new URL(page.url()).pathname).toBe('/password/reset')
})

test('an operator-sent reset mail leads to the same screen', async ({ page }) => {
  const adminEmail = process.env.E2E_ADMIN_EMAIL
  const adminPassword = process.env.E2E_ADMIN_PASSWORD
  test.skip(!adminEmail || !adminPassword, 'set E2E_ADMIN_EMAIL and E2E_ADMIN_PASSWORD')

  const learner = freshAccount()
  await page.goto('/signup')
  await page.locator('input[name="email"]').fill(learner.email)
  await page.locator('input[name="password"]').fill(learner.password)
  await page.locator('input[name="passwordConfirm"]').fill(learner.password)
  await page.locator('form button[type="submit"]').click()
  await page.waitForURL(/\/login/)
  await latestLink(learner.email, 1) // the verification mail

  await signIn(page, adminEmail!, adminPassword!)
  await page.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 15_000 })
  await page.goto(`/admin/users?q=${encodeURIComponent(learner.email)}`)
  await page.locator('a[href^="/admin/users/"]').first().click()
  await page.waitForURL(/\/admin\/users\/\d+/)
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: /재설정 메일|reset/i }).click()
  // The operator is told it was sent (it used to say it failed).
  await expect(page.locator('[data-flash]')).toContainText(/보냈|sent/i)

  const reset = await latestLink(learner.email, 2)
  expect(reset.startsWith('/password/reset?token=')).toBe(true)
  await page.context().clearCookies()
  expect((await page.goto(reset))?.status()).toBe(200)
  await expect(page.locator('input[name="passwordConfirm"]')).toBeVisible()
})
