"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { StarSpinner } from "@/components/ui/icons/StarSpinner"

export default function AskForm() {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer]   = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    try {
      const token = localStorage.getItem("token")
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
      const response = await fetch(`${apiBase}/api/ask/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      setAnswer(data.answer || "No response received")
    } catch (error) {
      setAnswer("Error: Could not get response from server")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="shadow-lg backdrop-blur-md border-white/20 bg-white/5">
      <CardHeader>
        <CardTitle>Ask a Question</CardTitle>
        <CardDescription>
          Get AI-powered assistance with visas and immigration
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Textarea
            placeholder="Ask me anything about visas..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="min-h-[100px]"
          />

          <Button 
            type="submit" 
            disabled={loading || !question.trim()}
            className="w-full"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <StarSpinner className="w-4 h-4" />
                Getting answer...
              </div>
            ) : (
              "Ask Mandry"
            )}
          </Button>
        </form>

        {answer && (
          <div className="mt-6 rounded-lg bg-gradient-to-r from-yellow-400/10 to-yellow-500/10 p-4 border border-yellow-400/20">
            <h3 className="font-semibold mb-2">Answer:</h3>
            <p className="text-gray-100 whitespace-pre-wrap">{answer}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
