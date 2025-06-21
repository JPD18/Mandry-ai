'use client'

import AuthGuard from '@/components/assistant/AuthGuard'
import AskForm from '@/components/assistant/AskForm'

export default function Dashboard() {
  return (
    <AuthGuard>
      {({ username }) => (
        <>
          <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
            <section className="w-full max-w-4xl mx-auto space-y-8 px-4 sm:px-6 lg:px-8 pt-8">
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