"use client"

import { useState, useEffect } from "react"
import { AnimatePresence } from "framer-motion"
import { Splash } from "@/components/splash/splash"
import SiteHeader from "@/components/layout/site-header"
import MainContentComponent from "@/components/sections/main-content"

export default function Home() {
  const [showSplash, setShowSplash] = useState(true)

  useEffect(() => {
    // Check if this is the first visit
    try {
      const hasVisitedBefore = localStorage.getItem("hasVisitedBefore")
      
      if (hasVisitedBefore) {
        // Returning visitor - show content immediately
        setShowSplash(false)
      } else {
        // First time visitor - show splash screen
        localStorage.setItem("hasVisitedBefore", "true")
        // Keep splash visible - let the splash component control timing
      }
    } catch (error) {
      // Fallback if localStorage is not available
      console.warn("localStorage not available:", error)
      setShowSplash(false)
    }
  }, [])

  return (
    <>
      <AnimatePresence>{showSplash && <Splash key="splash" onDone={() => setShowSplash(false)} />}</AnimatePresence>

      {!showSplash && (
        <>
          <SiteHeader />
          <MainContentComponent />
        </>
      )}
    </>
  )
} 