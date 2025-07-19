import React from 'react'
import { motion } from 'framer-motion'
import { User, Bot, Copy, ThumbsUp, ThumbsDown, FileText, Clock, BookOpen, Target, Users, MessageSquare } from 'lucide-react'
import { MotionButton } from './MotionButton'

interface ChatMessageProps {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string 
    agent?: 'knowledge' | 'mentor' | 'task' | 'guide'
    confidence?: number
    responseTime?: string
    metadata?: {
      sources?: string[]
      confidence?: number
    }
  }
  userName?: string
}

const agentConfigs = {
  knowledge: {
    name: 'Knowledge Agent',
    icon: <BookOpen className="w-4 h-4" />,
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    darkBgColor: 'bg-blue-900/50',
    darkColor: 'text-blue-300'
  },
  task: {
    name: 'Task Agent',
    icon: <Target className="w-4 h-4" />,
    color: 'text-orange-700',
    bgColor: 'bg-orange-100',
    darkBgColor: 'bg-orange-900/50',
    darkColor: 'text-orange-300'
  },
  mentor: {
    name: 'Mentor Agent',
    icon: <Users className="w-4 h-4" />,
    color: 'text-purple-700',
    bgColor: 'bg-purple-100',
    darkBgColor: 'bg-purple-900/50',
    darkColor: 'text-purple-300'
  },
  guide: {
    name: 'Guide Agent',
    icon: <MessageSquare className="w-4 h-4" />,
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    darkBgColor: 'bg-green-900/50',
    darkColor: 'text-green-300'
  }
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, userName = "Developer" }) => {
  const handleCopy = () => {
    navigator.clipboard.writeText(message.content)
  }


  const agentConfig = message.agent ? agentConfigs[message.agent as keyof typeof agentConfigs] : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
        <div className={`flex items-start space-x-3 ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
            message.role === 'user' 
              ? 'bg-blue-600 text-white' 
              : agentConfig 
                ? agentConfig.darkBgColor 
                : 'bg-gray-600'
          }`}>
            {message.role === 'user' ? (
              <User className="w-4 h-4" />
            ) : (
              agentConfig ? agentConfig.icon : <Bot className="w-4 h-4" />
            )}
          </div>

          <div className={`rounded-2xl px-4 py-3 ${
            message.role === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-100'
          }`}>
            
            {message.agent && message.role === 'assistant' && agentConfig && (
              <div className="flex items-center space-x-2 mb-2 flex-wrap">
                <div className={`flex items-center space-x-1 text-xs px-2 py-1 rounded-full ${agentConfig.darkBgColor} ${agentConfig.darkColor}`}>
                  {agentConfig.icon}
                  <span className="font-medium">{agentConfig.name}</span>
                </div>
                
                {message.confidence && (
                  <span className="text-xs bg-green-900/50 text-green-300 px-2 py-1 rounded-full">
                    {Math.round(message.confidence * 100)}% confident
                  </span>
                )}
                
                {message.responseTime && (
                  <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded-full flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {message.responseTime}
                  </span>
                )}
              </div>
            )}
            
           
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {typeof message.content === 'string' ? message.content : 'Message received'}
            </p>
            
           
            {message.metadata?.sources && Array.isArray(message.metadata.sources) && message.metadata.sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-600">
                <p className="text-xs text-gray-400 mb-1">Sources:</p>
                <div className="flex flex-wrap gap-1">
                  {message.metadata.sources.map((source, index) => (
                    <span key={index} className="text-xs bg-blue-900/50 text-blue-300 px-2 py-0.5 rounded flex items-center">
                      <FileText className="w-3 h-3 mr-1" />
                      {typeof source === 'string' ? source : 'Source'}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className={`text-xs text-gray-400 mt-1 ${message.role === 'user' ? 'text-right mr-11' : 'ml-11'}`}>
          {message.role === 'user' 
            ? userName 
            : agentConfig 
              ? agentConfig.name 
              : 'AI Assistant'
          } • {new Date(message.timestamp).toLocaleTimeString()}
        </div>

        {message.role === 'assistant' && (
          <div className="flex items-center space-x-2 mt-2 ml-11">
            <MotionButton 
              variant="ghost" 
              size="sm" 
              onClick={handleCopy}
              className="text-gray-400 hover:text-gray-300 p-1"
            >
              <Copy className="w-3 h-3" />
            </MotionButton>
            <MotionButton 
              variant="ghost" 
              size="sm"
              className="text-gray-400 hover:text-gray-300 p-1"
            >
              <ThumbsUp className="w-3 h-3" />
            </MotionButton>
          </div>
        )}
      </div>
    </motion.div>
  )
}