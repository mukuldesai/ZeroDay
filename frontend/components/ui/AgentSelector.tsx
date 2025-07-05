import React from 'react'
import { motion } from 'framer-motion'
import { Zap, Sparkles } from 'lucide-react'
import { AgentType, Agent } from '../../lib/types'
import { MotionButton } from './MotionButton'

interface AgentSelectorProps {
  agents: Agent[]
  selectedAgent: AgentType | 'auto'
  onAgentSelect: (agent: AgentType | 'auto') => void
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onAgentSelect
}) => {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 sticky top-24">
      <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
        <Sparkles className="w-4 h-4 mr-2 text-indigo-600" />
        AI Agents
      </h3>
      
      <div className="space-y-3">
        <MotionButton
          onClick={() => onAgentSelect('auto')}
          className={`w-full p-3 rounded-lg border-2 transition-all ${
            selectedAgent === 'auto' 
              ? 'bg-indigo-50 border-indigo-200 text-indigo-700' 
              : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
          }`}
          variant="ghost"
        >
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4" />
            <span className="font-medium">Auto Select</span>
          </div>
          <p className="text-xs text-gray-600 mt-1">Let AI choose the best agent</p>
        </MotionButton>

        {agents.map((agent) => (
          <MotionButton
            key={agent.id}
            onClick={() => onAgentSelect(agent.id)}
            className={`w-full p-3 rounded-lg border-2 transition-all ${
              selectedAgent === agent.id 
                ? `${agent.bgColor} ${agent.color}` 
                : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
            }`}
            variant="ghost"
          >
            <div className="flex items-center space-x-2">
              {agent.icon}
              <span className="font-medium">{agent.name}</span>
            </div>
            <p className="text-xs text-gray-600 mt-1">{agent.description}</p>
          </MotionButton>
        ))}
      </div>
    </div>
  )
}