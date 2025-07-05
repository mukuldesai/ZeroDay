import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckCircle, Square, PlayCircle, PauseCircle, ArrowRight, 
  MoreHorizontal, Edit3, Trash2, Share2, CheckSquare, FileText, Star
} from 'lucide-react'
import { Task } from '../../lib/types'
import { AgentBadge } from './AgentBadge'
import { StatusBadge } from './StatusBadge'
import { ProgressBar } from './ProgressBar'
import { MotionButton } from './MotionButton'
import { formatTimeAgo } from '../../lib/utils/time'

interface TaskCardProps {
  task: Task
  onStatusChange: (id: string, status: Task['status']) => void
  onEdit: (task: Task) => void
  onDelete: (id: string) => void
}

export const TaskCard: React.FC<TaskCardProps> = ({ 
  task, 
  onStatusChange, 
  onEdit, 
  onDelete 
}) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [isTimerRunning, setIsTimerRunning] = useState(false)

  const getDifficultyIcon = () => {
    switch (task.difficulty) {
      case 'easy': return <span className="text-green-500">●</span>
      case 'medium': return <span className="text-yellow-500">●●</span>
      case 'hard': return <span className="text-red-500">●●●</span>
      default: return <span className="text-gray-500">●</span>
    }
  }

  const toggleTaskStatus = () => {
    const statusOrder: Task['status'][] = ['todo', 'in-progress', 'review', 'completed']
    const currentIndex = statusOrder.indexOf(task.status)
    const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length]
    onStatusChange(task.id, nextStatus)
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.01, y: -2 }}
      className="bg-white rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 overflow-hidden"
    >
      {/* Card Header */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-3 flex-1">
            <MotionButton
              onClick={toggleTaskStatus}
              variant="ghost"
              size="sm"
              className="mt-1"
            >
              {task.status === 'completed' ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <Square className="w-5 h-5 text-gray-400 hover:text-indigo-500" />
              )}
            </MotionButton>
            <div className="flex-1">
              <h3 className={`font-semibold text-gray-900 mb-2 ${task.status === 'completed' ? 'line-through text-gray-500' : ''}`}>
                {task.title}
              </h3>
              <p className="text-sm text-gray-600 mb-3">{task.description}</p>
              
              {/* Progress Bar */}
              <ProgressBar 
                progress={task.progress} 
                color="indigo" 
                className="mb-3"
              />
            </div>
          </div>
          
          <div className="flex items-center space-x-2 ml-4">
            <MotionButton
              onClick={() => setIsTimerRunning(!isTimerRunning)}
              variant="ghost"
              size="sm"
              className={`${
                isTimerRunning 
                  ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                  : 'bg-green-100 text-green-600 hover:bg-green-200'
              }`}
            >
              {isTimerRunning ? <PauseCircle className="w-4 h-4" /> : <PlayCircle className="w-4 h-4" />}
            </MotionButton>
            <MotionButton variant="ghost" size="sm">
              <MoreHorizontal className="w-4 h-4" />
            </MotionButton>
          </div>
        </div>

        {/* Task Metadata */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <StatusBadge type="status" value={task.status} size="sm" />
          <StatusBadge type="priority" value={task.priority} size="sm" />
          <div className="flex items-center space-x-1 text-xs text-gray-600">
            {getDifficultyIcon()}
            <span>{task.difficulty}</span>
          </div>
          <AgentBadge agent={task.assignedAgent} size="sm" showIcon={false} />
          <div className="flex items-center space-x-1 text-xs text-gray-600">
            <span>{task.estimatedTime}</span>
          </div>
        </div>

        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {task.tags.map((tag, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
              {tag}
            </span>
          ))}
        </div>

        {/* Skills Required */}
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2">Skills Required:</div>
          <div className="flex flex-wrap gap-1">
            {task.skillsRequired.map((skill, index) => (
              <span key={index} className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs rounded border border-indigo-200">
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Expand/Collapse Button */}
        <MotionButton
          onClick={() => setIsExpanded(!isExpanded)}
          variant="ghost"
          className="w-full bg-gray-50 text-gray-600 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center space-x-2"
        >
          <span className="text-sm">{isExpanded ? 'Show Less' : 'Show More'}</span>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ArrowRight className="w-4 h-4 rotate-90" />
          </motion.div>
        </MotionButton>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-gray-100 bg-gray-50"
          >
            <div className="p-6 space-y-4">
              {/* Subtasks */}
              <div>
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <CheckSquare className="w-4 h-4 mr-2" />
                  Subtasks ({task.subtasks.filter(st => st.completed).length}/{task.subtasks.length})
                </h4>
                <div className="space-y-2">
                  {task.subtasks.map((subtask) => (
                    <div key={subtask.id} className="flex items-center space-x-3 p-3 bg-white rounded-lg">
                      <input
                        type="checkbox"
                        checked={subtask.completed}
                        onChange={() => {}}
                        className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                      />
                      <span className={`flex-1 text-sm ${subtask.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                        {subtask.title}
                      </span>
                      <span className="text-xs text-gray-500">{subtask.estimatedTime}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Prerequisites */}
              {task.prerequisites.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Prerequisites:</h4>
                  <ul className="space-y-1">
                    {task.prerequisites.map((prereq, index) => (
                      <li key={index} className="text-sm text-gray-600 flex items-center">
                        <CheckCircle className="w-3 h-3 text-green-500 mr-2" />
                        {prereq}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Feedback */}
              {task.feedback && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="font-medium text-green-900">Feedback</span>
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3 h-3 ${i < task.feedback!.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
                        />
                      ))}
                    </div>
                  </div>
                  <p className="text-sm text-green-700">{task.feedback.comment}</p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <MotionButton
                    onClick={() => onEdit(task)}
                    variant="ghost"
                    size="sm"
                    className="bg-blue-100 text-blue-600 hover:bg-blue-200"
                  >
                    <Edit3 className="w-3 h-3 mr-1" />
                    Edit
                  </MotionButton>
                  <MotionButton
                    variant="ghost"
                    size="sm"
                    className="bg-gray-100 text-gray-600 hover:bg-gray-200"
                  >
                    <Share2 className="w-3 h-3 mr-1" />
                    Share
                  </MotionButton>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    Updated {formatTimeAgo(task.updatedAt)}
                  </span>
                  <MotionButton
                    onClick={() => onDelete(task.id)}
                    variant="ghost"
                    size="sm"
                    className="text-red-400 hover:text-red-600"
                  >
                    <Trash2 className="w-3 h-3" />
                  </MotionButton>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}