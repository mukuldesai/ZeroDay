import React from 'react'
import { motion } from 'framer-motion'
import { ArrowUp } from 'lucide-react'
import { ProgressData } from '../../lib/types'
import { ProgressBar } from './ProgressBar'

interface ProgressCardProps {
  data: ProgressData
  delay?: number
}

export const ProgressCard: React.FC<ProgressCardProps> = ({ data, delay = 0 }) => {
  const percentage = (data.completed / data.total) * 100

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
    >
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-r ${data.color} flex items-center justify-center text-white`}>
          {data.icon}
        </div>
        <span className="text-sm text-gray-500">
          {data.completed}/{data.total}
        </span>
      </div>
      
      <h3 className="font-semibold text-gray-900 mb-2">{data.category}</h3>
      
      <ProgressBar 
        progress={percentage} 
        color="indigo" 
        className="mb-2"
      />
      
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{Math.round(percentage)}% complete</span>
        <motion.span 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-green-600 flex items-center"
        >
          <ArrowUp className="w-3 h-3 mr-1" />
          +12%
        </motion.span>
      </div>
    </motion.div>
  )
}