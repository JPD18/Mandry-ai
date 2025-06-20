'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Calendar, Clock, User, CheckCircle, AlertCircle } from 'lucide-react'

export default function RemindersPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState({
    user: '',
    type: 'consultation',
    date: '',
    time: '',
    notes: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    message: string
  } | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
    } else {
      router.push('/login')
    }
    setLoading(false)
  }, [router])

  const appointmentTypes = [
    { value: 'consultation', label: 'Consultation' },
    { value: 'document_review', label: 'Document Review' },
    { value: 'application_submission', label: 'Application Submission' },
    { value: 'interview_prep', label: 'Interview Preparation' }
  ]

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.user || !formData.date || !formData.time) {
      setResult({
        success: false,
        message: 'Please fill in all required fields.'
      })
      return
    }

    setIsSubmitting(true)
    setResult(null)

    try {
      // Combine date and time into ISO format
      const iso_date = new Date(`${formData.date}T${formData.time}`).toISOString()
      
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/schedule/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({
          user: formData.user,
          type: formData.type,
          iso_date: iso_date
        }),
      })

      const data = await response.json()

      if (response.ok) {
        setResult({
          success: true,
          message: `Appointment scheduled successfully! Appointment ID: ${data.appointment_id}`
        })
        // Reset form
        setFormData({
          user: '',
          type: 'consultation',
          date: '',
          time: '',
          notes: ''
        })
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to schedule appointment. Please try again.'
        })
      }
    } catch (error) {
      console.error('Scheduling error:', error)
      setResult({
        success: false,
        message: 'Failed to schedule appointment. Please check your connection and try again.'
      })
    } finally {
      setIsSubmitting(false)
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

  // Only show the content if authenticated
  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Schedule Appointment</CardTitle>
          <CardDescription>
            Book a consultation or appointment for visa and immigration services.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label htmlFor="user" className="text-sm font-medium">
                Full Name *
              </label>
              <Input
                id="user"
                name="user"
                value={formData.user}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                required
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="type" className="text-sm font-medium">
                Appointment Type *
              </label>
              <select
                id="type"
                name="type"
                value={formData.type}
                onChange={handleInputChange}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                required
              >
                {appointmentTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="date" className="text-sm font-medium">
                  Date *
                </label>
                <Input
                  id="date"
                  name="date"
                  type="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  min={new Date().toISOString().split('T')[0]}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <label htmlFor="time" className="text-sm font-medium">
                  Time *
                </label>
                <Input
                  id="time"
                  name="time"
                  type="time"
                  value={formData.time}
                  onChange={handleInputChange}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <label htmlFor="notes" className="text-sm font-medium">
                Additional Notes
              </label>
              <Textarea
                id="notes"
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Any specific requirements or information..."
                rows={3}
              />
            </div>

            {result && (
              <div
                className={`flex items-center space-x-2 p-4 rounded-lg ${
                  result.success
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-red-50 text-red-700 border border-red-200'
                }`}
              >
                {result.success ? (
                  <CheckCircle className="h-5 w-5" />
                ) : (
                  <AlertCircle className="h-5 w-5" />
                )}
                <p className="text-sm">{result.message}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={isSubmitting}
              className="w-full"
            >
              <Calendar className="mr-2 h-4 w-4" />
              {isSubmitting ? 'Scheduling...' : 'Schedule Appointment'}
            </Button>
          </form>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <p className="text-sm font-medium">Business Hours</p>
            </div>
            <p className="text-sm text-muted-foreground">
              Monday - Friday: 9:00 AM - 6:00 PM<br />
              Saturday: 10:00 AM - 4:00 PM<br />
              Sunday: Closed
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 