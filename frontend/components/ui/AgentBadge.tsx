import React from 'react'
import { Code, Brain, BookOpen, CheckSquare } from 'lucide-react'

export type AgentType = 'knowledge' | 'mentor' | 'guide' | 'task'

interface AgentConfig {
  name: string
  icon: React.ReactNode
  color: string
  bgColor: string
}

export const agentConfigs: Record<AgentType, AgentConfig> = {
  knowledge: {
    name: 'Knowledge',
    icon: <Code className="w-4 h-4" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200'
  },
  mentor: {
    name: 'Mentor', 
    icon: <Brain className="w-4 h-4" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200'
  },
  guide: {
    name: 'Guide',
    icon: <BookOpen className="w-4 h-4" />,
    color: 'text-green-600', 
    bgColor: 'bg-green-50 border-green-200'
  },
  task: {
    name: 'Task',
    icon: <CheckSquare className="w-4 h-4" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200'
  }
}

interface AgentBadgeProps {
  agent: AgentType
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  className?: string
  userId?: string
}

export const AgentBadge: React.FC<AgentBadgeProps> = ({
  agent,
  size = 'md',
  showIcon = true,
  className = '',
  userId
}) => {
  const config = agentConfigs[agent]
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm', 
    lg: 'px-4 py-2 text-base'
  }

  return (
    <span className={`
      inline-flex items-center space-x-1 rounded-full font-medium border-2
      ${config.color} ${config.bgColor} ${sizeClasses[size]} ${className}
    `}>
      {showIcon && config.icon}
      <span>{config.name}</span>
    </span>
  )
}