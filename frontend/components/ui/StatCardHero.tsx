import React from 'react'
import { motion } from 'framer-motion'

interface StatCardHeroProps {
  icon: React.ReactNode
  value: string | number
  label: string
  color: string
  delay?: number
  userId?: string
  statUserId?: string
}

export const StatCardHero: React.FC<StatCardHeroProps> = ({
  icon,
  value,
  label,
  color,
  delay = 0,
  userId,
  statUserId
}) => {
  const userOwnsStat = !userId || !statUserId || statUserId === userId
  const displayValue = userOwnsStat ? value : '—'

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      whileHover={{ scale: 1.05, y: -5 }}
      className={`bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 ${
        !userOwnsStat ? 'opacity-75' : ''
      }`}
    >
      <div className={`w-12 h-12 rounded-xl ${color} flex items-center justify-center mb-4`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{displayValue}</div>
      <div className="text-gray-600 text-sm">{label}</div>
    </motion.div>
  )
}