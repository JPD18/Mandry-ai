"use client"

import { MandryStarIcon } from "./mandry-icon"
import { useRouter } from "next/navigation"

interface NavbarProps {
  onLogoClick?: () => void
  onChatClick?: () => void
  onAboutUsClick?: () => void
  onLoginClick?: () => void
  onSignUpClick?: () => void
  showAboutUs?: boolean
  showChat?: boolean
  className?: string
}

export function Navbar({
  onLogoClick,
  onChatClick,
  onAboutUsClick,
  onLoginClick,
  onSignUpClick,
  showAboutUs = true,
  showChat = true,
  className = "",
}: NavbarProps) {
  const router = useRouter()

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

          {showChat && (
            <button
              onClick={() => router.push("/dashboard")}
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              Chat
            </button>
          )}

          {showAboutUs && (
            <button
              onClick={() => router.push("/about")}
              className="text-gray-300 hover:text-white transition-colors duration-200 font-medium"
            >
              About Us
            </button>
          )}
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center space-x-4">
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
        </div>
      </div>
    </nav>
  )
} 