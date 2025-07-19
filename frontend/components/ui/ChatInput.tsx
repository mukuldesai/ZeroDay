import React from 'react'
import { Send, Brain, BookOpen, Target, Users, MessageSquare } from 'lucide-react'
import { MotionButton } from './MotionButton'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSend: () => void
  selectedAgent: 'auto' | 'knowledge' | 'task' | 'mentor' | 'guide'
  isLoading: boolean
  placeholder?: string
  userName?: string
}

const agentConfigs = {
  auto: {
    name: 'Auto Select',
    icon: <Brain className="w-3 h-3" />,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100'
  },
  knowledge: {
    name: 'Knowledge',
    icon: <BookOpen className="w-3 h-3" />,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100'
  },
  task: {
    name: 'Task',
    icon: <Target className="w-3 h-3" />,
    color: 'text-orange-700',
    bgColor: 'bg-orange-100'
  },
  mentor: {
    name: 'Mentor',
    icon: <Users className="w-3 h-3" />,
    color: 'text-purple-700',
    bgColor: 'bg-purple-100'
  },
  guide: {
    name: 'Guide',
    icon: <MessageSquare className="w-3 h-3" />,
    color: 'text-green-700',
    bgColor: 'bg-green-100'
  }
}

export const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onSend,
  selectedAgent,
  isLoading,
  placeholder,
  userName = "Developer"
}) => {
  const defaultPlaceholder = `Ask about code, request guidance, or get task suggestions...`

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (value.trim() && !isLoading) {
        onSend()
      }
    }
  }

  const currentAgent = agentConfigs[selectedAgent as keyof typeof agentConfigs] || agentConfigs.auto

  return (
    <div className="border-t border-gray-700/50 bg-gray-800/30 p-4">
      <div className="flex items-center space-x-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder || defaultPlaceholder}
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20"
            disabled={isLoading}
          />

          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className={`flex items-center space-x-1 text-xs px-2 py-1 rounded-full ${currentAgent.bgColor} ${currentAgent.color}`}>
              {currentAgent.icon}
              <span className="font-medium">{currentAgent.name}</span>
            </div>
          </div>
        </div>

        <MotionButton
          onClick={onSend}
          disabled={!value.trim() || isLoading}
          className="bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </MotionButton>
      </div>

      <div className="mt-2 text-xs text-gray-400 text-center">
        {selectedAgent === 'auto'
          ? "AI will choose the best agent for your request"
          : `Sending to ${currentAgent.name} Agent`
        }
      </div>
    </div>
  )
}
