import { useState, useCallback } from 'react'
import { Message, AgentType } from '../types'
import { useDemo } from './useDemo'
import { demoAPI } from '../api/demoAPI'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useChat() {
  const { isDemoMode, selectedScenario } = useDemo()
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I\'m your ZeroDay AI assistant. I can help you with code questions, learning paths, tasks, and mentoring. What would you like to explore?',
      role: 'assistant',
      timestamp: new Date().toISOString(),
      agent: 'knowledge'
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)

  const loadDemoMessages = useCallback(async () => {
    if (isDemoMode && selectedScenario) {
      try {
        const demoMessages = await demoAPI.getChatMessages(selectedScenario)
        const convertedMessages: Message[] = demoMessages.map(msg => ({
          id: msg.id.toString(),
          content: msg.content,
          role: msg.sender === 'user' ? 'user' : 'assistant',
            timestamp: new Date(msg.timestamp).toISOString(),
          agent: msg.sender === 'ai' ? 'knowledge' : undefined
        }))
        setMessages(convertedMessages)
      } catch (error) {
        console.error('Failed to load demo messages:', error)
      }
    }
  }, [isDemoMode, selectedScenario])

  const sendMessage = useCallback(async (content: string, selectedAgent: AgentType | 'auto' = 'auto') => {
    if (!content.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      role: 'user',
      timestamp: new Date().toISOString(),
      agent: selectedAgent === 'auto' ? undefined : selectedAgent
    }

    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setIsTyping(true)

    try {
      if (isDemoMode) {
        setTimeout(() => {
          const demoResponse: Message = {
            id: (Date.now() + 1).toString(),
            content: `This is a demo response to: "${content}". In real mode, I would analyze your actual codebase, team conversations, and project context to provide personalized guidance.`,
            role: 'assistant',
            timestamp: new Date().toISOString(),
            agent: selectedAgent === 'auto' ? 'knowledge' : selectedAgent,
            sources: ['Demo Data'],
            suggestions: ['Try asking about your projects', 'Explore the task suggestions', 'Check out the learning paths']
          }
          setMessages(prev => [...prev, demoResponse])
          setIsLoading(false)
          setIsTyping(false)
        }, 1500)
        return
      }

      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          agent_type: selectedAgent,
          user_role: 'developer',
          context: {}
        })
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        agent: data.agent_used as AgentType,
        sources: data.sources || [],
        suggestions: data.suggestions || []
      }

      setMessages(prev => [...prev, assistantMessage])

    } catch (error) {
      console.error('Chat error:', error)
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I encountered an error connecting to the backend. Please make sure your Python server is running on ${API_BASE}. Error: ${(error as Error).message}`,
        role: 'assistant',
        timestamp: new Date().toISOString(),
        agent: 'knowledge'
      }

      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }, [isDemoMode, selectedScenario])

  const clearMessages = useCallback(() => {
    setMessages([{
      id: '1',
      content: 'Hello! I\'m your ZeroDay AI assistant. How can I help you today?',
      role: 'assistant',
      timestamp: new Date().toISOString(),
      agent: 'knowledge'
    }])
  }, [])

  return {
    messages,
    isLoading,
    isTyping,
    sendMessage,
    clearMessages,
    loadDemoMessages
  }
}