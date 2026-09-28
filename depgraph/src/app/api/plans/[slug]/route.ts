import { ID_RE, validatePlan, type Plan } from '@/lib/schema'
import { readPlan, writePlan } from '@/lib/store'

export const dynamic = 'force-dynamic'

type Ctx = { params: Promise<{ slug: string }> }

async function slugOf(ctx: Ctx): Promise<string | Response> {
  const { slug } = await ctx.params
  if (!ID_RE.test(slug)) return Response.json({ errors: [`invalid slug "${slug}"`] }, { status: 400 })
  return slug
}

export async function GET(_req: Request, ctx: Ctx) {
  const slug = await slugOf(ctx)
  if (slug instanceof Response) return slug
  const plan = await readPlan(slug)
  if (!plan) return Response.json({ errors: ['not found'] }, { status: 404 })
  return Response.json(plan)
}

export async function PUT(req: Request, ctx: Ctx) {
  const slug = await slugOf(ctx)
  if (slug instanceof Response) return slug
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return Response.json({ errors: ['body must be valid JSON'] }, { status: 400 })
  }
  const errors = validatePlan(body)
  if (errors.length) return Response.json({ errors }, { status: 400 })
  return Response.json(await writePlan(slug, body as Plan))
}
