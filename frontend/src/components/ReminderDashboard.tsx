'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  Bell, 
  Calendar, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  TrendingUp
} from 'lucide-react'

interface ReminderStats {
  total: number
  active: number
  completed: number
  overdue: number
  upcoming: number
}

interface ReminderDashboardProps {
  reminders: any[]
}

export function ReminderDashboard({ reminders }: ReminderDashboardProps) {
  const [stats, setStats] = useState<ReminderStats>({
    total: 0,
    active: 0,
    completed: 0,
    overdue: 0,
    upcoming: 0
  })

  useEffect(() => {
    const now = new Date()
    const nextWeek = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

    const calculatedStats = reminders.reduce((acc, reminder) => {
      const targetDate = new Date(reminder.target_date)
      const isOverdue = targetDate < now && reminder.status === 'active'
      const isUpcoming = targetDate > now && targetDate <= nextWeek && reminder.status === 'active'

      return {
        total: acc.total + 1,
        active: reminder.status === 'active' ? acc.active + 1 : acc.active,
        completed: reminder.status === 'completed' ? acc.completed + 1 : acc.completed,
        overdue: isOverdue ? acc.overdue + 1 : acc.overdue,
        upcoming: isUpcoming ? acc.upcoming + 1 : acc.upcoming
      }
    }, {
      total: 0,
      active: 0,
      completed: 0,
      overdue: 0,
      upcoming: 0
    })

    setStats(calculatedStats)
  }, [reminders])

  const statCards = [
    {
      title: 'Total Reminders',
      value: stats.total,
      icon: Bell,
      description: 'All reminders created',
      color: 'text-blue-600'
    },
    {
      title: 'Active',
      value: stats.active,
      icon: Calendar,
      description: 'Currently active reminders',
      color: 'text-green-600'
    },
    {
      title: 'Upcoming',
      value: stats.upcoming,
      icon: Clock,
      description: 'Due in the next 7 days',
      color: 'text-yellow-600',
      badge: stats.upcoming > 0 ? 'warning' : undefined
    },
    {
      title: 'Overdue',
      value: stats.overdue,
      icon: AlertTriangle,
      description: 'Past due date',
      color: 'text-red-600',
      badge: stats.overdue > 0 ? 'danger' : undefined
    },
    {
      title: 'Completed',
      value: stats.completed,
      icon: CheckCircle,
      description: 'Successfully completed',
      color: 'text-gray-600'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      {statCards.map((stat) => {
        const IconComponent = stat.icon
        return (
          <Card key={stat.title} className="relative">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className="flex items-center space-x-2">
                {stat.badge && stat.value > 0 && (
                  <Badge variant={stat.badge as any} className="text-xs">
                    {stat.value}
                  </Badge>
                )}
                <IconComponent className={`h-4 w-4 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.description}
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
} 