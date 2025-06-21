"use client"

import { useEffect } from "react"
import { motion, useAnimation } from "framer-motion"
import { MandryBaseIcon, MandryStarIcon } from "@/components/mandry-icon"
import { STAR_ID } from "@/lib/constants"

export function Splash({ onDone }: { onDone: () => void }) {
  const controls = useAnimation()

  // run rotation for 0.33 seconds, then call onDone()
  useEffect(() => {
    let isMounted = true

    const runAnimation = async () => {
      try {
        // Make the star rotate twice for a more pronounced effect
        await controls.start({
          rotate: 720,
          transition: { duration: 1.2, ease: "circOut" },
        })

        if (isMounted) {
          onDone()
        }
      } catch (error) {
        console.warn("Animation error:", error)
        if (isMounted) {
          onDone()
        }
      }
    }

    runAnimation()

    // Cleanup function
    return () => {
      isMounted = false
      controls.stop()
    }
  }, [controls, onDone])

  return (
    <motion.div
      className="fixed inset-0 flex items-center justify-center
                 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800"
      initial={{ opacity: 1 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 1 }} // Keep background visible
    >
      {/* Layered Mandry Icon with Rotating Star */}
      <div className="relative flex items-center justify-center">
        {/* Static Base Compass - only this disappears */}
        <motion.div
          initial={{ opacity: 1, scale: 1 }}
          exit={{
            opacity: 0,
            scale: 0.3,
            filter: "blur(20px)",
            transition: {
              duration: 0.5, // Quick dissolve
              ease: "easeInOut",
            },
          }}
        >
          <MandryBaseIcon size={120} className="drop-shadow-2xl" />
        </motion.div>

        {/* star in centre - shared with navbar, stays visible */}
        <motion.div
          layoutId={STAR_ID} // 🪄 shared with navbar
          animate={controls}
          className="absolute inset-0 flex items-center justify-center"
          style={{ transformOrigin: "center center" }}
        >
          <MandryStarIcon size={120} uniqueId="splash" />
        </motion.div>
      </div>
    </motion.div>
  )
} 