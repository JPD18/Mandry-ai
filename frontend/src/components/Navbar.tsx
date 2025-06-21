"use client"

import { MandryStarIcon } from "./mandry-icon"
import { useRouter, usePathname } from "next/navigation"
import { useState, useEffect } from "react"

interface NavbarProps {
  onLogoClick?: () => void
  onChatClick?: () => void
  onAboutUsClick?: () => void
  onScheduleClick?: () => void
  onLoginClick?: () => void
  onSignUpClick?: () => void
  showAboutUs?: boolean
  showChat?: boolean
  showSchedule?: boolean
  className?: string
}

export function Navbar({
  onLogoClick,
  onChatClick,
  onAboutUsClick,
  onScheduleClick,
  onLoginClick,
  onSignUpClick,
  showAboutUs = true,
  showChat = true,
  showSchedule = true,
  className = "",
}: NavbarProps) {
  const router = useRouter()
  const pathname = usePathname()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check authentication status on component mount
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    
    if (token && storedUsername) {
      setIsAuthenticated(true)
      setUsername(storedUsername)
    } else {
      setIsAuthenticated(false)
    }
    setLoading(false)
  }, [])

  const handleLogout = async () => {
    try {
      const token = localStorage.getItem('token')
      
      // Call backend logout endpoint
      const response = await fetch('http://localhost:8000/api/logout/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      // Clear local storage regardless of backend response
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      
      // Update state
      setIsAuthenticated(false)
      setUsername('')
      
      // Redirect to home page
      router.push('/')
    } catch (error) {
      console.error('Logout error:', error)
      // Still clear local storage and redirect even if backend call fails
      localStorage.removeItem('token')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      setIsAuthenticated(false)
      setUsername('')
      router.push('/')
    }
  }

  // Debug logging
  console.log('Current pathname:', pathname)

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10 transition-all duration-300 ${className}`}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <button
            onClick={() => router.push("/")}
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity duration-200"
          >
            <MandryStarIcon size={40} />
          </button>

          {showAboutUs && (
            (pathname === '/about' || pathname.startsWith('/about')) ? (
              <span className="text-yellow-400 font-medium cursor-default">
                About Us
              </span>
            ) : (
              <button
                onClick={() => router.push("/about")}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                About Us
              </button>
            )
          )}

          {showAboutUs && showChat && (
            <span className="text-yellow-400/60">|</span>
          )}

          {showChat && (
            (pathname === '/dashboard' || pathname.startsWith('/dashboard')) ? (
              <span className="text-yellow-400 font-medium cursor-default">
                Chat
              </span>
            ) : (
              <button
                onClick={() => router.push("/dashboard")}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                Chat
              </button>
            )
          )}

          {showChat && showSchedule && (
            <span className="text-yellow-400/60">|</span>
          )}

          {showSchedule && (
            (pathname === '/reminders' || pathname.startsWith('/reminders')) ? (
              <span className="text-yellow-400 font-medium cursor-default">
                Schedule
              </span>
            ) : (
              <button
                onClick={() => router.push("/reminders")}
                className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
              >
                Schedule
              </button>
            )
          )}
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-4">
          {!loading && (
            <>
              {isAuthenticated ? (
                <div className="flex items-center space-x-4">
                  <span className="text-gray-300 text-sm">
                    Welcome, {username}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="px-6 py-2 border-2 border-red-400 text-red-400 hover:bg-red-400 hover:text-white font-semibold rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    Log Out
                  </button>
                </div>
              ) : (
                <>
                  <button
                    onClick={() => router.push("/login")}
                    className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
                  >
                    Log In
                  </button>
                  <button
                    onClick={() => router.push("/signup")}
                    className="px-6 py-2 border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-slate-900 font-semibold rounded-lg transition-all duration-200 hover:scale-105"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </>
          )}
        </div>
      </div>
    </nav>
  )
} 