import React from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, Square } from 'lucide-react'
import { Task } from '../../lib/types'
import { StatusBadge } from './StatusBadge'
import { MotionButton } from './MotionButton'

interface TaskListViewProps {
  tasks: Task[]
  onStatusChange: (id: string, status: Task['status']) => void
  userId?: string
}

export const TaskListView: React.FC<TaskListViewProps> = ({ 
  tasks, 
  onStatusChange,
  userId 
}) => {
  const userTasks = userId 
    ? tasks.filter(task => !task.userId || task.userId === userId)
    : tasks

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      <div className="p-4 border-b border-gray-200 bg-gray-50">
        <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-600">
          <div className="col-span-4">Task</div>
          <div className="col-span-2">Status</div>
          <div className="col-span-2">Priority</div>
          <div className="col-span-2">Progress</div>
          <div className="col-span-2">Due Date</div>
        </div>
      </div>
      <div className="divide-y divide-gray-200">
        {userTasks.map((task, index) => {
          const userOwnsTask = !userId || task.userId === userId
          
          return (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className={`p-4 hover:bg-gray-50 transition-colors ${
                !userOwnsTask ? 'opacity-75' : ''
              }`}
            >
              <div className="grid grid-cols-12 gap-4 items-center">
                <div className="col-span-4">
                  <div className="flex items-center space-x-3">
                    <MotionButton
                      onClick={() => onStatusChange(task.id, 'completed')}
                      variant="ghost"
                      size="sm"
                      disabled={!userOwnsTask}
                    >
                      {task.status === 'completed' ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <Square className="w-5 h-5 text-gray-400 hover:text-orange-500" />
                      )}
                    </MotionButton>
                    <div>
                      <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                        {task.title}
                      </h4>
                      <p className="text-sm text-gray-600 truncate">{task.description}</p>
                    </div>
                  </div>
                </div>
                <div className="col-span-2">
                  <StatusBadge type="status" value={task.status} size="sm" />
                </div>
                <div className="col-span-2">
                  <StatusBadge type="priority" value={task.priority} size="sm" />
                </div>
                <div className="col-span-2">
                  <div className="flex items-center space-x-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-gradient-to-r from-orange-500 to-red-500"
                        style={{ width: `${task.progress}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600">{task.progress}%</span>
                  </div>
                </div>
                <div className="col-span-2">
                  <span className="text-sm text-gray-600">
                    {task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'No due date'}
                  </span>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}