import { createPlan, listPlans, PlanExistsError } from '@/lib/store'

export const dynamic = 'force-dynamic'

export async function GET() {
  return Response.json(await listPlans())
}

export async function POST(req: Request) {
  let body: unknown
  try {
    body = await req.json()
  } catch {
    return Response.json({ errors: ['body must be valid JSON'] }, { status: 400 })
  }
  const name = (body as { name?: unknown })?.name
  if (typeof name !== 'string' || !name.trim()) {
    return Response.json({ errors: ['name must be a non-empty string'] }, { status: 400 })
  }
  try {
    return Response.json(await createPlan(name.trim()), { status: 201 })
  } catch (e) {
    if (e instanceof PlanExistsError) return Response.json({ errors: [e.message] }, { status: 409 })
    throw e
  }
}
