import React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Play } from 'lucide-react'

interface VideoModalProps {
  isOpen: boolean
  onClose: () => void
  isDemo?: boolean
}

export const VideoModal: React.FC<VideoModalProps> = ({ 
  isOpen, 
  onClose,
  isDemo = false 
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.5 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0.5 }}
            className={`bg-white rounded-2xl p-8 max-w-4xl w-full ${
              isDemo ? 'ring-4 ring-demo-300' : ''
            }`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center">
              <div className="flex items-center justify-center space-x-3 mb-4">
                <h3 className="text-2xl font-bold text-gray-900">
                  {isDemo ? 'ZeroDay Demo Walkthrough' : 'ZeroDay Demo Video'}
                </h3>
                {isDemo && (
                  <span className="bg-demo-100 text-demo-700 px-2 py-1 rounded-full text-xs font-medium">
                    Demo Mode
                  </span>
                )}
              </div>
              <div className={`rounded-xl h-64 flex items-center justify-center mb-6 ${
                isDemo ? 'bg-demo-100' : 'bg-gray-100'
              }`}>
                <div className={`${isDemo ? 'text-demo-500' : 'text-gray-500'}`}>
                  <Play className="w-16 h-16 mx-auto mb-4" />
                  <p>
                    {isDemo 
                      ? 'Interactive demo walkthrough will be shown here'
                      : 'Demo video will be embedded here'
                    }
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className={`px-6 py-2 rounded-lg transition-colors ${
                  isDemo 
                    ? 'bg-demo-600 text-white hover:bg-demo-700'
                    : 'bg-gray-600 text-white hover:bg-gray-700'
                }`}
              >
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}