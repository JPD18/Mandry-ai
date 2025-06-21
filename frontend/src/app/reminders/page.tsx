'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { ReminderDashboard } from '@/components/ReminderDashboard'
import { 
  Calendar, 
  Clock, 
  User, 
  CheckCircle, 
  AlertCircle, 
  Bell,
  Plus,
  List,
  AlertTriangle,
  FileText,
  UserCheck,
  Briefcase,
  MessageSquare,
  Trash2,
  Edit
} from 'lucide-react'

interface Reminder {
  id: number
  title: string
  description: string
  reminder_type: string
  target_date: string
  reminder_date: string
  status: string
  priority: string
  email_sent: boolean
  created_at: string
}

export default function RemindersPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'create' | 'list'>('list')
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loadingReminders, setLoadingReminders] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    reminder_type: 'visa_appointment',
    target_date: '',
    target_time: '',
    priority: 'medium',
    notes: '',
    custom_intervals: '' // comma-separated values
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<{
    success: boolean
    message: string
  } | null>(null)
  const router = useRouter()

  const reminderTypes = [
    { value: 'visa_appointment', label: 'Visa Appointment', icon: Calendar, color: 'text-blue-600' },
    { value: 'visa_expiry', label: 'Visa Expiry', icon: AlertTriangle, color: 'text-red-600' },
    { value: 'document_deadline', label: 'Document Deadline', icon: FileText, color: 'text-orange-600' },
    { value: 'consultation', label: 'Consultation', icon: MessageSquare, color: 'text-green-600' },
    { value: 'document_review', label: 'Document Review', icon: UserCheck, color: 'text-purple-600' },
    { value: 'application_submission', label: 'Application Submission', icon: Briefcase, color: 'text-indigo-600' },
    { value: 'interview_prep', label: 'Interview Preparation', icon: User, color: 'text-pink-600' }
  ]

  const priorityLevels = [
    { value: 'low', label: 'Low', color: 'text-green-600' },
    { value: 'medium', label: 'Medium', color: 'text-yellow-600' },
    { value: 'high', label: 'High', color: 'text-orange-600' },
    { value: 'urgent', label: 'Urgent', color: 'text-red-600' }
  ]

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      setIsAuthenticated(true)
      loadReminders()
    } else {
      router.push('/login')
    }
    setLoading(false)
  }, [router])

  const loadReminders = async () => {
    setLoadingReminders(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/reminders/list/', {
        headers: {
          'Authorization': `Token ${token}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        setReminders(data.reminders || [])
      }
    } catch (error) {
      console.error('Failed to load reminders:', error)
    } finally {
      setLoadingReminders(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title || !formData.target_date || !formData.target_time) {
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
      const target_date = new Date(`${formData.target_date}T${formData.target_time}`).toISOString()
      
      const requestData: any = {
        title: formData.title,
        description: formData.description,
        reminder_type: formData.reminder_type,
        target_date: target_date,
        priority: formData.priority,
        notes: formData.notes
      }

      // Add custom intervals if provided
      if (formData.custom_intervals.trim()) {
        const intervals = formData.custom_intervals
          .split(',')
          .map(i => parseInt(i.trim()))
          .filter(i => !isNaN(i) && i > 0)
        
        if (intervals.length > 0) {
          requestData.custom_intervals = intervals
        }
      }
      
      const token = localStorage.getItem('token')
      const response = await fetch('http://localhost:8000/api/reminders/create/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify(requestData),
      })

      const data = await response.json()

      if (response.ok) {
        setResult({
          success: true,
          message: `Successfully created ${data.reminders_created} reminder(s)! You'll receive notifications before your important date.`
        })
        // Reset form
        setFormData({
          title: '',
          description: '',
          reminder_type: 'visa_appointment',
          target_date: '',
          target_time: '',
          priority: 'medium',
          notes: '',
          custom_intervals: ''
        })
        // Reload reminders list
        loadReminders()
      } else {
        setResult({
          success: false,
          message: data.error || 'Failed to create reminder. Please try again.'
        })
      }
    } catch (error) {
      console.error('Reminder creation error:', error)
      setResult({
        success: false,
        message: 'Failed to create reminder. Please check your connection and try again.'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateReminderStatus = async (reminderId: number, status: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`http://localhost:8000/api/reminders/${reminderId}/status/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ status }),
      })

      if (response.ok) {
        // Reload reminders to show updated status
        loadReminders()
      }
    } catch (error) {
      console.error('Failed to update reminder status:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'sent': return 'text-green-600 bg-green-50 border-green-200'
      case 'completed': return 'text-gray-600 bg-gray-50 border-gray-200'
      case 'cancelled': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    const priorityConfig = priorityLevels.find(p => p.value === priority)
    return priorityConfig?.color || 'text-gray-600'
  }

  const getReminderTypeIcon = (type: string) => {
    const typeConfig = reminderTypes.find(t => t.value === type)
    return typeConfig?.icon || Bell
  }

  const getReminderTypeColor = (type: string) => {
    const typeConfig = reminderTypes.find(t => t.value === type)
    return typeConfig?.color || 'text-gray-600'
  }

  const getDefaultIntervals = (type: string) => {
    const defaults: { [key: string]: number[] } = {
      'visa_appointment': [7, 1],
      'visa_expiry': [30, 7, 1],
      'document_deadline': [7, 3, 1],
      'consultation': [3, 1],
      'document_review': [2, 1],
      'application_submission': [7, 3, 1],
      'interview_prep': [7, 1]
    }
    return defaults[type] || [1]
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
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Reminders & Notifications</h1>
        <p className="text-gray-600 mt-2">
          Never miss important visa appointments, deadlines, or expiry dates. Set up smart reminders that will notify you via email.
        </p>
      </div>

      {/* Dashboard Stats */}
      {!loadingReminders && (
        <ReminderDashboard reminders={reminders} />
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setActiveTab('list')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'list'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <List className="w-4 h-4 inline mr-2" />
          My Reminders
        </button>
        <button
          onClick={() => setActiveTab('create')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'create'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Plus className="w-4 h-4 inline mr-2" />
          Create New
        </button>
      </div>

      {/* Reminders List Tab */}
      {activeTab === 'list' && (
        <div className="space-y-4">
          {loadingReminders ? (
            <Card>
              <CardContent className="flex items-center justify-center py-8">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
                  <p>Loading reminders...</p>
                </div>
              </CardContent>
            </Card>
          ) : reminders.length === 0 ? (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center">
                  <Bell className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No reminders yet</h3>
                  <p className="text-gray-600 mb-4">
                    Create your first reminder to get started with automated notifications.
                  </p>
                  <Button onClick={() => setActiveTab('create')}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create First Reminder
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-4">
              {reminders.map((reminder) => {
                const IconComponent = getReminderTypeIcon(reminder.reminder_type)
                const isOverdue = new Date(reminder.target_date) < new Date() && reminder.status === 'active'
                
                return (
                  <Card key={reminder.id} className={`${isOverdue ? 'border-red-200 bg-red-50/50' : ''}`}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className={`p-2 rounded-lg ${isOverdue ? 'bg-red-100' : 'bg-gray-100'}`}>
                            <IconComponent className={`h-5 w-5 ${getReminderTypeColor(reminder.reminder_type)}`} />
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {reminder.title}
                            </h3>
                            
                            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-2">
                              <span className="capitalize">
                                {reminder.reminder_type.replace('_', ' ')}
                              </span>
                              <span className={`font-medium ${getPriorityColor(reminder.priority)}`}>
                                {reminder.priority.toUpperCase()} Priority
                              </span>
                            </div>
                            
                            {reminder.description && (
                              <p className="text-gray-600 mb-3 text-sm">{reminder.description}</p>
                            )}
                            
                            <div className="flex items-center space-x-6 text-sm">
                              <div className="flex items-center space-x-1">
                                <Calendar className="h-4 w-4 text-gray-400" />
                                <span className={isOverdue ? 'text-red-600 font-medium' : 'text-gray-600'}>
                                  {formatDate(reminder.target_date)}
                                  {isOverdue && ' (Overdue)'}
                                </span>
                              </div>
                              
                              <div className="flex items-center space-x-1">
                                <Bell className="h-4 w-4 text-gray-400" />
                                <span className="text-gray-600">
                                  Next reminder: {formatDate(reminder.reminder_date)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(reminder.status)}`}>
                            {reminder.status.charAt(0).toUpperCase() + reminder.status.slice(1)}
                          </span>
                          
                          {reminder.status === 'active' && (
                            <div className="flex space-x-1">
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => updateReminderStatus(reminder.id, 'completed')}
                                className="text-xs"
                              >
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Complete
                              </Button>
                              <Button 
                                size="sm" 
                                variant="outline"
                                onClick={() => updateReminderStatus(reminder.id, 'cancelled')}
                                className="text-xs text-red-600 hover:text-red-700"
                              >
                                <Trash2 className="h-3 w-3 mr-1" />
                                Cancel
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Create Reminder Tab */}
      {activeTab === 'create' && (
        <Card>
          <CardHeader>
            <CardTitle>Create New Reminder</CardTitle>
            <CardDescription>
              Set up intelligent reminders for visa appointments, document deadlines, and important dates.
              Our system will automatically send you email notifications at optimal times.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label htmlFor="title" className="text-sm font-medium">
                    Reminder Title *
                  </label>
                  <Input
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g., UK Visa Appointment at Embassy"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="reminder_type" className="text-sm font-medium">
                    Reminder Type *
                  </label>
                  <select
                    id="reminder_type"
                    name="reminder_type"
                    value={formData.reminder_type}
                    onChange={handleInputChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    required
                  >
                    {reminderTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  <p className="text-xs text-gray-500">
                    Default reminders: {getDefaultIntervals(formData.reminder_type).join(', ')} days before
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="description" className="text-sm font-medium">
                  Description
                </label>
                <Textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Add any specific details, requirements, or notes..."
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <label htmlFor="target_date" className="text-sm font-medium">
                    Target Date *
                  </label>
                  <Input
                    id="target_date"
                    name="target_date"
                    type="date"
                    value={formData.target_date}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split('T')[0]}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <label htmlFor="target_time" className="text-sm font-medium">
                    Target Time *
                  </label>
                  <Input
                    id="target_time"
                    name="target_time"
                    type="time"
                    value={formData.target_time}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="priority" className="text-sm font-medium">
                    Priority Level
                  </label>
                  <select
                    id="priority"
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    {priorityLevels.map((priority) => (
                      <option key={priority.value} value={priority.value}>
                        {priority.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="custom_intervals" className="text-sm font-medium">
                  Custom Reminder Schedule (Optional)
                </label>
                <Input
                  id="custom_intervals"
                  name="custom_intervals"
                  value={formData.custom_intervals}
                  onChange={handleInputChange}
                  placeholder="e.g., 14,7,3,1 (days before target date)"
                />
                <p className="text-xs text-gray-500">
                  Leave empty to use default schedule, or enter comma-separated days (e.g., "30,7,1" for 30 days, 7 days, and 1 day before)
                </p>
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
                  placeholder="Any additional information or instructions..."
                  rows={2}
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
                <Bell className="mr-2 h-4 w-4" />
                {isSubmitting ? 'Creating Reminders...' : 'Create Smart Reminders'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 