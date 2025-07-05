import React from 'react'
import { motion } from 'framer-motion'
import { TrendingUp } from 'lucide-react'

interface StatsCardProps {
  icon: React.ReactNode
  title: string
  value: string | number
  change?: string
  color: string
  delay?: number
}

export const StatsCard: React.FC<StatsCardProps> = ({
  icon,
  title,
  value,
  change,
  color,
  delay = 0
}) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    whileHover={{ scale: 1.02, y: -2 }}
    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300"
  >
    <div className="flex items-center justify-between mb-4">
      <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center text-white`}>
        {icon}
      </div>
      {change && (
        <span className="text-sm font-medium text-green-600 flex items-center">
          <TrendingUp className="w-3 h-3 mr-1" />
          {change}
        </span>
      )}
    </div>
    <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
    <div className="text-sm text-gray-600">{title}</div>
  </motion.div>
)