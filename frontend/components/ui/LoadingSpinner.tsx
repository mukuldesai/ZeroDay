import React from 'react'
import { motion } from 'framer-motion'
import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  color?: 'default' | 'demo' | 'auth'
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  className = '',
  color = 'default'
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5', 
    lg: 'w-8 h-8'
  }

  const colorClasses = {
    default: 'text-indigo-600',
    demo: 'text-demo-600',
    auth: 'text-auth-600'
  }

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      className={`${colorClasses[color]} ${className}`}
    >
      <Loader2 className={`${sizeClasses[size]} animate-spin`} />
    </motion.div>
  )
}