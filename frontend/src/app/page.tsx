"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useRouter } from 'next/navigation'
import { MandryBaseIcon, MandryStarIcon } from "@/components/mandry-icon"

export default function HomePage() {
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem('token')
    const username = localStorage.getItem('username')
    
    if (token && username) {
      // User is authenticated, redirect to dashboard
      router.push('/dashboard')
      return
    }

    // Simulate loading time
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 3000) // 3 seconds loading time

    return () => clearTimeout(timer)
  }, [router])

  const handleGetStartedClick = () => {
    router.push('/login')
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 overflow-hidden">
      <AnimatePresence mode="wait">
        {isLoading ? <LoadingScreen key="loading" /> : <MainContent key="main" />}
      </AnimatePresence>
    </div>
  )

  function LoadingScreen() {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col items-center justify-center min-h-screen"
      >
        <div className="flex flex-col items-center space-y-8">
          {/* Layered Mandry Icon with Rotating Star */}
          <div className="relative flex items-center justify-center">
            {/* Static Base Compass */}
            <MandryBaseIcon size={120} className="drop-shadow-2xl" />

            {/* Rotating Star Element - centered properly */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{
                duration: 3,
                repeat: Number.POSITIVE_INFINITY,
                ease: "linear",
              }}
              className="absolute inset-0 flex items-center justify-center"
              style={{ transformOrigin: "center center" }}
            >
              <MandryStarIcon size={120} />
            </motion.div>
          </div>

          {/* Loading Text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-4">Loading...</h2>
            <div className="flex space-x-2 justify-center">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.4, 1, 0.4],
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Number.POSITIVE_INFINITY,
                    delay: i * 0.3,
                  }}
                  className="w-3 h-3 bg-yellow-400 rounded-full"
                />
              ))}
            </div>
          </motion.div>

          {/* Optional progress indicator */}
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 3, ease: "easeInOut" }}
            className="w-64 h-1 bg-gray-700 rounded-full overflow-hidden"
          >
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: "100%" }}
              transition={{ duration: 3, ease: "easeInOut" }}
              className="h-full bg-gradient-to-r from-yellow-400 to-yellow-300 rounded-full"
            />
          </motion.div>
        </div>
      </motion.div>
    )
  }

  function MainContent() {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed inset-0 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 overflow-hidden"
      >
        {/* Font loading */}
        <style jsx global>{`
          @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
          
          .misto-font {
            font-family: 'Misto', sans-serif;
          }
        `}</style>

        {/* Main Content */}
        <div className="absolute inset-0 flex flex-col">
          <HeroSection />
        </div>
      </motion.div>
    )
  }

  function HeroSection() {
    return (
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="flex-1 flex items-center justify-center px-6 py-32"
      >
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-6xl font-bold text-white mb-6 misto-font"
            >
              Welcome to Mandry
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-2xl text-gray-300 mb-12 max-w-3xl mx-auto"
            >
              Your digital compass for navigating endless possibilities with precision and style
            </motion.p>

            {/* Call to Action Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="mb-16"
            >
              <motion.button
                whileHover={{ scale: 1.05, y: -2 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleGetStartedClick}
                className="group relative px-12 py-6 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-300 hover:to-yellow-400 text-slate-900 font-bold text-xl rounded-2xl shadow-2xl hover:shadow-yellow-500/25 transition-all duration-300 border-2 border-yellow-300/50 hover:border-yellow-200"
              >
                <div className="flex items-center space-x-3">
                  <span>Let's Get Started</span>
                </div>

                {/* Outer glow layer */}
                <div className="absolute inset-0 rounded-2xl bg-yellow-400/20 blur-3xl group-hover:blur-[40px] group-hover:bg-yellow-300/30 transition-all duration-500 -z-20 scale-110"></div>

                {/* Enhanced glow effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-yellow-400/30 to-yellow-500/30 blur-2xl group-hover:blur-3xl group-hover:from-yellow-300/40 group-hover:to-yellow-400/40 transition-all duration-300 -z-10"></div>
              </motion.button>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7, duration: 0.6 }}
                className="text-gray-400 text-sm mt-4"
              >
                Launch the Mandry Assistant and begin exploring
              </motion.p>
            </motion.div>
          </div>
        </div>
      </motion.section>
    )
  }
} 