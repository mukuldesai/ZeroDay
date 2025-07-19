import React from 'react'
import { motion } from 'framer-motion'

interface FeatureCardProps {
  icon: React.ReactNode
  title: string
  description: string
  color: string
  bgColor: string
  delay?: number
  isDemo?: boolean
}

export const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  color,
  bgColor,
  delay = 0,
  isDemo = false
}) => (
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.6 }}
    whileHover={{ scale: 1.02, y: -5 }}
    className={`group bg-white rounded-2xl p-8 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 ${
      isDemo ? 'ring-2 ring-demo-200' : ''
    }`}
  >
    <div className={`w-16 h-16 rounded-2xl ${bgColor} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
      <div className={color}>
        {icon}
      </div>
    </div>
    <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
    {isDemo && (
      <div className="mt-4 text-xs bg-demo-50 text-demo-700 px-2 py-1 rounded-full inline-block">
        Available in demo
      </div>
    )}
  </motion.div>
)