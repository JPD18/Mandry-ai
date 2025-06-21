'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronUp, User, MapPin, Globe, Target, Clock, MessageSquare, RefreshCw, Trash2 } from 'lucide-react'

interface UserProfile {
  nationality: string
  current_location: string
  destination_country: string
  visa_intent: string
  structured_data: Record<string, any>
  profile_context: string
  conversation_insights: string
  missing_context: string[]
  context_sufficient: boolean
  created_at: string
  updated_at: string
}

interface ProfileDropdownProps {
  isExpanded: boolean
  onToggle: () => void
  refreshTrigger?: number // Increment this to trigger a refresh
}

export function ProfileDropdown({ isExpanded, onToggle, refreshTrigger = 0 }: ProfileDropdownProps) {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [clearLoading, setClearLoading] = useState(false)

  const fetchProfile = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/profile/', {
        method: 'GET',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      } else {
        setError('Failed to fetch profile')
      }
    } catch (err) {
      setError('Error fetching profile')
      console.error('Profile fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Fetch profile when component mounts or when refreshTrigger changes
  useEffect(() => {
    fetchProfile()
  }, [refreshTrigger])

  // Auto-refresh when expanded
  useEffect(() => {
    if (isExpanded) {
      fetchProfile()
    }
  }, [isExpanded])

  const getCompletionPercentage = () => {
    if (!profile) return 0
    
    let score = 0
    if (profile.nationality) score += 25
    if (profile.visa_intent) score += 25
    if (profile.current_location) score += 15
    if (profile.destination_country) score += 15
    
    // Additional context: either conversation_insights OR structured_data OR profile_context
    const hasAdditionalContext = 
      (profile.conversation_insights && profile.conversation_insights.trim()) ||
      (profile.structured_data && Object.keys(profile.structured_data).length > 0) ||
      (profile.profile_context && profile.profile_context.trim())
    
    if (hasAdditionalContext) score += 20
    
    return Math.min(score, 100)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const clearProfile = async () => {
    if (!confirm('Are you sure you want to clear your profile? This action cannot be undone.')) {
      return
    }

    setClearLoading(true)
    setError(null)
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/profile/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        // Refresh the profile data after clearing
        await fetchProfile()
      } else {
        setError('Failed to clear profile')
      }
    } catch (err) {
      setError('Error clearing profile')
      console.error('Profile clear error:', err)
    } finally {
      setClearLoading(false)
    }
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <User className="h-5 w-5" />
            Profile Information
            {profile && (
              <span className="text-sm font-normal text-gray-500">
                ({getCompletionPercentage()}% complete)
              </span>
            )}
          </CardTitle>
          <div className="flex items-center gap-2">
            {isExpanded && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={fetchProfile}
                  disabled={loading}
                  className="h-8 w-8 p-0"
                  title="Refresh profile"
                >
                  <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearProfile}
                  disabled={loading || clearLoading}
                  className="h-8 w-8 p-0 text-red-500 hover:text-red-700 hover:bg-red-50"
                  title="Clear profile"
                >
                  <Trash2 className={`h-4 w-4 ${clearLoading ? 'animate-pulse' : ''}`} />
                </Button>
              </>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="h-8 w-8 p-0"
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>
        </div>
        
        {/* Completion Progress Bar */}
        {profile && (
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getCompletionPercentage()}%` }}
            />
          </div>
        )}
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          {loading && (
            <div className="flex items-center justify-center py-4">
              <RefreshCw className="h-5 w-5 animate-spin mr-2" />
              Loading profile...
            </div>
          )}

          {error && (
            <div className="text-red-600 text-sm py-2">
              {error}
            </div>
          )}

          {profile && !loading && (
            <div className="space-y-4">
              {/* Core Information */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-blue-600" />
                  <span className="font-medium">Nationality:</span>
                  <span className={profile.nationality ? "text-gray-900" : "text-gray-400"}>
                    {profile.nationality || "Not specified"}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-green-600" />
                  <span className="font-medium">Current Location:</span>
                  <span className={profile.current_location ? "text-gray-900" : "text-gray-400"}>
                    {profile.current_location || "Not specified"}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-purple-600" />
                  <span className="font-medium">Destination:</span>
                  <span className={profile.destination_country ? "text-gray-900" : "text-gray-400"}>
                    {profile.destination_country || "Not specified"}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-orange-600" />
                  <span className="font-medium">Visa Intent:</span>
                  <span className={profile.visa_intent ? "text-gray-900" : "text-gray-400"}>
                    {profile.visa_intent || "Not specified"}
                  </span>
                </div>
              </div>

              {/* Profile Context */}
              {profile.profile_context && (
                <div className="border-t pt-3">
                  <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Profile Context
                  </h4>
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {profile.profile_context}
                  </div>
                </div>
              )}

              {/* Additional Context */}
              {profile.conversation_insights && (
                <div className="border-t pt-3">
                  <h4 className="font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <MessageSquare className="h-4 w-4" />
                    Conversation Insights
                  </h4>
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {profile.conversation_insights.split('\n').map((insight, index) => (
                      <div key={index} className="mb-1">
                        {insight}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Structured Data */}
              {profile.structured_data && Object.keys(profile.structured_data).length > 0 && (
                <div className="border-t pt-3">
                  <h4 className="font-medium text-gray-700 mb-2">Additional Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    {Object.entries(profile.structured_data).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-600 capitalize">{key.replace('_', ' ')}:</span>
                        <span className="text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Status */}
              <div className="border-t pt-3 flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${profile.context_sufficient ? 'bg-green-500' : 'bg-yellow-500'}`} />
                  <span className="text-gray-600">
                    Status: {profile.context_sufficient ? 'Ready for consultation' : 'Gathering information'}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-gray-500">
                  <Clock className="h-3 w-3" />
                  <span>Updated {formatDate(profile.updated_at)}</span>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  )
} 