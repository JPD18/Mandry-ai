'use client'

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'
import { MandryStarIcon } from '@/components/mandry-icon'

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
          <nav className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10 transition-all duration-300">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
              <div className="flex items-center space-x-8">
                <Link 
                  href={isAuthenticated ? "/dashboard" : "/"} 
                  className="flex items-center space-x-3 hover:opacity-80 transition-opacity duration-200"
                >
                  <MandryStarIcon size={40} />
                  <span className="font-bold text-xl text-white">Mandry AI</span>
                </Link>
                
                {/* About Us Button */}
                {pathname !== '/about' ? (
                  <Link
                    href="/about"
                    className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                  >
                    About Us
                  </Link>
                ) : (
                  <span className="text-gray-500 font-medium cursor-default">
                    About Us
                  </span>
                )}
                
                {isAuthenticated && (
                  <nav className="flex items-center space-x-6 text-sm font-medium">
                    <Link
                      href="/dashboard"
                      className={`transition-colors duration-200 ${
                        pathname === '/dashboard' 
                          ? "text-gray-500 cursor-default" 
                          : "text-gray-300 hover:text-white"
                      }`}
                    >
                      Chat
                    </Link>
                    <Link
                      href="/upload"
                      className={`transition-colors duration-200 ${
                        pathname === '/upload' 
                          ? "text-gray-500 cursor-default" 
                          : "text-gray-300 hover:text-white"
                      }`}
                    >
                      Upload Documents
                    </Link>
                    <Link
                      href="/reminders"
                      className={`transition-colors duration-200 ${
                        pathname === '/reminders' 
                          ? "text-gray-500 cursor-default" 
                          : "text-gray-300 hover:text-white"
                      }`}
                    >
                      Schedule Appointment
                    </Link>
                  </nav>
                )}
              </div>

              {/* Auth Buttons */}
              <div className="flex items-center space-x-4">
                {isAuthenticated ? (
                  <>
                    <span className="text-gray-300 text-sm">
                      Welcome, {username}
                    </span>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 border border-gray-600 text-gray-300 hover:bg-gray-800 hover:text-white font-medium rounded-lg transition-all duration-200"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    {pathname !== '/login' && pathname !== '/signup' ? (
                      <>
                        <Link
                          href="/login"
                          className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                        >
                          Log In
                        </Link>
                        <Link
                          href="/signup"
                          className="px-6 py-2 border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-slate-900 font-semibold rounded-lg transition-all duration-200 hover:scale-105"
                        >
                          Sign Up
                        </Link>
                      </>
                    ) : (
                      <>
                        <span className="text-gray-500 font-medium cursor-default">
                          Log In
                        </span>
                        <span className="px-6 py-2 border-2 border-gray-600 text-gray-500 font-semibold rounded-lg cursor-default">
                          Sign Up
                        </span>
                      </>
                    )}
                  </>
                )}
              </div>
            </div>
          </nav>
        )}
        <main className={isAuthPage ? "" : "pt-20"}>
          {children}
        </main>
      </body>
    </html>
  )
} 