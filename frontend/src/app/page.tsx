'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { CitationList } from '@/components/ui/citation'
import { MarkdownRenderer } from '@/components/ui/markdown-renderer'
import { ProfileDropdown } from '@/components/ui/profile-dropdown'
import { AlertCircle, CheckCircle, MessageSquare, User, Settings, MessageCircle } from 'lucide-react'

interface Citation {
  title: string
  url: string
  snippet: string
}

interface ChatMessage {
  type: 'human' | 'ai'
  content: string
}

interface LangGraphResponse {
  response: string
  current_step: string
  context_sufficient: boolean
  missing_context_areas: string[]
  session_data: any
  message_history: ChatMessage[]
  error?: string
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [username, setUsername] = useState('')
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([])
  const [currentStep, setCurrentStep] = useState<string>('assess_context')
  const [contextSufficient, setContextSufficient] = useState(false)
  const [sessionState, setSessionState] = useState<any>(null)
  const [chatLoading, setChatLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profileExpanded, setProfileExpanded] = useState(false)
  const [profileRefreshTrigger, setProfileRefreshTrigger] = useState(0)
  const router = useRouter()

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token')
    const storedUsername = localStorage.getItem('username')
    
    if (token && storedUsername) {
      setIsAuthenticated(true)
      setUsername(storedUsername)
      // Auto-initialize conversation with bot greeting
      initializeConversation()
    } else {
      // Redirect to login if not authenticated
      router.push('/login')
    }
    setLoading(false)
  }, [router])

  // Initialize conversation with bot greeting
  const initializeConversation = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ 
          message: "start", // Special message to trigger initial greeting
          session_state: null 
        }),
      })

      const data: LangGraphResponse = await response.json()
      
      if (response.ok) {
        // Filter out the "start" trigger message, keep only the bot's greeting
        const filteredHistory = data.message_history.filter(
          (msg: ChatMessage) => !(msg.type === 'human' && msg.content.toLowerCase().includes('hello, i\'m new here'))
        )
        
        // Update chat state with initial greeting
        setChatHistory(filteredHistory)
        setCurrentStep(data.current_step)
        setContextSufficient(data.context_sufficient)
        setSessionState({
          current_step: data.current_step,
          context_sufficient: data.context_sufficient,
          missing_context_areas: data.missing_context_areas,
          session_data: data.session_data,
          message_history: filteredHistory,
        })
        
        // Trigger initial profile refresh
        setProfileRefreshTrigger(prev => prev + 1)
      }
    } catch (error) {
      console.error('Failed to initialize conversation:', error)
      // Don't show error to user for initialization failure
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    router.push('/login')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return

    setChatLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ 
          message: message,
          session_state: sessionState 
        }),
      })

      const data: LangGraphResponse = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to get response from server')
      }
      
      // Update chat state
      setChatHistory(data.message_history)
      setCurrentStep(data.current_step)
      setContextSufficient(data.context_sufficient)
      setSessionState({
        current_step: data.current_step,
        context_sufficient: data.context_sufficient,
        missing_context_areas: data.missing_context_areas,
        session_data: data.session_data,
        message_history: data.message_history,
      })
      setMessage('') // Clear input
      
      // Trigger profile refresh after bot response
      setProfileRefreshTrigger(prev => prev + 1)
      
    } catch (error) {
      console.error('Chat Error:', error)
      setError(error instanceof Error ? error.message : 'Error: Could not get response from server')
    } finally {
      setChatLoading(false)
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

  const getStepTitle = () => {
    switch (currentStep) {
      case 'assess_context':
        return 'Understanding Your Situation'
      case 'gather_context':
        return 'Learning About You'
      case 'intelligent_qna':
        return 'Visa Consultation'
      case 'end':
        return 'Session Complete'
      default:
        return 'Visa Assistant'
    }
  }

  const getStepDescription = () => {
    switch (currentStep) {
      case 'assess_context':
        return 'Analyzing your visa situation...'
      case 'gather_context':
        return 'Learning about your specific circumstances'
      case 'intelligent_qna':
        return 'Get personalized visa advice based on your situation'
      case 'end':
        return 'Thank you for using Mandry AI!'
      default:
        return 'Your AI-powered visa assistant'
    }
  }

  const getStepIcon = () => {
    switch (currentStep) {
      case 'assess_context':
        return <Settings className="h-5 w-5" />
      case 'gather_context':
        return <User className="h-5 w-5" />
      case 'intelligent_qna':
        return <MessageCircle className="h-5 w-5" />
      case 'end':
        return <CheckCircle className="h-5 w-5" />
      default:
        return <MessageSquare className="h-5 w-5" />
    }
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

      {/* Profile Information Dropdown */}
      <ProfileDropdown 
        isExpanded={profileExpanded}
        onToggle={() => setProfileExpanded(!profileExpanded)}
        refreshTrigger={profileRefreshTrigger}
      />

      {/* Status Indicator */}
      <div className="flex items-center justify-center gap-2 p-4 bg-blue-50 rounded-lg">
        {chatLoading ? <Settings className="h-5 w-5 animate-spin" /> : getStepIcon()}
        <span className="font-medium text-blue-900">
          {contextSufficient 
            ? 'Ready for Questions' 
            : sessionState?.session_data?.context_completeness > 0 
              ? `Context ${sessionState.session_data.context_completeness}% Complete`
              : 'Getting Started'
          }
        </span>
        <span className="text-blue-700">•</span>
        <span className="text-blue-700">{getStepTitle()}</span>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getStepIcon()}
            {getStepTitle()}
          </CardTitle>
          <CardDescription>
            {getStepDescription()}
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {/* Chat History */}
          <div className="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
            {chatHistory.length > 0 ? (
              chatHistory.map((msg, index) => (
                <div key={index} className={`flex ${msg.type === 'human' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                    msg.type === 'human' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-white text-gray-800 border'
                  }`}>
                    <MarkdownRenderer content={msg.content} />
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-500">
                <MessageCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
                <p>Mandry AI is preparing your personalized welcome message...</p>
              </div>
            )}
            
            {/* Loading Indicator */}
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white px-4 py-2 rounded-lg shadow-sm border">
                  <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4 animate-spin" />
                    <span className="text-gray-500">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Message Input */}
          <div className="p-6 border-t">
            <form onSubmit={handleSubmit} className="space-y-4">
              <Textarea
                placeholder={
                  currentStep === 'gather_context' 
                    ? "Tell me your nationality and visa type..."
                    : currentStep === 'assess_context'
                    ? "Respond to my welcome message above..."
                    : "Ask me anything about your visa application..."
                }
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="min-h-[100px]"
                disabled={chatLoading}
              />
              <Button 
                type="submit" 
                disabled={chatLoading || !message.trim()}
                className="w-full"
              >
                {chatLoading ? 'Sending...' : 'Send Message'}
              </Button>
            </form>

            {/* Error Display */}
            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-800 mb-1">Error</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 