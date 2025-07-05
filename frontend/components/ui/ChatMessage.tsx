import React from 'react'
import { motion } from 'framer-motion'
import { User, Bot, Copy, ThumbsUp, ThumbsDown, FileText } from 'lucide-react'
import { Message } from '../../lib/types'
import { AgentBadge, agentConfigs } from './AgentBadge'
import { MotionButton } from './MotionButton'
import { useCopyToClipboard } from '../../lib/hooks/useCopyToClipboard'

interface ChatMessageProps {
  message: Message
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const { copy } = useCopyToClipboard()

  const handleCopy = () => {
    copy(message.content)
  }

  return (
    <motion.div
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
                ? agentConfigs[message.agent]?.bgColor 
                : 'bg-gray-200'
          }`}>
            {message.sender === 'user' ? (
              <User className="w-4 h-4" />
            ) : (
              message.agent ? agentConfigs[message.agent]?.icon : <Bot className="w-4 h-4" />
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
                <AgentBadge agent={message.agent} size="sm" />
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
            <MotionButton variant="ghost" size="sm" onClick={handleCopy}>
              <Copy className="w-3 h-3" />
            </MotionButton>
            <MotionButton variant="ghost" size="sm">
              <ThumbsUp className="w-3 h-3" />
            </MotionButton>
            <MotionButton variant="ghost" size="sm">
              <ThumbsDown className="w-3 h-3" />
            </MotionButton>
          </div>
        )}
      </div>
    </motion.div>
  )
}