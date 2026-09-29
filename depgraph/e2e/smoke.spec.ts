import { expect, test, type Page } from '@playwright/test'
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises'

const label = (page: Page, id: string) => page.locator(`[data-testid="node-label"][data-node-id="${id}"]`)
const planText = () => readFile('e2e/plans/example.json', 'utf8')

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

test('edit the new node in the HUD, link it by clicking a label, then delete it', async ({ page }) => {
  await page.goto('/?plan=example')
  await page.getByRole('button', { name: 'Add node', exact: true }).click()
  const hud = page.getByTestId('node-hud')
  await expect(hud).toBeVisible()
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('Smoke node')
  await title.press('Enter')
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Smoke node')
  await page.getByRole('radio', { name: 'doing', exact: true }).click()
  await expect(page.getByTestId('status-pip-doing')).toHaveAttribute('aria-checked', 'true')
  await page.getByRole('button', { name: 'Add dependency', exact: true }).click()
  await label(page, 'schema').click()
  await expect(page.getByTestId('dep-schema')).toBeVisible()
  await expect.poll(planText).toMatch(/"id": "untitled"[\s\S]*?"depends_on": \[\s*"schema"\s*\]/)
  const text = await planText()
  expect(text).toContain('"title": "Smoke node"')
  expect(text).toMatch(/"id": "untitled"[\s\S]*?"status": "doing"/)
  const del = page.getByTestId('delete-node')
  await expect(del).toHaveAccessibleName('Delete node')
  await del.click()
  await expect(del).toHaveAccessibleName('Confirm delete')
  await del.click()
  await expect(hud).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})

test('Add dependency arms, Esc disarms', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'api-routes').click()
  const hud = page.getByTestId('node-hud')
  const arm = page.getByRole('button', { name: 'Add dependency', exact: true })
  await expect(hud).toBeVisible()
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await arm.click()
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('link-hint')).toHaveText('Pick what Write API routes needs')
  await page.keyboard.press('Escape')
  await expect(arm).toHaveAttribute('aria-pressed', 'false')
  await expect(page.getByTestId('link-hint')).toBeHidden()
  await expect(hud).toBeVisible()
  await page.keyboard.press('l')
  await expect(arm).toHaveAttribute('aria-pressed', 'true')
  await page.keyboard.press('Escape')
  await page.keyboard.press('Escape')
  await expect(hud).toBeHidden()
})

test('cycle is refused with an error', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await page.getByRole('button', { name: 'Add dependency', exact: true }).click()
  await label(page, 'api-routes').click()
  await expect(page.getByTestId('toast')).toContainText('cycle:')
  await expect(page.getByTestId('toast')).toHaveAttribute('data-tone', 'error')
  const text = await readFile('e2e/plans/example.json', 'utf8')
  expect(text).toMatch(/"id": "schema"[\s\S]*?"depends_on": \[\s*"design-spec"\s*\]/)
  const res = await page.request.put('/api/plans/example', {
    data: {
      name: 'x',
      nodes: [
        { id: 'a', title: 'A', depends_on: ['b'] },
        { id: 'b', title: 'B', depends_on: ['a'] },
      ],
    },
  })
  expect(res.status()).toBe(400)
  expect((await res.json()).errors[0]).toMatch(/^cycle:/)
})

test('all 8 labels are visible on load', async ({ page }) => {
  await page.goto('/?plan=example')
  const labels = page.getByTestId('node-label')
  await expect(labels).toHaveCount(8)
  for (const l of await labels.all()) await expect(l).toBeVisible()
  await expect(page.getByRole('button', { name: 'Schema + validator', exact: true })).toHaveAttribute('data-node-id', 'schema')
  await expect(label(page, 'node-panel')).toHaveAttribute('data-status', 'blocked')
})

test('clicking a label selects the node; a needs chip jumps to the dependency', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'schema').click()
  await expect(page.getByRole('region', { name: 'Selected node' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Schema + validator')
  await expect(label(page, 'schema')).toHaveAttribute('data-selected', 'true')
  await expect(label(page, 'store')).toHaveAttribute('data-dim', 'false')
  await expect(label(page, 'watcher')).toHaveAttribute('data-dim', 'true')
  await page.getByTestId('dep-design-spec').getByRole('button', { name: 'Approve design spec', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Rename', exact: true })).toContainText('Approve design spec')
  await expect(label(page, 'design-spec')).toHaveAttribute('data-selected', 'true')
})

test('hotkeys 1–4 and N work', async ({ page }) => {
  await writeFile('e2e/plans/empty.json', JSON.stringify({ name: 'Empty', nodes: [] }, null, 2) + '\n')
  await page.goto('/?plan=empty')
  await expect(page.getByTestId('empty-hint')).toHaveText('Press N or click + Node to place your first step.')
  await page.keyboard.press('n')
  await expect(page.getByTestId('node-count')).toHaveText('1 nodes')
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('First step')
  await title.press('Enter')
  await expect(page.getByTestId('empty-hint')).toBeHidden()
  for (const [key, status] of [['2', 'doing'], ['3', 'done'], ['4', 'blocked'], ['1', 'todo'], ['4', 'blocked']] as const) {
    await page.keyboard.press(key)
    await expect(page.getByTestId(`status-pip-${status}`)).toHaveAttribute('aria-checked', 'true')
  }
  await expect.poll(() => readFile('e2e/plans/empty.json', 'utf8')).toContain('"status": "blocked"')
  expect(await readFile('e2e/plans/empty.json', 'utf8')).toContain('"title": "First step"')
})

test('Shift+N adds a next step; Del twice deletes it', async ({ page }) => {
  await page.goto('/?plan=example')
  await label(page, 'watcher').click()
  await page.keyboard.press('Shift+N')
  await expect(page.getByTestId('node-count')).toHaveText('9 nodes')
  const title = page.getByRole('textbox', { name: 'Title', exact: true })
  await expect(title).toBeFocused()
  await title.fill('After watcher')
  await title.press('Enter')
  await expect(page.getByTestId('dep-watcher')).toBeVisible()
  await expect.poll(planText).toMatch(/"id": "untitled"[\s\S]*?"depends_on": \[\s*"watcher"\s*\]/)
  await page.keyboard.press('Delete')
  await expect(page.getByTestId('delete-node')).toHaveAccessibleName('Confirm delete')
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('delete-node')).toHaveAccessibleName('Delete node')
  await expect(page.getByTestId('node-hud')).toBeVisible()
  await page.keyboard.press('Delete')
  await expect(page.getByTestId('delete-node')).toHaveAccessibleName('Confirm delete')
  await page.keyboard.press('Delete')
  await expect(page.getByTestId('node-hud')).toBeHidden()
  await expect(page.getByTestId('node-count')).toHaveText('8 nodes')
})
