"use client"

import type React from "react"
import { useState } from "react"
import { ArrowLeft } from "lucide-react"
import { useRouter } from 'next/navigation'

export default function AuthPage() {
  const [isSignUp, setIsSignUp] = useState(false)
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Validate passwords match for signup
    if (isSignUp && formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      setLoading(false)
      return
    }

    // Validate password length for signup
    if (isSignUp && formData.password.length < 8) {
      setError('Password must be at least 8 characters long')
      setLoading(false)
      return
    }

    try {
      const endpoint = isSignUp ? 'http://localhost:8000/api/signup/' : 'http://localhost:8000/api/login/'
      const payload = isSignUp 
        ? {
            username: formData.username,
            email: formData.email,
            password: formData.password
          }
        : {
            username: formData.username,
            password: formData.password
          }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (response.ok) {
        // Store token in localStorage
        localStorage.setItem('token', data.token)
        localStorage.setItem('user_id', data.user_id)
        localStorage.setItem('username', data.username)
        
        // Redirect to dashboard
        router.push('/dashboard')
      } else {
        setError(data.error || (isSignUp ? 'Signup failed' : 'Login failed'))
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleBackClick = () => {
    router.push('/')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Font loading */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
        
        .misto-font {
          font-family: 'Misto', sans-serif;
        }
      `}</style>

      <main className="relative min-h-screen flex items-center justify-center px-6">
        <div className="absolute top-6 left-6">
          <button 
            onClick={handleBackClick}
            className="text-yellow-400 hover:text-yellow-300 transition-all duration-200"
          >
            <ArrowLeft
              size={24}
              className="drop-shadow-[0_0_8px_rgba(255,243,9,0.6)] hover:drop-shadow-[0_0_12px_rgba(255,243,9,0.8)]"
            />
          </button>
        </div>
        <div className="w-full max-w-md">
          {/* Header Section */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white misto-font mb-4">
              {isSignUp ? "Join Mandry AI" : "Welcome to Mandry AI"}
            </h1>
            <p className="text-xl text-gray-300">
              {isSignUp
                ? "Start your journey with our AI-powered visa and immigration assistant"
                : "Your AI-powered visa and immigration consultant assistant"}
            </p>
          </div>

          {/* Form Card */}
          <div className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8">
            <div className="text-center mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">{isSignUp ? "Create account" : "Sign in"}</h2>
              <p className="text-gray-300">
                {isSignUp
                  ? "Enter your information to create your account"
                  : "Enter your credentials to access your account"}
              </p>
            </div>

            {error && (
              <div className="mb-6 p-3 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username Field */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-white mb-2">
                  Username
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  placeholder={isSignUp ? "Choose a username" : "Enter your username"}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                />
              </div>

              {/* Email Field (only for sign up) */}
              {isSignUp && (
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    placeholder="Enter your email"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    required
                  />
                </div>
              )}

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-white mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder={isSignUp ? "Create a password (min 8 characters)" : "Enter your password"}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  required
                  minLength={isSignUp ? 8 : undefined}
                />
              </div>

              {/* Confirm Password Field (only for sign up) */}
              {isSignUp && (
                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-white mb-2">
                    Confirm Password
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm your password"
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    required
                  />
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-6 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-300 hover:to-yellow-400 text-slate-900 font-semibold rounded-lg transition-all duration-200 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 focus:ring-offset-transparent disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
              >
                {loading 
                  ? (isSignUp ? "Creating account..." : "Signing in...") 
                  : (isSignUp ? "Create account" : "Sign in")
                }
              </button>
            </form>

            {/* Toggle Link */}
            <div className="text-center mt-6">
              <p className="text-gray-300">
                {isSignUp ? "Already have an account? " : "Don't have an account? "}
                <button
                  onClick={() => {
                    setIsSignUp(!isSignUp)
                    setError('')
                    setFormData({
                      username: "",
                      email: "",
                      password: "",
                      confirmPassword: "",
                    })
                  }}
                  className="text-yellow-400 hover:text-yellow-300 font-medium transition-colors duration-200"
                >
                  {isSignUp ? "Sign in" : "Sign up"}
                </button>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 