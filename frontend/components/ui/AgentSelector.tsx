import React from 'react'
import { motion } from 'framer-motion'
import { Zap } from 'lucide-react'
import { AgentType } from '../../lib/types'

interface Agent {
  id: AgentType | 'auto'
  name: string
  description: string
  icon: React.ReactNode
  color: string
  available: boolean
}

interface AgentSelectorProps {
  agents: Agent[]
  selectedAgent: AgentType | 'auto'
  onAgentSelect: (agentId: AgentType | 'auto') => void
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  agents,
  selectedAgent,
  onAgentSelect
}) => {
  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-gray-700/50 mb-6">
      <h3 className="text-white font-semibold mb-4 flex items-center">
        <Zap className="w-5 h-5 mr-2 text-yellow-400" />
        AI Agents
      </h3>
      
      <div className="space-y-2">
        {agents.map((agent, index) => (
          <motion.button
            key={agent.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            onClick={() => onAgentSelect(agent.id)}
            className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
              selectedAgent === agent.id 
                ? 'bg-blue-600 text-white transform scale-105' 
                : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="text-white">
                  {agent.icon}
                </div>
                <span className="font-medium">{agent.name}</span>
              </div>
              
             
              {agent.id !== 'auto' && (
                <div className="flex items-center space-x-1">
                  <div className={`w-2 h-2 rounded-full ${
                    agent.available ? 'bg-green-400 animate-pulse' : 'bg-red-400'
                  }`}></div>
                  <span className="text-xs text-gray-400">
                    {agent.available ? 'Active' : 'Offline'}
                  </span>
                </div>
              )}
            </div>
            
            <p className="text-xs mt-1 opacity-80 text-left">
              {agent.description}
            </p>
          </motion.button>
        ))}
      </div>
      
    
      <div className="mt-4 pt-4 border-t border-gray-700/50">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span>Agents Online</span>
          <span className="text-green-400 font-medium">
            {agents.filter(a => a.id !== 'auto' && a.available).length}/4
          </span>
        </div>
      </div>
    </div>
  )
}