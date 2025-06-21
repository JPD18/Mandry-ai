import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { ExternalLink, FileText } from 'lucide-react'

interface Citation {
  title: string
  url: string
  snippet: string
}

interface CitationProps {
  citations: Citation[]
  ragVerified?: boolean
}

export function CitationList({ citations, ragVerified = true }: CitationProps) {
  if (!citations || citations.length === 0) {
    return null
  }

  return (
    <div className="mt-6 space-y-4">
      <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
        <FileText className="h-4 w-4" />
        <span>Sources</span>
        {ragVerified && (
          <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
            Verified
          </span>
        )}
      </div>
      
      <div className="space-y-3">
        {citations.map((citation, index) => (
          <Card key={index} className="border-l-4 border-l-blue-500">
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {citation.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                    {citation.snippet}
                  </p>
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    View Source
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
                <div className="flex-shrink-0 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  [{index + 1}]
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export function CitationReference({ sourceNumber }: { sourceNumber: number }) {
  return (
    <sup className="text-blue-600 hover:text-blue-800 cursor-pointer font-medium">
      [{sourceNumber}]
    </sup>
  )
} 