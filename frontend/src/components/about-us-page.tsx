"use client"

import { motion } from "framer-motion"
import { Navbar } from "./Navbar"

export default function AboutUsPage() {
  return (
    <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Font loading */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
        
        .misto-font {
          font-family: 'Misto', sans-serif;
        }
      `}</style>

      <Navbar 
        showAboutUs={true}
        showChat={true}
        showSchedule={true}
      />

      <div className="pt-20 h-full flex flex-col">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex-1 px-6 py-12"
        >
          <div className="max-w-7xl mx-auto">
            {/* About Us Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-center mb-12"
            >
              <h1 className="text-5xl font-bold text-white mb-4 misto-font">Our Story: Your Journey, Our Passion</h1>
            </motion.div>

            {/* Content Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 px-8 py-16"
            >
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="max-w-4xl mx-auto"
              >
                <p className="text-lg text-gray-300 leading-relaxed mb-6">
                  We know navigating visas and immigration can feel overwhelming. That's why, at Mandry AI, we're dedicated to making your journey <strong className="text-white">straightforward and stress-free</strong>. Our name, "Mandry," means "travels" in Ukrainian – a perfect fit for our passion to help you <strong className="text-white">begin your new chapter with ease</strong>.
                </p>
                
                <p className="text-lg text-gray-300 leading-relaxed">
                  Born from our <strong className="text-white">diverse international backgrounds</strong>, our founders, from Ukraine and South Africa, have <strong className="text-white">personally experienced the challenges of global movement</strong>. That's why we built Mandry AI – to offer the <strong className="text-white">guidance and support we wished we had ourselves</strong>, making your journey much simpler.
                </p>
              </motion.div>
            </motion.div>
          </div>
        </motion.section>
      </div>
    </div>
  )
} 