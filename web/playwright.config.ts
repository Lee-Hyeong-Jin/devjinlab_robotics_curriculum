import { defineConfig, devices } from '@playwright/test'

const port = Number(process.env.PORT ?? 3000)
const baseURL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${port}`

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
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : {
        command: 'npm run start',
        url: baseURL,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
})
