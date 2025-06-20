import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Mandry AI - Visa & Immigration Assistant',
  description: 'AI-powered visa and immigration consultant assistant',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto px-4">
            <div className="flex h-14 items-center">
              <Link href="/" className="mr-6 flex items-center space-x-2">
                <span className="font-bold text-xl">Mandry AI</span>
              </Link>
              <nav className="flex items-center space-x-6 text-sm font-medium">
                <Link
                  href="/"
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                >
                  Chat
                </Link>
                <Link
                  href="/upload"
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                >
                  Upload Documents
                </Link>
                <Link
                  href="/reminders"
                  className="transition-colors hover:text-foreground/80 text-foreground/60"
                >
                  Schedule Appointment
                </Link>
              </nav>
            </div>
          </div>
        </nav>
        <main className="container mx-auto px-4 py-6">
          {children}
        </main>
      </body>
    </html>
  )
} 