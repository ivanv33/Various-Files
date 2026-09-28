import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = { title: 'depgraph', description: 'Plans as dependency graphs' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="h-screen w-screen overflow-hidden bg-[#05060a] text-white antialiased">{children}</body>
    </html>
  )
}
