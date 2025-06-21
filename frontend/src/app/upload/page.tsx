'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Upload, FileText, AlertCircle, CheckCircle, Eye, FileCheck, Info } from 'lucide-react'

// Type for document processing results
interface DocumentProcessingResult {
  is_valid: boolean
  reason: string
  metadata: {
    file_type: string
    document_type: string
    text_length: number
    processing_successful: boolean
    activity_log_id: number
  }
  processing_successful: boolean
}

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
  const [processingResult, setProcessingResult] = useState<DocumentProcessingResult | null>(null)
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
    setProcessingResult(null)

    try {
      const token = localStorage.getItem('token')
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', 'document') // You can make this configurable

      // Call the process-document endpoint
      const response = await fetch('http://localhost:8000/api/process-document/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
        },
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        // Document processed successfully
        setUploadResult({
          success: true,
          message: `Document processed successfully!`
        })
        setProcessingResult(data)
      } else {
        setUploadResult({
          success: false,
          message: data.error || 'Document processing failed. Please try again.'
        })
      }
    } catch (error) {
      console.error('Processing error:', error)
      setUploadResult({
        success: false,
        message: 'Document processing failed. Please check your connection and try again.'
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
    <div className="max-w-2xl mx-auto space-y-6">
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
              {uploading ? 'Processing...' : 'Select File'}
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

      {/* Document Processing Results Bar */}
      {processingResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileCheck className="h-5 w-5" />
              <span>Document Processing Results</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Validation Status */}
            <div
              className={`flex items-center space-x-3 p-4 rounded-lg ${
                processingResult.is_valid
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              {processingResult.is_valid ? (
                <CheckCircle className="h-6 w-6 text-green-600" />
              ) : (
                <AlertCircle className="h-6 w-6 text-red-600" />
              )}
              <div className="flex-1">
                <p className="font-semibold">
                  {processingResult.is_valid ? 'Document Valid' : 'Document Invalid'}
                </p>
                <p className="text-sm opacity-90">{processingResult.reason}</p>
              </div>
            </div>

            {/* Document Metadata */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-sm font-medium text-gray-600">File Type</p>
                <p className="text-sm text-gray-900 uppercase">{processingResult.metadata.file_type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Document Type</p>
                <p className="text-sm text-gray-900 capitalize">{processingResult.metadata.document_type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Text Length</p>
                <p className="text-sm text-gray-900">{processingResult.metadata.text_length.toLocaleString()} characters</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600">Processing Status</p>
                <p className="text-sm text-gray-900">
                  {processingResult.metadata.processing_successful ? 'Successful' : 'Failed'}
                </p>
              </div>
            </div>

            {/* Privacy Notice */}
            <div className="flex items-start space-x-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <Info className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-medium">Privacy & Security:</p>
                <p>
                  Your document was processed securely and no files or extracted text are stored on our servers. 
                  Only basic processing metadata is logged for audit purposes (Activity Log ID: {processingResult.metadata.activity_log_id}).
                </p>
              </div>
            </div>

            {/* Processing Summary */}
            <div className="flex items-start space-x-2 p-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div className="text-sm text-green-800">
                <p className="font-medium">Summary:</p>
                <p>
                  Successfully processed {processingResult.metadata.file_type.toUpperCase()} file with{' '}
                  {processingResult.metadata.text_length.toLocaleString()} characters of text.{' '}
                  Document validation: {processingResult.is_valid ? 'PASSED' : 'FAILED'}.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 