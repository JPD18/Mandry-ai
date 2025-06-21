'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import AuthGuard from '@/components/assistant/AuthGuard'
import AskForm from '@/components/assistant/AskForm'
import { CompassBadge } from '@/components/ui/icons/CompassBadge'

export default function Home() {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    router.push('/login')
  }

  return (
    <AuthGuard>
      {({ username }) => (
        <>
          <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center h-16">
                <CompassBadge />
                <Button 
                  onClick={handleLogout}
                  variant="outline"
                >
                  Logout
                </Button>
              </div>
            </div>
          </header>
          
          <main className="pt-24 min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            <section className="w-full max-w-4xl mx-auto space-y-8 px-4 sm:px-6 lg:px-8">
              <h1 className="text-4xl font-bold text-gray-900 text-center">
                Welcome, {username}
              </h1>
              <AskForm />
            </section>
          </main>
        </>
      )}
    </AuthGuard>
  )
} 