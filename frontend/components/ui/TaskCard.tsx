import React from 'react'
import { motion } from 'framer-motion'
import { 
  Calendar, Clock, User, MoreVertical, CheckCircle, 
  AlertTriangle, Target, Brain, Zap, Star
} from 'lucide-react'
import { MotionButton } from './MotionButton'
import { Task, TaskStatus } from '@/lib/types'


interface TaskCardProps {
  task: Task
  onStatusChange: (taskId: string, status: TaskStatus) => void
  onEdit: (task: Task) => void
  onDelete: (taskId: string) => void
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onStatusChange,
  onEdit,
  onDelete
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'in-progress':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'suggested':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700'
      case 'medium':
        return 'bg-yellow-100 text-yellow-700'
      default:
        return 'bg-green-100 text-green-700'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4" />
      case 'in-progress':
        return <Clock className="w-4 h-4" />
      case 'suggested':
        return <Target className="w-4 h-4" />
      default:
        return <AlertTriangle className="w-4 h-4" />
    }
  }

  return (
    <motion.div
      layout
      whileHover={{ scale: 1.02 }}
      className={`bg-white rounded-xl shadow-sm border p-6 hover:shadow-md transition-all duration-300 ${
        task.aiGenerated ? 'border-orange-200 bg-gradient-to-br from-white to-orange-50' : 'border-gray-200'
      }`}
    >
    
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="font-semibold text-gray-900 text-sm leading-tight">
              {task.title}
            </h3>
            {task.aiGenerated && (
              <div className="flex items-center space-x-1 bg-orange-100 text-orange-700 px-2 py-1 rounded-full text-xs">
                <Brain className="w-3 h-3" />
                <span>AI</span>
              </div>
            )}
          </div>
          
        
          {task.aiGenerated && task.confidence && (
            <div className="flex items-center space-x-1 mb-2">
              <Star className="w-3 h-3 text-yellow-500" />
              <span className="text-xs text-gray-600">
                {Math.round(task.confidence * 100)}% match accuracy
              </span>
            </div>
          )}
        </div>
        
        <MotionButton
          variant="ghost"
          size="sm"
          className="text-gray-400 hover:text-gray-600"
        >
          <MoreVertical className="w-4 h-4" />
        </MotionButton>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {task.description}
      </p>

     
      {task.skills && task.skills.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {task.skills.slice(0, 3).map((skill, index) => (
            <span
              key={index}
              className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
            >
              {skill}
            </span>
          ))}
          {task.skills.length > 3 && (
            <span className="text-xs text-gray-500">
              +{task.skills.length - 3} more
            </span>
          )}
        </div>
      )}

    
      <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
        <div className="flex items-center space-x-3">
          {task.difficulty && (
            <span className="flex items-center space-x-1">
              <Target className="w-3 h-3" />
              <span>{task.difficulty}</span>
            </span>
          )}
          {task.estimatedTime && (
            <span className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>{task.estimatedTime}</span>
            </span>
          )}
        </div>
        
        <span className={`px-2 py-1 rounded-full text-xs ${getPriorityColor(task.priority)}`}>
          {task.priority}
        </span>
      </div>

     
      <div className="flex items-center justify-between">
        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getStatusColor(task.status)}`}>
          {getStatusIcon(task.status)}
          <span className="capitalize">{task.status.replace('-', ' ')}</span>
        </div>

        <div className="flex items-center space-x-2">
          {task.status === 'suggested' && task.aiGenerated && (
            <MotionButton
              onClick={() => onStatusChange(task.id, 'todo')}
              className="bg-orange-600 text-white px-3 py-1 rounded text-xs hover:bg-orange-700 transition-colors"
            >
              Accept
            </MotionButton>
          )}
          
          {task.status === 'todo' && (
            <MotionButton
              onClick={() => onStatusChange(task.id, 'in-progress')}
              className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-colors"
            >
              Start
            </MotionButton>
          )}
          
          {task.status === 'in-progress' && (
            <MotionButton
              onClick={() => onStatusChange(task.id, 'completed')}
              className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700 transition-colors"
            >
              Complete
            </MotionButton>
          )}
        </div>
      </div>

    
      {task.aiGenerated && (
        <div className="mt-4 pt-4 border-t border-orange-200">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-1 text-orange-600">
              <Zap className="w-3 h-3" />
              <span>Generated by Task Agent</span>
            </div>
            <span className="text-gray-500">
              {new Date(task.createdAt).toLocaleDateString()}
            </span>
          </div>
        </div>
      )}
    </motion.div>
  )
}