"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { MandryStarIcon } from "./mandry-icon"
import { Button } from "./ui/button"

interface ChatAuthGuardProps {
  children: React.ReactNode
}

export function ChatAuthGuard({ children }: ChatAuthGuardProps) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    setIsAuthenticated(!!token)
  }, [])

  if (isAuthenticated === null) {
    // Loading state
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <MandryStarIcon size={80} className="mx-auto mb-6 animate-pulse" />
          <p className="text-white text-lg">Loading...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <>
      {children}
      {!isAuthenticated && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-12 max-w-md"
          >
            <MandryStarIcon size={80} className="mx-auto mb-6" />
            <h3 className="text-2xl font-bold text-white mb-4">Authentication Required</h3>
            <p className="text-gray-300 mb-8">
              Please log in to access this feature and interact with your AI assistant.
            </p>
            <div className="space-y-4">
              <Button
                onClick={() => router.push("/login")}
                className="w-full bg-gradient-to-r from-[#FFF309] to-[#FFF309]/80 hover:from-[#FFF309]/90 hover:to-[#FFF309]/70 text-slate-900 font-semibold"
              >
                Log In
              </Button>
              <Button
                onClick={() => router.push("/signup")}
                variant="outline"
                className="w-full border-[#FFF309] text-[#FFF309] hover:bg-[#FFF309] hover:text-slate-900"
              >
                Sign Up
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </>
  )
}