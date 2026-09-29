import { expect, test } from '@playwright/test'
import { copyFile, mkdir, readFile } from 'node:fs/promises'

test.beforeEach(async () => {
  await mkdir('e2e/plans', { recursive: true })
  await copyFile('plans/example.json', 'e2e/plans/example.json')
})

test('add a node: count increments, file gains the node, survives reload', async ({ page }) => {
  await page.goto('/?plan=example')
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"id": "untitled"')
  await page.reload()
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
})

test('edit the new node in the panel, then delete it', async ({ page }) => {
  await page.goto('/?plan=example')
  await page.getByRole('button', { name: 'Add node' }).click()
  await expect(page.getByTestId('node-panel')).toBeVisible()
  await page.getByLabel('Title').fill('Smoke node')
  await page.getByLabel('Status').selectOption('doing')
  await page.getByRole('checkbox', { name: 'schema' }).check()
  await expect(page.getByTestId('save-indicator')).toHaveAttribute('data-state', 'saved')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toContain('"title": "Smoke node"')
  expect(text).toContain('"status": "doing"')
  expect(text).toMatch(/"depends_on": \[\s*"schema"\s*\]/)
  await page.getByRole('button', { name: 'Delete node' }).click()
  await expect(page.getByTestId('node-panel')).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})

test('link mode toggles and hints', async ({ page }) => {
  await page.goto('/?plan=example')
  const btn = page.getByRole('button', { name: 'Link mode' })
  await expect(btn).toHaveAttribute('aria-pressed', 'false')
  await btn.click()
  await expect(btn).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('toast')).toContainText('click the dependency')
  await page.keyboard.press('Escape')
  await expect(btn).toHaveAttribute('aria-pressed', 'false')
})
