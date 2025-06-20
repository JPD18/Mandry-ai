'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react'

export default function UploadPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{
    success: boolean
    message: string
    fileId?: number
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

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    // Check file type
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']
    if (!allowedTypes.includes(file.type)) {
      setUploadResult({
        success: false,
        message: 'Only PDF, PNG, and JPG files are allowed.'
      })
      return
    }

    // Check file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setUploadResult({
        success: false,
        message: 'File size must be less than 10MB.'
      })
      return
    }

    setUploading(true)
    setUploadResult(null)

    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
        },
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        setUploadResult({
          success: true,
          message: `File uploaded successfully! File ID: ${data.file_id}`,
          fileId: data.file_id
        })
      } else {
        setUploadResult({
          success: false,
          message: data.error || 'Upload failed. Please try again.'
        })
      }
    } catch (error) {
      console.error('Upload error:', error)
      setUploadResult({
        success: false,
        message: 'Upload failed. Please check your connection and try again.'
      })
    } finally {
      setUploading(false)
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
          <CardTitle>Upload Documents</CardTitle>
          <CardDescription>
            Upload visa documents, passports, or other immigration-related files for analysis.
            Supported formats: PDF, PNG, JPG (max 10MB)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragOver
                ? 'border-primary bg-primary/10'
                : 'border-muted-foreground/25 hover:border-muted-foreground/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <div className="space-y-2">
              <p className="text-lg font-medium">
                {dragOver ? 'Drop your file here' : 'Drag and drop your file here'}
              </p>
              <p className="text-sm text-muted-foreground">
                or click the button below to select a file
              </p>
            </div>
          </div>

          <div className="flex justify-center">
            <Button
              onClick={() => document.getElementById('file-input')?.click()}
              disabled={uploading}
              variant="outline"
            >
              <FileText className="mr-2 h-4 w-4" />
              {uploading ? 'Uploading...' : 'Select File'}
            </Button>
            <input
              id="file-input"
              type="file"
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {uploadResult && (
            <div
              className={`flex items-center space-x-2 p-4 rounded-lg ${
                uploadResult.success
                  ? 'bg-green-50 text-green-700 border border-green-200'
                  : 'bg-red-50 text-red-700 border border-red-200'
              }`}
            >
              {uploadResult.success ? (
                <CheckCircle className="h-5 w-5" />
              ) : (
                <AlertCircle className="h-5 w-5" />
              )}
              <p className="text-sm">{uploadResult.message}</p>
            </div>
          )}

          <div className="text-sm text-muted-foreground space-y-2">
            <p className="font-medium">Accepted file types:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>PDF documents (.pdf)</li>
              <li>PNG images (.png)</li>
              <li>JPEG images (.jpg, .jpeg)</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
} 