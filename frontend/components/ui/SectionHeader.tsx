import React from 'react'
import { motion } from 'framer-motion'

interface SectionHeaderProps {
  title: string
  subtitle: string
  centered?: boolean
  className?: string
  isDemo?: boolean
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  centered = true,
  className = '',
  isDemo = false
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
      className={`${centered ? 'text-center' : ''} mb-16 ${className}`}
    >
      <div className="flex items-center justify-center space-x-3 mb-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
          {title}
        </h2>
        {isDemo && (
          <span className="bg-demo-100 text-demo-700 px-3 py-1 rounded-full text-sm font-medium">
            Demo
          </span>
        )}
      </div>
      <p className={`text-xl text-gray-600 ${centered ? 'max-w-3xl mx-auto' : ''}`}>
        {isDemo 
          ? `${subtitle} (Currently showing demo data)`
          : subtitle
        }
      </p>
    </motion.div>
  )
}