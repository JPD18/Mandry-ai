"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

/* ────────────────────────────
   TYPES
   ──────────────────────────── */
type GuardRender = (args: { username: string }) => React.ReactNode

interface AuthGuardProps {
  children: GuardRender
}

/* ────────────────────────────
   COMPONENT
   ──────────────────────────── */
export default function AuthGuard({ children }: AuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [username, setUsername] = useState('')
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    
    if (token && storedUsername) {
      setIsAuthenticated(true)
      setUsername(storedUsername)
    } else {
      // Redirect to login if not authenticated
      router.push('/login')
    }
    setLoading(false)
  }, [router])

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  // Only show the main content if authenticated
  if (!isAuthenticated) {
    return null // This shouldn't show as we redirect above, but just in case
  }

  return <>{children({ username })}</>
}
