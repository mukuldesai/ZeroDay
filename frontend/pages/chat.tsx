'use client'

import React, { useState, useRef, useEffect } from 'react'
import { AnimatePresence } from 'framer-motion'
import { Zap } from 'lucide-react'
import { AgentType } from '../lib/types'
import { useChat } from '../lib/hooks/useChat'
import { agents, quickActions } from '../lib/data/chatData'

// Components
import { NavigationHeader } from '../components/layout/NavigationHeader'
import { AgentSelector } from '../components/ui/AgentSelector'
import { QuickActions } from '../components/ui/QuickActions'
import { ChatMessage } from '../components/ui/ChatMessage'
import { TypingIndicator } from '../components/ui/TypingIndicator'
import { ChatInput } from '../components/ui/ChatInput'

export default function ChatPage() {
  const { messages, isLoading, isTyping, sendMessage } = useChat()
  const [inputValue, setInputValue] = useState('')
  const [selectedAgent, setSelectedAgent] = useState<AgentType | 'auto'>('auto')
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
    await sendMessage(inputValue, selectedAgent)
    setInputValue('')
  }

  const handleQuickAction = (action: typeof quickActions[0]) => {
    setInputValue(action.text)
    setSelectedAgent(action.agent)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <NavigationHeader
        title="ZeroDay Chat"
        subtitle="AI-powered developer onboarding"
        gradient="from-blue-600 to-indigo-600"
        showSettings
      />

      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Agent Selection Sidebar */}
          <div className="lg:col-span-1">
            <AgentSelector
              agents={agents}
              selectedAgent={selectedAgent}
              onAgentSelect={setSelectedAgent}
            />
            <QuickActions
              actions={quickActions}
              onActionClick={handleQuickAction}
            />
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 h-[calc(100vh-200px)] flex flex-col">
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                <AnimatePresence>
                  {messages.map((message) => (
                    <ChatMessage key={message.id} message={message} />
                  ))}
                </AnimatePresence>

                {/* Typing Indicator */}
                {isTyping && <TypingIndicator />}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <ChatInput
                value={inputValue}
                onChange={setInputValue}
                onSend={handleSendMessage}
                selectedAgent={selectedAgent}
                isLoading={isLoading}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}