"use client"

import React from "react"
import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Calendar, Clock, Bell, Plus, AlertCircle, CheckCircle2, ArrowLeft, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Navbar } from "@/components/Navbar"
import { useRouter } from "next/navigation"
import { ChatAuthGuard } from "@/components/chat-auth-guard"

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

const reminderTypes = [
  { value: "visa_appointment", label: "Visa Appointment", icon: Calendar },
  { value: "visa_expiry", label: "Visa Expiry", icon: AlertCircle },
  { value: "document_deadline", label: "Document Deadline", icon: Clock },
  { value: "consultation", label: "Consultation", icon: Bell },
  { value: "document_review", label: "Document Review", icon: CheckCircle2 },
  { value: "application_submission", label: "Application Submission", icon: Plus },
  { value: "interview_prep", label: "Interview Preparation", icon: Calendar },
]

const priorityLevels = [
  { value: "low", label: "Low", colour: "bg-green-500" },
  { value: "medium", label: "Medium", colour: "bg-yellow-500" },
  { value: "high", label: "High", colour: "bg-orange-500" },
  { value: "urgent", label: "Urgent", colour: "bg-red-500" },
]

export default function SchedulingPage() {
  const [currentView, setCurrentView] = useState<"menu" | "create" | "manage">("menu")
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [loadingReminders, setLoadingReminders] = useState(false)
  const [formData, setFormData] = useState({
    title: "",
    reminderType: "",
    targetDate: "",
    targetTime: "",
    priority: "medium",
    description: "",
    notes: "",
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
      loadReminders()
    }
    // Auth is handled by ChatAuthGuard now
  }, [])

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

  const handleInputChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.title || !formData.targetDate || !formData.targetTime) {
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
      const target_date = new Date(`${formData.targetDate}T${formData.targetTime}`).toISOString()
      
      const requestData: any = {
        title: formData.title,
        description: formData.description,
        reminder_type: formData.reminderType,
        target_date: target_date,
        priority: formData.priority,
        notes: formData.notes
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
          title: "",
          reminderType: "",
          targetDate: "",
          targetTime: "",
          priority: "medium",
          description: "",
          notes: "",
        })
        // Reload reminders list
        loadReminders()
        // Switch to manage view
        setCurrentView("manage")
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
      const response = await fetch(`http://localhost:8000/api/reminders/${reminderId}/update_status/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({ status }),
      })

      if (response.ok) {
        loadReminders()
      }
    } catch (error) {
      console.error('Failed to update reminder status:', error)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getPriorityColour = (priority: string) => {
    const priorityObj = priorityLevels.find((p) => p.value === priority)
    return priorityObj?.colour || "bg-grey-500"
  }

  const getReminderIcon = (type: string) => {
    const icon = reminderTypes.find(t => t.value === type)?.icon
    return icon ? icon : Bell
  }
  
  const StatCard = ({ title, value, icon, description, badge, color }: { title: string, value: number, icon: React.ElementType, description: string, badge?: string, color: string }) => {
    const IconComponent = icon
    return (
      <Card className="relative hover:shadow-lg transition-shadow duration-300">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className="flex items-center space-x-2">
            {badge && value > 0 && <Badge variant={badge as any} className="text-xs">{value}</Badge>}
            <IconComponent className={`h-4 w-4 ${color}`} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        </CardContent>
      </Card>
    )
  }

  // Service Menu View
  if (currentView === "menu") {
    return (
      <ChatAuthGuard>
        <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
          {/* Font loading */}
          <style jsx global>{`
            @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
            
            .misto-font {
              font-family: 'Misto', sans-serif;
            }
          `}</style>

          <Navbar />
          <div className="pt-20 h-full flex flex-col">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="flex-1 flex items-center justify-center px-6"
            >
              <div className="max-w-7xl mx-auto">
                {/* Service Header */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.6 }}
                  className="text-center mb-12"
                >
                  <h1 className="text-5xl font-bold text-white mb-4 misto-font">
                    Choose a service to get started
                  </h1>
                </motion.div>

                {/* Service Options */}
                <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                  {/* Create Reminder Service */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.2 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      className="bg-white/5 backdrop-blur-sm border border-white/20 cursor-pointer hover:bg-white/10 transition-all duration-300 h-full"
                      onClick={() => setCurrentView("create")}
                    >
                      <CardContent className="p-8 text-center">
                        <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-6">
                          <Plus className="w-8 h-8 text-white/80" />
                        </div>
                        <h3 className="text-2xl font-semibold text-white mb-4 misto-font">
                          Create Reminder
                        </h3>
                        <p className="text-gray-300 mb-6">
                          Set up new automated reminders for your important visa-related dates and deadlines
                        </p>
                        <div className="flex flex-wrap gap-2 justify-center">
                          <Badge variant="secondary" className="bg-sky-500/20 text-sky-300">
                            Appointments
                          </Badge>
                          <Badge variant="secondary" className="bg-red-500/20 text-red-300">
                            Deadlines
                          </Badge>
                          <Badge variant="secondary" className="bg-violet-500/20 text-violet-300">
                            Consultations
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>

                  {/* Manage Reminders Service */}
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      className="bg-white/5 backdrop-blur-sm border border-white/20 cursor-pointer hover:bg-white/10 transition-all duration-300 h-full"
                      onClick={() => setCurrentView("manage")}
                    >
                      <CardContent className="p-8 text-center">
                        <div className="w-16 h-16 bg-gradient-to-r from-yellow-400 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-6">
                          <Users className="w-8 h-8 text-white/80" />
                        </div>
                        <h3 className="text-2xl font-semibold text-white mb-4 misto-font">
                          Manage Reminders
                        </h3>
                        <p className="text-gray-300 mb-6">
                          View, edit, and organise your existing reminders. Track status and update details
                        </p>
                        <div className="flex flex-wrap gap-2 justify-center">
                          <Badge variant="secondary" className="bg-yellow-500/20 text-yellow-300">
                            Active: {reminders.filter(r => r.status === 'active').length}
                          </Badge>
                          <Badge variant="secondary" className="bg-green-500/20 text-green-300">
                            Completed: {reminders.filter(r => r.status === 'completed').length}
                          </Badge>
                          <Badge variant="secondary" className="bg-red-500/20 text-red-300">
                            Urgent: {reminders.filter(r => r.priority === 'urgent').length}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </ChatAuthGuard>
    )
  }

  // Create Reminder View
  if (currentView === "create") {
    return (
      <ChatAuthGuard>
        <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
          {/* Font loading */}
          <style jsx global>{`
            @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
            
            .misto-font {
              font-family: 'Misto', sans-serif;
            }
          `}</style>

          <div className="relative min-h-screen">
            {/* Back Button */}
            <div className="absolute top-6 left-6 z-10">
              <button 
                onClick={() => setCurrentView("menu")}
                className="text-yellow-400 hover:text-yellow-300 transition-all duration-200"
              >
                <ArrowLeft
                  size={24}
                  className="drop-shadow-[0_0_8px_rgba(255,243,9,0.6)] hover:drop-shadow-[0_0_12px_rgba(255,243,9,0.8)]"
                />
              </button>
            </div>

            <div className="pt-20 h-full flex flex-col">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="flex-1 flex items-center justify-center px-6"
              >
                <div className="max-w-4xl mx-auto w-full">
                  {/* Result Message */}
                  {result && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={`mb-6 p-4 rounded-lg ${
                        result.success 
                          ? 'bg-green-500/20 border border-green-500/30 text-green-300' 
                          : 'bg-red-500/20 border border-red-500/30 text-red-300'
                      }`}
                    >
                      {result.message}
                    </motion.div>
                  )}

                  {/* Create Form */}
                  <Card className="bg-white/5 backdrop-blur-sm border border-white/20">
                    <CardHeader>
                      <CardTitle className="text-2xl font-semibold text-white misto-font">
                        Create New Reminder
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Title */}
                          <div className="space-y-2">
                            <Label htmlFor="title" className="text-white">
                              Reminder Title
                            </Label>
                            <Input
                              id="title"
                              value={formData.title}
                              onChange={(e) => handleInputChange("title", e.target.value)}
                              placeholder="e.g., Embassy Interview"
                              className="bg-white/10 border-white/20 text-white placeholder:text-grey-400"
                            />
                          </div>

                          {/* Reminder Type */}
                          <div className="space-y-2">
                            <Label htmlFor="reminderType" className="text-white">
                              Reminder Type
                            </Label>
                            <Select
                              value={formData.reminderType}
                              onValueChange={(value) => handleInputChange("reminderType", value)}
                            >
                              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                                <SelectValue placeholder="Select reminder type" />
                              </SelectTrigger>
                              <SelectContent>
                                {reminderTypes.map((type) => (
                                  <SelectItem key={type.value} value={type.value}>
                                    <div className="flex items-center gap-2">
                                      <type.icon className="w-4 h-4" />
                                      {type.label}
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          {/* Target Date */}
                          <div className="space-y-2">
                            <Label htmlFor="targetDate" className="text-white">
                              Target Date
                            </Label>
                            <Input
                              id="targetDate"
                              type="date"
                              value={formData.targetDate}
                              onChange={(e) => handleInputChange("targetDate", e.target.value)}
                              className="bg-white/10 border-white/20 text-white"
                            />
                          </div>

                          {/* Target Time */}
                          <div className="space-y-2">
                            <Label htmlFor="targetTime" className="text-white">
                              Target Time
                            </Label>
                            <Input
                              id="targetTime"
                              type="time"
                              value={formData.targetTime}
                              onChange={(e) => handleInputChange("targetTime", e.target.value)}
                              className="bg-white/10 border-white/20 text-white"
                            />
                          </div>

                          {/* Priority */}
                          <div className="space-y-2">
                            <Label htmlFor="priority" className="text-white">
                              Priority Level
                            </Label>
                            <Select value={formData.priority} onValueChange={(value) => handleInputChange("priority", value)}>
                              <SelectTrigger className="bg-white/10 border-white/20 text-white">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {priorityLevels.map((priority) => (
                                  <SelectItem key={priority.value} value={priority.value}>
                                    <div className="flex items-center gap-2">
                                      <div className={`w-3 h-3 rounded-full ${priority.colour}`} />
                                      {priority.label}
                                    </div>
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>
                        </div>

                        {/* Description */}
                        <div className="space-y-2">
                          <Label htmlFor="description" className="text-white">
                            Description
                          </Label>
                          <Textarea
                            id="description"
                            value={formData.description}
                            onChange={(e) => handleInputChange("description", e.target.value)}
                            placeholder="Add any additional details about this reminder..."
                            className="bg-white/10 border-white/20 text-white placeholder:text-grey-400"
                            rows={3}
                          />
                        </div>

                        {/* Notes */}
                        <div className="space-y-2">
                          <Label htmlFor="notes" className="text-white">
                            Notes
                          </Label>
                          <Textarea
                            id="notes"
                            value={formData.notes}
                            onChange={(e) => handleInputChange("notes", e.target.value)}
                            placeholder="Any personal notes or preparation items..."
                            className="bg-white/10 border-white/20 text-white placeholder:text-grey-400"
                            rows={2}
                          />
                        </div>

                        {/* Submit Button */}
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <Button
                            type="submit"
                            disabled={isSubmitting}
                            className="w-full px-8 py-3 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-300 hover:to-yellow-400 text-slate-900 font-semibold text-lg disabled:opacity-50"
                          >
                            {isSubmitting ? "Creating..." : "Create Reminder"}
                          </Button>
                        </motion.div>
                      </form>
                    </CardContent>
                  </Card>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </ChatAuthGuard>
    )
  }

  // Manage Reminders View
  return (
    <ChatAuthGuard>
      <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
        {/* Font loading */}
        <style jsx global>{`
          @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
          
          .misto-font {
            font-family: 'Misto', sans-serif;
          }
        `}</style>

        <div className="relative min-h-screen">
          {/* Back Button */}
          <div className="absolute top-6 left-6 z-10">
            <button 
              onClick={() => setCurrentView("menu")}
              className="text-yellow-400 hover:text-yellow-300 transition-all duration-200"
            >
              <ArrowLeft
                size={24}
                className="drop-shadow-[0_0_8px_rgba(255,243,9,0.6)] hover:drop-shadow-[0_0_12px_rgba(255,243,9,0.8)]"
              />
            </button>
          </div>

          <div className="pt-20 h-full flex flex-col">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex-1 px-6 py-8"
            >
              <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                  <h1 className="text-4xl font-bold text-white mb-4 misto-font">
                    Manage Reminders
                  </h1>
                </div>

                {/* Loading State */}
                {loadingReminders && (
                  <div className="text-center py-8">
                    <div className="text-white">Loading reminders...</div>
                  </div>
                )}

                {/* Empty State */}
                {!loadingReminders && reminders.length === 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center py-12"
                  >
                    <div className="bg-white/5 backdrop-blur-sm border border-white/20 rounded-2xl p-8 max-w-md mx-auto">
                      <Bell className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-2xl font-semibold text-white mb-2 misto-font">
                        No reminders yet
                      </h3>
                      <p className="text-gray-300 mb-6">
                        Create your first reminder to get started with automated notifications
                      </p>
                      <Button
                        onClick={() => setCurrentView("create")}
                        className="bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-300 hover:to-yellow-400 text-slate-900 font-semibold"
                      >
                        Create First Reminder
                      </Button>
                    </div>
                  </motion.div>
                )}

                {/* Reminders List */}
                {!loadingReminders && reminders.length > 0 && (
                  <div className="space-y-4">
                    {reminders.map((reminder, index) => (
                      <motion.div
                        key={reminder.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                      >
                        <Card className="bg-white/5 backdrop-blur-sm border border-white/20">
                          <CardContent className="p-6">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="text-xl font-semibold text-white misto-font">
                                    {reminder.title}
                                  </h3>
                                  <Badge className={`${getPriorityColour(reminder.priority)} text-white`}>
                                    {reminder.priority}
                                  </Badge>
                                  <Badge
                                    variant="secondary"
                                    className={
                                      reminder.status === 'completed'
                                        ? 'bg-green-500/20 text-green-300'
                                        : 'bg-yellow-500/20 text-yellow-300'
                                    }
                                  >
                                    {reminder.status}
                                  </Badge>
                                </div>
                                <p className="text-gray-300 mb-2">
                                  {reminderTypes.find((t) => t.value === reminder.reminder_type)?.label}
                                </p>
                                <p className="text-yellow-400 font-semibold">{formatDate(reminder.target_date)}</p>
                                {reminder.description && (
                                  <p className="text-gray-300 mt-2">{reminder.description}</p>
                                )}
                              </div>
                              <div className="flex gap-2">
                                {reminder.status !== "completed" && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => updateReminderStatus(reminder.id, "completed")}
                                    className="bg-green-500/20 border-green-500/30 text-green-300 hover:bg-green-500/30"
                                  >
                                    Complete
                                  </Button>
                                )}
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                                >
                                  Edit
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </ChatAuthGuard>
  )
}