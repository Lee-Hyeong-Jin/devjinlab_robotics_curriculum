import { defineConfig, devices } from '@playwright/test'

const port = Number(process.env.PORT ?? 3000)
const baseURL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${port}`

const BROWSERS = {
  chromium: devices['Desktop Chrome'],
  firefox: devices['Desktop Firefox'],
  webkit: devices['Desktop Safari'],
} as const

/**
 * Chromium by default (what CI runs). `E2E_BROWSERS=firefox,webkit` runs the same suites in
 * other engines for a cross-browser check, once `npx playwright install firefox webkit` has
 * fetched them.
 */
const projects = (process.env.E2E_BROWSERS ?? 'chromium')
  .split(',')
  .map((name) => name.trim())
  .filter((name): name is keyof typeof BROWSERS => name in BROWSERS)
  .map((name) => ({ name, use: { ...BROWSERS[name] } }))

/**
 * Smoke + accessibility (axe-core) E2E. The suite needs both the API
 * (`uv run rc api serve`) and the web app; CI wires them up (AC-WEB.1, AC-A11Y.1).
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
  use: { baseURL, trace: 'on-first-retry' },
  projects,
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'npm run start',
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
})
