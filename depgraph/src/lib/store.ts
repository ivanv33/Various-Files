import { createHash, randomBytes } from 'node:crypto'
import { mkdir, readdir, readFile, rename, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { ID_RE, serializePlan, slugify, validatePlan, type Plan } from '@/lib/schema'

export interface PlanSummary { slug: string; name: string; nodeCount: number }
export class PlanExistsError extends Error {}

// Survives Next.js dev HMR re-evaluation of this module.
const g = globalThis as unknown as { __depgraphHashes?: Map<string, string> }
const hashes = (g.__depgraphHashes ??= new Map<string, string>())

export function plansDir(): string {
  return process.env.PLANS_DIR ? path.resolve(process.env.PLANS_DIR) : path.join(process.cwd(), 'plans')
}

export function hashOf(text: string): string {
  return createHash('sha1').update(text).digest('hex')
}

export function lastWrittenHash(slug: string): string | undefined {
  return hashes.get(slug)
}

function assertSlug(slug: string): void {
  if (!ID_RE.test(slug)) throw new Error(`invalid slug "${slug}"`)
}

const fileFor = (slug: string, dir: string) => path.join(dir, `${slug}.json`)

export async function readPlan(slug: string, dir = plansDir()): Promise<Plan | null> {
  assertSlug(slug)
  try {
    return JSON.parse(await readFile(fileFor(slug, dir), 'utf8')) as Plan
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === 'ENOENT') return null
    throw e
  }
}

export async function writePlan(slug: string, plan: Plan, dir = plansDir()): Promise<Plan> {
  assertSlug(slug)
  const errors = validatePlan(plan)
  if (errors.length) throw new Error(errors.join('; '))
  const text = serializePlan(plan)
  await mkdir(dir, { recursive: true })
  const target = fileFor(slug, dir)
  const tmp = `${target}.${process.pid}-${randomBytes(4).toString('hex')}.tmp`
  await writeFile(tmp, text, 'utf8')
  await rename(tmp, target)
  hashes.set(slug, hashOf(text))
  return JSON.parse(text) as Plan
}

export async function listPlans(dir = plansDir()): Promise<PlanSummary[]> {
  let files: string[]
  try {
    files = await readdir(dir)
  } catch (e) {
    if ((e as NodeJS.ErrnoException).code === 'ENOENT') return []
    throw e
  }
  const slugs = files.filter(f => f.endsWith('.json')).map(f => f.slice(0, -5)).filter(s => ID_RE.test(s)).sort()
  const out: PlanSummary[] = []
  for (const slug of slugs) {
    let plan: Plan | null
    try {
      plan = await readPlan(slug, dir)
    } catch (e) {
      if (e instanceof SyntaxError) continue // skip corrupt / half-edited files
      throw e
    }
    if (plan && Array.isArray(plan.nodes)) out.push({ slug, name: plan.name, nodeCount: plan.nodes.length })
  }
  return out
}

export async function createPlan(name: string, dir = plansDir()): Promise<{ slug: string; plan: Plan }> {
  const slug = slugify(name)
  if (await readPlan(slug, dir)) throw new PlanExistsError(`plan "${slug}" already exists`)
  const plan = await writePlan(slug, { name, nodes: [] }, dir)
  return { slug, plan }
}
