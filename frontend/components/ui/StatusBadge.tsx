import React from 'react'

export type StatusType = 'todo' | 'in-progress' | 'review' | 'completed' | 'pending' | 'blocked'| 'suggested'
export type PriorityType = 'low' | 'medium' | 'high' | 'urgent'
export type DifficultyType = 'easy' | 'medium' | 'hard'

interface StatusConfig {
  label: string
  className: string
}

export const statusConfigs: Record<StatusType, StatusConfig> = {
  'todo': {
    label: 'To Do',
    className: 'bg-gray-100 text-gray-700 border-gray-300'
  },
  'in-progress': {
    label: 'In Progress',
    className: 'bg-blue-100 text-blue-700 border-blue-300'
  },
  'review': {
    label: 'Review',
    className: 'bg-yellow-100 text-yellow-700 border-yellow-300'
  },
  'completed': {
    label: 'Completed',
    className: 'bg-green-100 text-green-700 border-green-300'
  },
   'blocked': {
    label: 'Blocked',
    className: 'bg-red-100 text-red-700 border-red-300'
  },
  'pending': {
    label: 'Pending',
    className: 'bg-gray-100 text-gray-700 border-gray-300'
  },
  'suggested': {
    label: 'Suggested',
    className: 'bg-orange-100 text-orange-700 border-orange-300'
  }
}

export const priorityConfigs: Record<PriorityType, StatusConfig> = {
  'low': {
    label: 'Low',
    className: 'bg-green-100 text-green-700'
  },
  'medium': {
    label: 'Medium', 
    className: 'bg-yellow-100 text-yellow-700'
  },
  'high': {
    label: 'High',
    className: 'bg-orange-100 text-orange-700'
  },
  'urgent': {
    label: 'Urgent',
    className: 'bg-red-100 text-red-700'
  }
}

export const difficultyConfigs: Record<DifficultyType, StatusConfig> = {
  'easy': {
    label: 'Easy',
    className: 'bg-green-100 text-green-700'
  },
  'medium': {
    label: 'Medium',
    className: 'bg-yellow-100 text-yellow-700'
  },
  'hard': {
    label: 'Hard', 
    className: 'bg-red-100 text-red-700'
  }
}

interface StatusBadgeProps {
  type: 'status' | 'priority' | 'difficulty'
  value: StatusType | PriorityType | DifficultyType
  size?: 'sm' | 'md'
  className?: string
  isDemo?: boolean
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  type,
  value,
  size = 'md',
  className = '',
  isDemo = false
}) => {
  const config =
  type === 'status'
    ? statusConfigs[value as StatusType]
    : type === 'priority'
    ? priorityConfigs[value as PriorityType]
    : difficultyConfigs[value as DifficultyType];

  
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm'
  }

  const baseClasses = type === 'status' 
    ? 'rounded-full font-medium border-2' 
    : 'rounded font-medium'

  const demoClasses = isDemo ? 'ring-1 ring-demo-300' : ''

  return (
    <span className={`
      inline-flex items-center ${baseClasses} ${sizeClasses[size]} 
      ${config.className} ${demoClasses} ${className}
    `}>
      {config.label}
    </span>
  )
}