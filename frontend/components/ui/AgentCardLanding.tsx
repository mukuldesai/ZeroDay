import React from 'react'
import { motion } from 'framer-motion'

interface AgentCardLandingProps {
  agent: {
    name: string
    description: string
    icon: React.ReactNode
    color: string
    bgColor: string
    features: string[]
  }
  delay?: number
  isDemo?: boolean
}

export const AgentCardLanding: React.FC<AgentCardLandingProps> = ({ 
  agent, 
  delay = 0,
  isDemo = false 
}) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    whileHover={{ scale: 1.02 }}
    className={`bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 ${
      isDemo ? 'ring-2 ring-demo-200' : ''
    }`}
  >
    <div className={`w-14 h-14 rounded-xl ${agent.bgColor} flex items-center justify-center mb-4`}>
      <div className={agent.color}>
        {agent.icon}
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 mb-2">{agent.name}</h3>
    <p className="text-gray-600 mb-4">{agent.description}</p>
    <ul className="space-y-2">
      {agent.features.map((feature, index) => (
        <li key={index} className="flex items-center text-sm text-gray-600">
          <div className={`w-1.5 h-1.5 rounded-full mr-3 ${
            isDemo ? 'bg-demo-500' : 'bg-indigo-500'
          }`}></div>
          {feature}
        </li>
      ))}
    </ul>
    {isDemo && (
      <div className="mt-4 text-xs bg-demo-50 text-demo-700 px-2 py-1 rounded-full inline-block">
        Demo Mode
      </div>
    )}
  </motion.div>
)