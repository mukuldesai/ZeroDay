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
}

export const AgentCardLanding: React.FC<AgentCardLandingProps> = ({ agent, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    whileHover={{ scale: 1.02 }}
    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
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
          <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mr-3"></div>
          {feature}
        </li>
      ))}
    </ul>
  </motion.div>
)