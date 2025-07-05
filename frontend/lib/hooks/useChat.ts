import { useState } from 'react'
import { Message, AgentType } from '../types'
import { toast } from 'react-hot-toast'

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Welcome to ZeroDay! I'm your AI-powered onboarding assistant. I can help you understand the codebase, create learning plans, provide mentoring, and suggest tasks. What would you like to explore first?",
      sender: 'bot',
      timestamp: new Date(),
      agent: 'knowledge'
    }
  ])
  
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)

  const sendMessage = async (content: string, selectedAgent: AgentType | 'auto') => {
    if (!content.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setIsTyping(true)

    try {
      // Simulate API call - replace with actual API call later
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I understand you're asking about authentication. Based on your codebase, I can see you're using JWT tokens with middleware validation. Let me break down the flow for you...",
        sender: 'bot',
        timestamp: new Date(),
        agent: selectedAgent === 'auto' ? 'knowledge' : selectedAgent as AgentType,
        metadata: {
          confidence: 0.92,
          sources: ['auth/middleware.py', 'utils/jwt_helper.py'],
          codeLanguage: 'python'
        }
      }

      setMessages(prev => [...prev, botMessage])
      toast.success('Response generated successfully!')
    } catch (error) {
      toast.error('Failed to get response. Please try again.')
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  return {
    messages,
    isLoading,
    isTyping,
    sendMessage
  }
}