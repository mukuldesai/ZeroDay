import React from 'react'
import { motion } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import { LearningPath } from '../../lib/types'
import { StatusBadge } from './StatusBadge'
import { ProgressBar } from './ProgressBar'
import { MotionButton } from './MotionButton'

interface LearningPathCardProps {
  path: LearningPath
  delay?: number
  userId?: string
}

export const LearningPathCard: React.FC<LearningPathCardProps> = ({ 
  path, 
  delay = 0,
  userId
}) => {
  const userOwnsPath = !userId || path.userId === userId

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      whileHover={{ scale: 1.02, y: -2 }}
      className={`bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 ${
        !userOwnsPath ? 'opacity-75' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-1">{path.title}</h3>
          <p className="text-sm text-gray-600">{path.description}</p>
        </div>
        <StatusBadge
          type="difficulty"
          value={path.difficulty}
          size="sm"
        />
      </div>

      <ProgressBar 
        progress={path.progress} 
        color="indigo" 
        className="mb-4"
      />

      <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
        <span>{path.completedModules}/{path.totalModules} modules</span>
        <span>{path.estimatedTime} remaining</span>
      </div>

      <MotionButton
        className="w-full bg-indigo-50 text-indigo-600 py-2 rounded-lg font-medium hover:bg-indigo-100 transition-colors flex items-center justify-center space-x-2"
        variant="ghost"
        disabled={!userOwnsPath}
      >
        <span>Continue Learning</span>
        <ArrowRight className="w-4 h-4" />
      </MotionButton>
    </motion.div>
  )
}