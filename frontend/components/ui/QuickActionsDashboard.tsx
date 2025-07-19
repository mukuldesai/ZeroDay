import React from 'react'
import { motion } from 'framer-motion'
import { AgentType } from '../../lib/types'

interface QuickAction {
  text: string
  agent: AgentType
  icon: React.ReactNode
}

interface QuickActionsProps {
  actions: QuickAction[]
  onActionClick: (action: QuickAction) => void
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  actions,
  onActionClick
}) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50">
      <h3 className="text-white font-semibold mb-4">Quick Actions</h3>
      
      <div className="space-y-2">
        {actions.map((action, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onActionClick(action)}
            className="w-full text-left p-3 bg-gray-700/50 rounded-lg text-gray-300 hover:bg-gray-600/50 hover:text-white transition-all duration-200 text-sm group"
          >
            <div className="flex items-start space-x-2">
              <div className="text-gray-400 group-hover:text-white mt-0.5">
                {action.icon}
              </div>
              <span className="leading-relaxed">{action.text}</span>
            </div>
          </motion.button>
        ))}
      </div>
      
   
      <div className="mt-4 pt-4 border-t border-gray-700/50">
        <p className="text-xs text-gray-400 text-center">
          Click any action to try it with AI agents
        </p>
      </div>
    </div>
  )
}