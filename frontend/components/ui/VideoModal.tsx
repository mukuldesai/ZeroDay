import React from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Play } from 'lucide-react'
import { Modal } from './Modal'

interface VideoModalProps {
  isOpen: boolean
  onClose: () => void
}

export const VideoModal: React.FC<VideoModalProps> = ({ isOpen, onClose }) => {
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
            className="bg-white rounded-2xl p-8 max-w-4xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">ZeroDay Demo Video</h3>
              <div className="bg-gray-100 rounded-xl h-64 flex items-center justify-center mb-6">
                <div className="text-gray-500">
                  <Play className="w-16 h-16 mx-auto mb-4" />
                  <p>Demo video will be embedded here</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="bg-gray-600 text-white px-6 py-2 rounded-lg hover:bg-gray-700 transition-colors"
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