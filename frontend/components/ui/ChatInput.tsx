import React from 'react'
import { Send } from 'lucide-react'
import { AgentType } from '../../lib/types'
import { agentConfigs } from './AgentBadge'
import { MotionButton } from './MotionButton'
import { LoadingSpinner } from './LoadingSpinner'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  selectedAgent: AgentType | 'auto'
  isLoading: boolean
  placeholder?: string
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  selectedAgent,
  isLoading,
  placeholder = "Ask about code, request guidance, or get task suggestions..."
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSend()
    }
  }

  return (
    <div className="border-t bg-gray-50 p-4">
      <div className="flex items-center space-x-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            disabled={isLoading}
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            {selectedAgent !== 'auto' && (
              <div className={`text-xs px-2 py-1 rounded-full ${agentConfigs[selectedAgent as AgentType]?.bgColor} ${agentConfigs[selectedAgent as AgentType]?.color}`}>
                {agentConfigs[selectedAgent as AgentType]?.name}
              </div>
            )}
          </div>
        </div>
        <MotionButton
          onClick={onSend}
          disabled={!value.trim() || isLoading}
          className="bg-indigo-600 text-white p-3 rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </MotionButton>
      </div>
    </div>
  )
}