'use client'

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    
    if (token && storedUsername) {
      setIsAuthenticated(true)
      setUsername(storedUsername)
    }
    setLoading(false)
  }, [pathname])

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    setIsAuthenticated(false)
    setUsername('')
    router.push('/login')
  }

  // Don't show navigation on auth pages
  const isAuthPage = pathname === '/login' || pathname === '/signup'

  return (
    <html lang="en">
      <body className={inter.className}>
        {!isAuthPage && (
          <nav className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container mx-auto px-4">
              <div className="flex h-14 items-center">
                <Link href="/" className="mr-6 flex items-center space-x-2">
                  <span className="font-bold text-xl">Mandry AI</span>
                </Link>
                
                {isAuthenticated ? (
                  <>
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
                    <div className="ml-auto flex items-center space-x-4">
                      <span className="text-sm text-gray-600">
                        Welcome, {username}
                      </span>
                      <button
                        onClick={handleLogout}
                        className="text-sm transition-colors hover:text-foreground/80 text-foreground/60"
                      >
                        Logout
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="ml-auto flex items-center space-x-4">
                    <Link
                      href="/login"
                      className="transition-colors hover:text-foreground/80 text-foreground/60"
                    >
                      Login
                    </Link>
                    <Link
                      href="/signup"
                      className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-3"
                    >
                      Sign Up
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </nav>
        )}
        <main className={isAuthPage ? "" : "container mx-auto px-4 py-6"}>
          {children}
        </main>
      </body>
    </html>
  )
} 