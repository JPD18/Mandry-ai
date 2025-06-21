import { motion } from "framer-motion"
import { useState, useEffect } from "react"
import { MandryLoadingSpinner } from "./icons/MandryLoadingSpinner"

interface TypingIndicatorProps {
  className?: string
  onTypingComplete?: () => void
}

export function TypingIndicator({ className, onTypingComplete }: TypingIndicatorProps) {
  const [typedText, setTypedText] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isTyping, setIsTyping] = useState(true)
  
  const welcomeMessage = "Hello! I'm your AI assistant. I'm here to help you navigate through any challenge. How can I assist you today?"
  
  useEffect(() => {
    if (currentIndex < welcomeMessage.length && isTyping) {
      const timeout = setTimeout(() => {
        setTypedText(prev => prev + welcomeMessage[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, 50) // Type speed: 50ms per character
      
      return () => clearTimeout(timeout)
    } else if (currentIndex >= welcomeMessage.length && isTyping) {
      setIsTyping(false)
      // Call onTypingComplete after a short delay
      setTimeout(() => {
        onTypingComplete?.()
      }, 1000)
    }
  }, [currentIndex, isTyping, welcomeMessage, onTypingComplete])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex items-start space-x-3 ${className}`}
    >
      {/* Assistant Avatar */}
      <div
        className="w-8 h-8 rounded-full flex-shrink-0 border"
        style={{
          backgroundColor: "#31B8E9",
          opacity: 0.4,
          backdropFilter: "blur(12px)",
          borderColor: "rgba(49, 184, 233, 0.2)",
          boxShadow:
            "inset 0 0 15px rgba(255, 255, 255, 0.3), inset 0 0 30px rgba(255, 255, 255, 0.1)",
        }}
      />

      {/* Typing Bubble */}
      <div className="bg-white/10 border-white/20 px-6 py-4 rounded-2xl backdrop-blur-sm border max-w-md">
        <div className="flex items-start space-x-2">
          {/* Rotating Star */}
          <div className="flex-shrink-0 mt-1">
            <MandryLoadingSpinner className="w-4 h-4" />
          </div>
          
          {/* Typing Content */}
          <div className="flex-1 text-white">
            {typedText}
            {isTyping && (
              <motion.span
                className="inline-block w-2 h-4 bg-white ml-1"
                animate={{ opacity: [1, 0, 1] }}
                transition={{ duration: 0.8, repeat: Infinity }}
              />
            )}
          </div>
        </div>
        
        {/* Typing Dots */}
        {isTyping && (
          <div className="flex space-x-1 mt-2 ml-6">
            {[0, 1, 2].map((index) => (
              <motion.div
                key={index}
                className="w-2 h-2 bg-white/60 rounded-full"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 1.4,
                  repeat: Infinity,
                  delay: index * 0.2,
                  ease: "easeInOut",
                }}
              />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
} 