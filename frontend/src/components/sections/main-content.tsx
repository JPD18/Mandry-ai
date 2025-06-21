"use client"

import { motion } from "framer-motion"
import { useRouter } from "next/navigation"

export default function MainContentComponent() {
  const router = useRouter()

  function handleGetStartedClick() {
    router.push('/login')
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, delay: 0.1 }} // Quick content entrance
      className="min-h-screen" // Removed background since it's now on the parent
    >
      {/* Font loading */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
        
        .misto-font {
          font-family: 'Misto', sans-serif;
        }
      `}</style>

      {/* Main Content */}
      <div className="pt-20 min-h-screen flex flex-col">
        <HeroSection onGetStartedClick={handleGetStartedClick} />
      </div>
    </motion.div>
  )
}

function HeroSection({ onGetStartedClick }: { onGetStartedClick: () => void }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }} // Quick hero entrance
      className="flex-1 flex items-center justify-center px-6"
    >
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.4 }} // Quick title
            className="text-6xl font-bold text-white mb-6 misto-font"
          >
            Welcome to Mandry
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.4 }} // Quick subtitle
            className="text-2xl text-gray-300 mb-12 max-w-3xl mx-auto"
          >
            Your digital compass for navigating endless possibilities with precision and style
          </motion.p>

          {/* Call to Action Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.4 }} // Quick button
            className="mb-16"
          >
            <motion.button
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.98 }}
              onClick={onGetStartedClick}
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
              transition={{ delay: 0.8, duration: 0.3 }} // Quick final text
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