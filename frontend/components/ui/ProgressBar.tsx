import React from 'react'
import { motion, easeOut } from 'framer-motion'

interface ProgressBarProps {
  progress: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'indigo'
  className?: string
  animated?: boolean
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  showLabel = true,
  size = 'md',
  color = 'indigo',
  className = '',
  animated = true
}) => {
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  }

  const colorClasses = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600', 
    orange: 'from-orange-500 to-orange-600',
    purple: 'from-purple-500 to-purple-600',
    indigo: 'from-indigo-500 to-purple-500'
  }

  const ProgressComponent = animated ? motion.div : 'div'
  const progressProps = animated ? {
    initial: { width: 0 },
    animate: { width: `${progress}%` },
    transition: { duration: 1, ease: easeOut }

  } : {
    style: { width: `${progress}%` }
  }

  return (
    <div className={className}>
      {showLabel && (
        <div className="flex items-center justify-between text-sm mb-1">
          <span className="text-gray-600">Progress</span>
          <span className="font-medium">{Math.round(progress)}%</span>
        </div>
      )}
      <div className={`w-full bg-gray-200 rounded-full ${sizeClasses[size]}`}>
        <ProgressComponent
          {...progressProps}
          className={`${sizeClasses[size]} rounded-full bg-gradient-to-r ${colorClasses[color]}`}
        />
      </div>
    </div>
  )
}