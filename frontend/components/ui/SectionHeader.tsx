import React from 'react'
import { motion } from 'framer-motion'

interface SectionHeaderProps {
  title: string
  subtitle: string
  centered?: boolean
  className?: string
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  subtitle,
  centered = true,
  className = ''
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
      className={`${centered ? 'text-center' : ''} mb-16 ${className}`}
    >
      <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
        {title}
      </h2>
      <p className={`text-xl text-gray-600 ${centered ? 'max-w-3xl mx-auto' : ''}`}>
        {subtitle}
      </p>
    </motion.div>
  )
}