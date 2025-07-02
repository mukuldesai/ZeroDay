'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Send, 
  Bot, 
  User, 
  Code, 
  BookOpen, 
  MessageSquare, 
  CheckSquare,
  Loader2,
  Sparkles,
  Brain,
  GitBranch,
  Lightbulb,
  FileText,
  Zap,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Settings
} from 'lucide-react'
import { toast } from 'react-hot-toast'

// Types
interface Message {
  id: string
  content: string
  sender: 'user' | 'bot'
  timestamp: Date
  agent?: 'knowledge' | 'mentor' | 'guide' | 'task'
  type?: 'text' | 'code' | 'plan' | 'task'
  metadata?: {
    confidence?: number
    sources?: string[]
    codeLanguage?: string
  }
}

interface Agent {
  id: 'knowledge' | 'mentor' | 'guide' | 'task'
  name: string
  description: string
  icon: React.ReactNode
  color: string
  bgColor: string
}

const agents: Agent[] = [
  {
    id: 'knowledge',
    name: 'Knowledge',
    description: 'Code search & explanations',
    icon: <Code className="w-4 h-4" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200'
  },
  {
    id: 'mentor',
    name: 'Mentor',
    description: 'Senior developer guidance',
    icon: <Brain className="w-4 h-4" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200'
  },
  {
    id: 'guide',
    name: 'Guide',
    description: 'Learning path generation',
    icon: <BookOpen className="w-4 h-4" />,
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200'
  },
  {
    id: 'task',
    name: 'Task',
    description: 'Task recommendations',
    icon: <CheckSquare className="w-4 h-4" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200'
  }
]

const quickActions = [
  { text: "Explain authentication flow", icon: <Code className="w-3 h-3" />, agent: 'knowledge' },
  { text: "Create learning plan", icon: <BookOpen className="w-3 h-3" />, agent: 'guide' },
  { text: "Help with debugging", icon: <Brain className="w-3 h-3" />, agent: 'mentor' },
  { text: "Suggest first task", icon: <CheckSquare className="w-3 h-3" />, agent: 'task' }
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Welcome to ZeroDay! I'm your AI-powered onboarding assistant. I can help you understand the codebase, create learning plans, provide mentoring, and suggest tasks. What would you like to explore first?",
      sender: 'bot',
      timestamp: new Date(),
      agent: 'knowledge'
    }
  ])
  
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<Agent['id'] | 'auto'>('auto')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
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
        agent: selectedAgent === 'auto' ? 'knowledge' : selectedAgent as Agent['id'],
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

  const handleQuickAction = (action: typeof quickActions[0]) => {
    setInputValue(action.text)
    setSelectedAgent(action.agent as Agent['id'])
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const getAgentInfo = (agentId: Agent['id']) => {
    return agents.find(agent => agent.id === agentId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <div className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-xl">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ZeroDay Chat</h1>
                <p className="text-sm text-gray-600">AI-powered developer onboarding</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="w-5 h-5" />
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Agent Selection Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sticky top-24">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
                <Sparkles className="w-4 h-4 mr-2 text-indigo-600" />
                AI Agents
              </h3>
              
              <div className="space-y-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedAgent('auto')}
                  className={`w-full p-3 rounded-lg border-2 transition-all ${
                    selectedAgent === 'auto' 
                      ? 'bg-indigo-50 border-indigo-200 text-indigo-700' 
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Zap className="w-4 h-4" />
                    <span className="font-medium">Auto Select</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Let AI choose the best agent</p>
                </motion.button>

                {agents.map((agent) => (
                  <motion.button
                    key={agent.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedAgent(agent.id)}
                    className={`w-full p-3 rounded-lg border-2 transition-all ${
                      selectedAgent === agent.id 
                        ? `${agent.bgColor} ${agent.color}` 
                        : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {agent.icon}
                      <span className="font-medium">{agent.name}</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-1">{agent.description}</p>
                  </motion.button>
                ))}
              </div>

              {/* Quick Actions */}
              <div className="mt-6">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Lightbulb className="w-4 h-4 mr-2 text-yellow-500" />
                  Quick Actions
                </h4>
                <div className="space-y-2">
                  {quickActions.map((action, index) => (
                    <motion.button
                      key={index}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleQuickAction(action)}
                      className="w-full p-2 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm"
                    >
                      <div className="flex items-center space-x-2">
                        {action.icon}
                        <span>{action.text}</span>
                      </div>
                    </motion.button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 h-[calc(100vh-200px)] flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${message.sender === 'user' ? 'order-2' : 'order-1'}`}>
                        <div className={`flex items-start space-x-3 ${message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                          {/* Avatar */}
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                            message.sender === 'user' 
                              ? 'bg-indigo-600 text-white' 
                              : message.agent 
                                ? getAgentInfo(message.agent)?.bgColor 
                                : 'bg-gray-200'
                          }`}>
                            {message.sender === 'user' ? (
                              <User className="w-4 h-4" />
                            ) : (
                              message.agent ? getAgentInfo(message.agent)?.icon : <Bot className="w-4 h-4" />
                            )}
                          </div>

                          {/* Message Bubble */}
                          <div className={`rounded-2xl px-4 py-3 ${
                            message.sender === 'user'
                              ? 'bg-indigo-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            {message.agent && message.sender === 'bot' && (
                              <div className="flex items-center space-x-1 mb-2">
                                <span className={`text-xs font-medium ${getAgentInfo(message.agent)?.color}`}>
                                  {getAgentInfo(message.agent)?.name} Agent
                                </span>
                                {message.metadata?.confidence && (
                                  <span className="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">
                                    {Math.round(message.metadata.confidence * 100)}% confident
                                  </span>
                                )}
                              </div>
                            )}
                            <p className="text-sm leading-relaxed">{message.content}</p>
                            
                            {message.metadata?.sources && (
                              <div className="mt-2 pt-2 border-t border-gray-200">
                                <p className="text-xs text-gray-600 mb-1">Sources:</p>
                                <div className="flex flex-wrap gap-1">
                                  {message.metadata.sources.map((source, index) => (
                                    <span key={index} className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                      <FileText className="w-3 h-3 inline mr-1" />
                                      {source}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Message Actions */}
                        {message.sender === 'bot' && (
                          <div className="flex items-center space-x-2 mt-2 ml-11">
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => copyToClipboard(message.content)}
                              className="p-1 text-gray-400 hover:text-gray-600 rounded"
                            >
                              <Copy className="w-3 h-3" />
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              className="p-1 text-gray-400 hover:text-green-600 rounded"
                            >
                              <ThumbsUp className="w-3 h-3" />
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              className="p-1 text-gray-400 hover:text-red-600 rounded"
                            >
                              <ThumbsDown className="w-3 h-3" />
                            </motion.button>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Typing Indicator */}
                {isTyping && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex justify-start"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <Bot className="w-4 h-4" />
                      </div>
                      <div className="bg-gray-100 rounded-2xl px-4 py-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t bg-gray-50 p-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-1 relative">
                    <input
                      ref={inputRef}
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Ask about code, request guidance, or get task suggestions..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      disabled={isLoading}
                    />
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      {selectedAgent !== 'auto' && (
                        <div className={`text-xs px-2 py-1 rounded-full ${getAgentInfo(selectedAgent as Agent['id'])?.bgColor} ${getAgentInfo(selectedAgent as Agent['id'])?.color}`}>
                          {getAgentInfo(selectedAgent as Agent['id'])?.name}
                        </div>
                      )}
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </motion.button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}