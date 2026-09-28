import { ID_RE } from '@/lib/schema'
import { subscribe } from '@/lib/watcher'

export const dynamic = 'force-dynamic'

export async function GET(_req: Request, ctx: { params: Promise<{ slug: string }> }) {
  const { slug } = await ctx.params
  if (!ID_RE.test(slug)) return Response.json({ errors: [`invalid slug "${slug}"`] }, { status: 400 })
  const encoder = new TextEncoder()
  let unsubscribe = () => {}
  let ping: ReturnType<typeof setInterval> | undefined
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      const send = (s: string) => {
        try {
          controller.enqueue(encoder.encode(s))
        } catch {
          /* closed */
        }
      }
      send(': connected\n\n')
      unsubscribe = subscribe(changed => {
        if (changed === slug) send('event: changed\ndata: {}\n\n')
      })
      ping = setInterval(() => send(': ping\n\n'), 15000)
    },
    cancel() {
      unsubscribe()
      if (ping) clearInterval(ping)
    },
  })
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
    },
  })
}
