import React from 'react'
import { motion, HTMLMotionProps } from 'framer-motion'

type MotionButtonProps = HTMLMotionProps<'button'> & {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'demo' | 'auth'
  size?: 'sm' | 'md' | 'lg'
}

export const MotionButton = ({
  children,
  className = '',
  disabled = false,
  variant = 'primary',
  size = 'md',
  type = 'button',
  ...rest
}: MotionButtonProps) => {
  const baseClasses =
    'font-medium rounded-xl transition-all duration-300 flex items-center justify-center space-x-2'

  const variantClasses = {
    primary: 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white hover:shadow-lg',
    secondary: 'bg-white text-gray-900 border border-gray-200 hover:shadow-lg',
    ghost: 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700',
    demo: 'bg-gradient-to-r from-demo-600 to-demo-700 text-white hover:shadow-lg',
    auth: 'bg-gradient-to-r from-auth-600 to-auth-700 text-white hover:shadow-lg'
  }

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.05 }}
      whileTap={{ scale: disabled ? 1 : 0.95 }}
      disabled={disabled}
      type={type}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      {...rest}
    >
      {children}
    </motion.button>
  )
}