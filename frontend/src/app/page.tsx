'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [username, setUsername] = useState('')
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [askLoading, setAskLoading] = useState(false)
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

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    router.push('/login')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setAskLoading(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/ask/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      setAnswer(data.answer || 'No response received')
    } catch (error) {
      setAnswer('Error: Could not get response from server')
    } finally {
      setAskLoading(false)
    }
  }

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

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">
          Welcome to Mandry AI, {username}!
        </h1>
        <p className="text-xl text-gray-600">
          Your AI-powered visa and immigration consultant assistant
        </p>
        <Button 
          onClick={handleLogout}
          variant="outline"
          className="ml-4"
        >
          Logout
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Ask a Question</CardTitle>
          <CardDescription>
            Get AI-powered assistance with your visa and immigration questions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Textarea
              placeholder="What would you like to know about visas or immigration?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="min-h-[100px]"
            />
            <Button 
              type="submit" 
              disabled={askLoading || !question.trim()}
              className="w-full"
            >
              {askLoading ? 'Getting answer...' : 'Ask Question'}
            </Button>
          </form>

          {answer && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Answer:</h3>
              <p className="text-gray-700">{answer}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 