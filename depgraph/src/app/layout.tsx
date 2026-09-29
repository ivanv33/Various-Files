import type { Metadata } from 'next'
import { Instrument_Sans } from 'next/font/google'
import './globals.css'

const sans = Instrument_Sans({ subsets: ['latin'], variable: '--font-sans' })

export const metadata: Metadata = { title: 'depgraph', description: 'Plans as dependency graphs' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${sans.variable}`}>
      <body className="h-screen w-screen overflow-hidden bg-[#05060a] text-white antialiased">{children}</body>
    </html>
  )
}
