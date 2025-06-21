'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { MandryStarIcon } from '@/components/mandry-icon'
import { STAR_ID } from '@/lib/constants'

export default function SiteHeader() {
  const pathname = usePathname()
  
  return (
    <motion.nav 
      className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10 transition-all duration-300"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link 
            href="/" 
            className="flex items-center space-x-3 hover:opacity-80 transition-opacity duration-200"
          >
            <motion.div layoutId={STAR_ID}>
              <MandryStarIcon size={40} uniqueId="header" />
            </motion.div>
            <span className="font-bold text-xl text-white">Mandry AI</span>
          </Link>
          
          {pathname !== '/dashboard' ? (
            <Link
              href="/dashboard"
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Chat
            </Link>
          ) : (
            <span className="text-gray-500 font-medium cursor-default">
              Chat
            </span>
          )}
          
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
        </div>

        <div className="flex items-center space-x-4">
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
        </div>
      </div>
    </motion.nav>
  )
} 