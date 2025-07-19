import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X } from 'lucide-react'
import { modalVariants, backdropVariants } from '../../lib/animations/variants'
import { MotionButton } from './MotionButton'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showCloseButton?: boolean
  className?: string
  isDemo?: boolean
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  className = '',
  isDemo = false
}) => {
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl'
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          variants={backdropVariants}
          initial="initial"
          animate="animate"
          exit="exit"
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            variants={modalVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className={`
              bg-white rounded-2xl w-full ${sizeClasses[size]} max-h-[90vh] 
              overflow-y-auto shadow-2xl ${className} ${
                isDemo ? 'ring-4 ring-demo-200' : ''
              }
            `}
            onClick={(e) => e.stopPropagation()}
          >
            {(title || showCloseButton || isDemo) && (
              <div className={`flex items-center justify-between p-6 border-b border-gray-200 ${
                isDemo ? 'bg-demo-50' : ''
              }`}>
                <div className="flex items-center space-x-3">
                  {title && (
                    <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
                  )}
                  {isDemo && (
                    <span className="bg-demo-100 text-demo-700 px-2 py-1 rounded-full text-xs font-medium">
                      Demo Mode
                    </span>
                  )}
                </div>
                {showCloseButton && (
                  <MotionButton
                    variant="ghost"
                    size="sm"
                    onClick={onClose}
                  >
                    <X className="w-5 h-5" />
                  </MotionButton>
                )}
              </div>
            )}
            <div className="p-6">
              {children}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
