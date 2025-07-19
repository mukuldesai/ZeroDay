import React from 'react'
import { motion } from 'framer-motion'
import { MotionButton } from './MotionButton'

interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  className?: string
  isDemo?: boolean
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  className = '',
  isDemo = false
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`text-center py-12 ${className}`}
    >
      <div className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 ${
        isDemo ? 'bg-demo-100' : 'bg-gray-100'
      }`}>
        <div className={`${isDemo ? 'text-demo-400' : 'text-gray-400'} [&>svg]:w-12 [&>svg]:h-12`}>
          {icon}
        </div>
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">{description}</p>
      {actionLabel && onAction && (
        <MotionButton 
          onClick={onAction} 
          className={`mx-auto ${isDemo ? 'bg-demo-600 hover:bg-demo-700' : ''}`}
        >
          {actionLabel}
        </MotionButton>
      )}
      {isDemo && (
        <div className="mt-4 text-xs text-demo-600">
          Demo mode active - synthetic data will be generated
        </div>
      )}
    </motion.div>
  )
}