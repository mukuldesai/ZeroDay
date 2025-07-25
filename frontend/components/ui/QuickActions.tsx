import React from 'react'
import { motion } from 'framer-motion'
import { Lightbulb } from 'lucide-react'
import { AgentType } from '../../lib/types'
import { MotionButton } from './MotionButton'
import type { JSX } from 'react'

interface QuickAction {
  text: string
  icon: JSX.Element 
  agent: AgentType
  userId?: string
}

interface QuickActionsProps {
  actions: QuickAction[]
  onActionClick: (action: QuickAction) => void
  userId?: string
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  actions,
  onActionClick,
  userId
}) => {
  const userActions = userId 
    ? actions.filter(action => !action.userId || action.userId === userId)
    : actions

  return (
    <div className="mt-6">
      <h4 className="font-medium text-gray-900 mb-3 flex items-center">
        <Lightbulb className="w-4 h-4 mr-2 text-yellow-500" />
        Quick Actions
      </h4>
      <div className="space-y-2">
        {userActions.map((action, index) => (
          <MotionButton
            key={index}
            onClick={() => onActionClick(action)}
            variant="ghost"
            className="w-full p-2 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-sm"
          >
            <div className="flex items-center space-x-2">
              {action.icon}
              <span>{action.text}</span>
            </div>
          </MotionButton>
        ))}
      </div>
    </div>
  )
}