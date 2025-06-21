"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { motion } from "framer-motion"
import { Navbar } from "@/components/Navbar"
import { MandryStarIcon } from "@/components/mandry-icon"
import { Upload, Send, User, FileText } from "lucide-react"
import { ChatInput } from "@/components/ui/chat-input"
import { Button } from "@/components/ui/button"
import { ChatAuthGuard } from "@/components/chat-auth-guard"
import { MarkdownRenderer } from "@/components/ui/markdown-renderer"
import { CitationList } from "@/components/ui/citation"
import { ProfileDropdown } from "@/components/ui/profile-dropdown"
import { MandryLoadingSpinner } from "@/components/ui/icons/MandryLoadingSpinner"
import { TypingIndicator } from "@/components/ui/typing-indicator"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  citations?: Array<{
    title: string
    url: string
    snippet: string
  }>
}

interface SessionState {
  current_step: string;
  message_history: Message[];
  last_question?: string;
}

interface ProcessedDocument {
  id: string
  name: string
  size: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  isValid?: boolean
  reason?: string
  metadata?: {
    file_type: string
    document_type: string
    text_length: number
    activity_log_id: number
  }
  error?: string
}

function ChatPageContent() {
  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState<Message[]>([])
  const [completionPercentage, setCompletionPercentage] = useState(75)
  const [processedDocuments, setProcessedDocuments] = useState<ProcessedDocument[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showTypingIndicator, setShowTypingIndicator] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const conversationStarted = useRef(false);
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [refreshProfileTrigger, setRefreshProfileTrigger] = useState(0);
  const [rightSidebarView, setRightSidebarView] = useState<'upload' | 'profile'>('upload');

  const handleTypingComplete = () => {
    setShowTypingIndicator(false);
    conversationStarted.current = true;
    const welcomeMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: "Hello! I'm your AI assistant. I'm here to help you navigate through any challenge. How can I assist you today?",
    };
    setMessages((prev) => [...prev, welcomeMessage]);
  };

  const startConversation = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("token");
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      
      const response = await fetch(`${apiBase}/api/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${token}`,
        },
        body: JSON.stringify({ message: "start", session_state: null }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.response,
          citations: data.citations || [],
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setSessionState(data.session_state);
        if (data.context_sufficient || data.current_step === "intelligent_qna") {
          setRefreshProfileTrigger(prev => prev + 1);
        }
      } else {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "I'm sorry, I couldn't process your request. Please try again or check your authentication.",
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("Error starting conversation:", error);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm sorry, there was an error connecting to the server. Please check your internet connection and try again.",
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    const messageToSend = message;
    if (messageToSend.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: "user",
        content: messageToSend,
      }
      setMessages((prev) => [...prev, userMessage])
      setMessage("")
      setIsLoading(true)

      try {
        const token = localStorage.getItem("token")
        const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
        
        const response = await fetch(`${apiBase}/api/chat/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Token ${token}`,
          },
          body: JSON.stringify({ message: messageToSend, session_state: sessionState }),
        })

        if (response.ok) {
          const data = await response.json()
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: data.response,
            citations: data.citations || [],
          }
          setMessages((prev) => [...prev, assistantMessage])
          setSessionState(data.session_state);
          // If context is now sufficient, trigger a profile refresh
          if (data.context_sufficient || data.current_step === "intelligent_qna") {
            setRefreshProfileTrigger(prev => prev + 1);
          }
        } else {
          // Handle error response
          const assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: "assistant",
            content: "I'm sorry, I couldn't process your request. Please try again or check your authentication.",
          }
          setMessages((prev) => [...prev, assistantMessage])
        }
      } catch (error) {
        console.error("Error sending message:", error)
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "I'm sorry, there was an error connecting to the server. Please check your internet connection and try again.",
        }
        setMessages((prev) => [...prev, assistantMessage])
      } finally {
        setIsLoading(false)
      }
    }
  }

  useEffect(() => {
    // Start the conversation when the component mounts, but only once.
    // Don't start if typing indicator is active
    if (!conversationStarted.current && !showTypingIndicator) {
      startConversation();
      conversationStarted.current = true;
    }
  }, [showTypingIndicator]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      const newFiles = Array.from(files)

      // Upload files to backend
      for (const file of newFiles) {
        await processDocument(file)
      }
    }
  }

  const processDocument = async (file: File) => {
    const docId = Date.now().toString()
    
    // Add document with uploading status
    setProcessedDocuments(prev => [...prev, {
      id: docId,
      name: file.name,
      size: file.size,
      status: 'uploading' as const,
    }])

    try {
      const token = localStorage.getItem("token")
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"
      
      const formData = new FormData()
      formData.append("file", file)
      formData.append("document_type", "document")

      // Update to processing status
      setProcessedDocuments(prev => prev.map(doc => 
        doc.id === docId ? { ...doc, status: 'processing' as const } : doc
      ))

      const response = await fetch(`${apiBase}/api/process-document/`, {
        method: "POST",
        headers: {
          Authorization: `Token ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        
        // Update with completed status and results
        setProcessedDocuments(prev => prev.map(doc => 
          doc.id === docId ? { 
            ...doc, 
            status: 'completed' as const,
            isValid: data.is_valid,
            reason: data.reason,
            metadata: data.metadata
          } : doc
        ))
        
        console.log("Document processed successfully:", data)
      } else {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        
        // Update with error status
        setProcessedDocuments(prev => prev.map(doc => 
          doc.id === docId ? { 
            ...doc, 
            status: 'error' as const,
            error: errorData.error || 'Processing failed'
          } : doc
        ))
        
        console.error("Failed to process document:", file.name, errorData)
      }
    } catch (error) {
      // Update with error status
      setProcessedDocuments(prev => prev.map(doc => 
        doc.id === docId ? { 
          ...doc, 
          status: 'error' as const,
          error: error instanceof Error ? error.message : 'Network error'
        } : doc
      ))
      
      console.error("Error processing document:", error)
    }
  }

  const handleUploadClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Font loading */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');

        .misto-font {
          font-family: 'Misto', sans-serif;
        }
      `}</style>

      {/* Navbar */}
      <Navbar
        onLogoClick={() => console.log("Logo clicked")}
        onChatClick={() => console.log("Chat clicked")}
        onAboutUsClick={() => console.log("About Us clicked")}
        onScheduleClick={() => console.log("Schedule clicked")}
        onLoginClick={() => console.log("Login clicked")}
        onSignUpClick={() => console.log("Sign up clicked")}
        showAboutUs={true}
        showChat={true}
        showSchedule={true}
      />

      <div className="pt-20 h-full flex flex-col">
        {/* Top Bar with Assistant Info and Completion */}
        
            

        {/* Main Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 p-6 overflow-y-auto">
              {messages.length === 0 ? (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6 }}
                  className="flex items-center justify-center h-full"
                >
                  <div className="text-center bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-12 max-w-md">
                    <MandryStarIcon size={80} className="mx-auto mb-6" />
                    <h3 className="text-2xl font-bold text-white mb-4 misto-font">Welcome to Mandry</h3>
                    <p className="text-gray-300">
                      Start a conversation with your AI assistant to navigate through any challenge
                    </p>
                  </div>
                </motion.div>
              ) : (
                <div className="space-y-6 max-w-4xl mx-auto">
                  {messages.map((msg, index) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1, duration: 0.4 }}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      {msg.role === "assistant" && (
                        <div
                          className="w-8 h-8 rounded-full mr-3 mt-1 flex-shrink-0 border"
                          style={{
                            backgroundColor: "#31B8E9",
                            opacity: 0.4,
                            backdropFilter: "blur(12px)",
                            borderColor: "rgba(49, 184, 233, 0.2)",
                            boxShadow:
                              "inset 0 0 15px rgba(255, 255, 255, 0.3), inset 0 0 30px rgba(255, 255, 255, 0.1)",
                          }}
                        ></div>
                      )}
                      <div
                        className={`max-w-full sm:max-w-md px-6 py-4 rounded-2xl backdrop-blur-sm border break-words whitespace-pre-wrap ${
                          msg.role === "user"
                            ? "bg-gradient-to-r from-[#FFF309]/20 to-[#FFF309]/10 text-white border-[#FFF309]/30"
                            : "bg-white/10 text-white border-white/20"
                        }`}
                      >
                        {msg.role === "assistant" ? (
                          <>
                            <MarkdownRenderer content={msg.content} citations={msg.citations} />
                            {msg.citations && msg.citations.length > 0 && (
                              <CitationList citations={msg.citations} />
                            )}
                          </>
                        ) : (
                          msg.content
                        )}
                      </div>
                    </motion.div>
                  ))}
                  
                  {/* Loading indicator */}
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="flex justify-start"
                    >
                      <div className="w-8 h-8 rounded-full mr-3 mt-1 flex-shrink-0 border"
                         style={{
                          backgroundColor: "#31B8E9",
                          opacity: 0.4,
                          backdropFilter: "blur(12px)",
                          borderColor: "rgba(49, 184, 233, 0.2)",
                          boxShadow:
                            "inset 0 0 15px rgba(255, 255, 255, 0.3), inset 0 0 30px rgba(255, 255, 255, 0.1)",
                        }}
                      ></div>
                      <div className="relative bg-white/10 border-white/20 px-6 rounded-2xl backdrop-blur-sm border h-10 flex items-center justify-center">
                        <MandryLoadingSpinner className="w-12 h-12" />
                      </div>
                    </motion.div>
                  )}

                  {/* Typing indicator */}
                  {showTypingIndicator && !isLoading && (
                    <TypingIndicator onTypingComplete={handleTypingComplete} />
                  )}
                </div>
              )}
            </div>

            {/* Input Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="p-6 backdrop-blur-sm border-t border-white/10"
            >
              <div className="flex space-x-4 max-w-4xl mx-auto">
                <ChatInput
                  value={message}
                  onChange={(e) => {
                    setMessage(e.target.value);
                    // Hide typing indicator when user starts typing
                    if (e.target.value.trim() !== '') {
                      setShowTypingIndicator(false);
                    }
                  }}
                  placeholder="Ask Mandry"
                  className="flex-1 backdrop-blur-sm border-white/20 rounded-xl px-6 py-4 focus:border-[#FFF309]/50 focus:ring-[#FFF309]/20 text-white placeholder:text-gray-300"
                  style={{ background: 'transparent' }}
                  onClick={() => {
                    if (messages.length === 0 && !conversationStarted.current) {
                      setShowTypingIndicator(true);
                    }
                  }}
                  onFocus={() => {
                    if (messages.length === 0 && !conversationStarted.current) {
                      setShowTypingIndicator(true);
                    }
                  }}
                  onBlur={() => {
                    // Only hide if user hasn't started typing
                    if (message.trim() === '') {
                      setShowTypingIndicator(false);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      setShowTypingIndicator(false);
                      handleSendMessage();
                    }
                  }}
                  disabled={isLoading}
                />
                <Button
                  onClick={() => {
                    setShowTypingIndicator(false);
                    handleSendMessage();
                  }}
                  disabled={isLoading}
                  className="px-4 py-4 bg-gradient-to-r from-[#FFF309] to-[#FFF309]/80 hover:from-[#FFF309]/90 hover:to-[#FFF309]/70 font-semibold rounded-xl transition-all duration-200 shadow-lg hover:shadow-[#FFF309]/25 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5 text-white" />
                </Button>
              </div>
            </motion.div>
          </div>

          {/* Right Sidebar - Document Upload & Profile */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="w-80 bg-transparent backdrop-blur-sm border-l border-white/10 flex flex-col"
          >
            <div className="p-4 border-b border-white/10">
              <div className="flex items-center justify-center gap-2">
                <Button
                  size="sm"
                  variant={rightSidebarView === 'upload' ? 'secondary' : 'ghost'}
                  onClick={() => setRightSidebarView('upload')}
                  className="w-full"
                >
                  <FileText className="h-4 w-4 mr-2"/>
                  Upload
                </Button>
                <Button
                  size="sm"
                  variant={rightSidebarView === 'profile' ? 'secondary' : 'ghost'}
                  onClick={() => setRightSidebarView('profile')}
                  className="w-full"
                >
                  <User className="h-4 w-4 mr-2"/>
                  Profile
                </Button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto flex-1">
              {rightSidebarView === 'upload' && (
                <>
                  <div className="mb-6">
                    <h3 className="font-semibold text-white mb-3 misto-font">Upload Documents</h3>
                    <p className="text-sm text-gray-300 leading-relaxed">Supported formats: PDF, PNG, JPG (max 10MB)</p>
                  </div>

                  {/* Upload Area */}
                  <div className="mb-4">
                    <div className="bg-transparent backdrop-blur-sm border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-[#FFF309]/50 transition-colors duration-200">
                      <Upload className="w-8 h-8 text-[#FFF309] mx-auto mb-3" />
                      <p className="text-sm text-gray-300 mb-4">
                        Drag and drop your file here or click the button below to select a file
                      </p>
                    </div>
                    <div className="flex justify-center">
                      <Button
                        size="sm"
                        onClick={handleUploadClick}
                        className="w-full mt-3 bg-[#FFF309]/20 hover:bg-[#FFF309] hover:text-slate-900 text-[#FFF309] border-none font-medium rounded-lg transition-all duration-200"
                      >
                        Select File
                      </Button>
                    </div>
                    <input
                      ref={fileInputRef}
                      type="file"
                      multiple
                      onChange={handleFileUpload}
                      className="hidden"
                      accept=".pdf,.png,.jpg,.jpeg"
                    />
                  </div>

                  {/* Uploaded Files List */}
                  {processedDocuments.length > 0 && (
                    <div className="space-y-3 mb-6">
                      <h4 className="font-medium text-gray-300 text-sm">Document Processing:</h4>
                      <div className="space-y-2">
                        {processedDocuments.map((doc, index) => (
                          <motion.div
                            key={doc.id}
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: index * 0.1, duration: 0.3 }}
                            className={`bg-transparent backdrop-blur-sm p-3 rounded-lg border ${
                              doc.status === 'completed' && doc.isValid 
                                ? 'border-green-400/50' 
                                : doc.status === 'error' || (doc.status === 'completed' && !doc.isValid)
                                ? 'border-red-400/50'
                                : 'border-white/20'
                            }`}
                          >
                            <div className="font-medium text-white text-sm truncate">{doc.name}</div>
                            <div className="text-gray-400 text-xs">{(doc.size / 1024).toFixed(1)} KB</div>
                            
                            {/* Status indicator */}
                            <div className="flex items-center gap-2 mt-2">
                              {doc.status === 'uploading' && (
                                <>
                                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                                  <span className="text-xs text-blue-300">Uploading...</span>
                                </>
                              )}
                              {doc.status === 'processing' && (
                                <>
                                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-spin"></div>
                                  <span className="text-xs text-yellow-300">Processing...</span>
                                </>
                              )}
                              {doc.status === 'completed' && doc.isValid && (
                                <>
                                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                  <span className="text-xs text-green-300">Valid Document</span>
                                </>
                              )}
                              {doc.status === 'completed' && !doc.isValid && (
                                <>
                                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                                  <span className="text-xs text-red-300">Invalid Document</span>
                                </>
                              )}
                              {doc.status === 'error' && (
                                <>
                                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                                  <span className="text-xs text-red-300">Error</span>
                                </>
                              )}
                            </div>
                            
                            {/* Validation reason or error */}
                            {doc.reason && (
                              <div className="text-xs text-gray-400 mt-1 italic">
                                {doc.reason}
                              </div>
                            )}
                            {doc.error && (
                              <div className="text-xs text-red-400 mt-1 italic">
                                {doc.error}
                              </div>
                            )}
                            
                            {/* Metadata */}
                            {doc.metadata && (
                              <div className="text-xs text-gray-500 mt-1">
                                {doc.metadata.text_length} characters extracted
                              </div>
                            )}
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}

                  
                </>
              )}

              {rightSidebarView === 'profile' && (
                <ProfileDropdown 
                  isExpanded={true}
                  onToggle={() => {}} // No-op as we control view from outside
                  refreshTrigger={refreshProfileTrigger}
                />
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

export default function ChatPage() {
  return (
    <ChatAuthGuard>
      <ChatPageContent />
    </ChatAuthGuard>
  )
} 