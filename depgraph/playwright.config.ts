import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: 'e2e',
  timeout: 60000,
  workers: 1,
  use: {
    baseURL: 'http://localhost:3123',
    headless: true,
    launchOptions: { args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] },
  },
  webServer: {
    command: 'NEXT_DIST_DIR=.next-e2e PLANS_DIR=e2e/plans npm run dev -- -p 3123',
    url: 'http://localhost:3123/api/plans',
    reuseExistingServer: false,
    timeout: 120000,
  },
})
