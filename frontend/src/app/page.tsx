'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { CitationList } from '@/components/ui/citation'
import { MarkdownRenderer } from '@/components/ui/markdown-renderer'
import { AlertCircle, CheckCircle, MessageSquare } from 'lucide-react'

interface Citation {
  title: string
  url: string
  snippet: string
}

interface ApiResponse {
  answer: string
  citations?: Citation[]
  rag_verified?: boolean
  source_count?: number
  error?: string
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [username, setUsername] = useState('')
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState<ApiResponse | null>(null)
  const [askLoading, setAskLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
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
    setError(null)
    setResponse(null)
    
    try {
      const token = localStorage.getItem('token')
      const apiResponse = await fetch('http://localhost:8000/api/ask/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ question }),
      })

      const data: ApiResponse = await apiResponse.json()
      
      if (!apiResponse.ok) {
        throw new Error(data.error || 'Failed to get response from server')
      }
      
      setResponse(data)
    } catch (error) {
      console.error('API Error:', error)
      setError(error instanceof Error ? error.message : 'Error: Could not get response from server')
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
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Ask a Question
          </CardTitle>
          <CardDescription>
            Get AI-powered assistance with your visa and immigration questions, backed by official sources
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

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-800 mb-1">Error</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Response Display */}
          {response && (
            <div className="mt-6 space-y-4">
              {/* Status Indicator */}
              <div className="flex items-center gap-2 text-sm">
                {response.rag_verified ? (
                  <>
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-green-700 font-medium">
                      Verified with {response.source_count || 0} official sources
                    </span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="h-4 w-4 text-amber-500" />
                    <span className="text-amber-700 font-medium">
                      Verification temporarily unavailable
                    </span>
                  </>
                )}
              </div>

              {/* Answer Section */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <MessageSquare className="h-4 w-4" />
                  Answer:
                </h3>
                <MarkdownRenderer 
                  content={response.answer} 
                  className="text-gray-800"
                />
              </div>

              {/* Citations Section */}
              {response.citations && response.citations.length > 0 && (
                <CitationList 
                  citations={response.citations} 
                  ragVerified={response.rag_verified}
                />
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 