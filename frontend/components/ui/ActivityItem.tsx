import React from 'react'
import { motion } from 'framer-motion'
import { MessageSquare, CheckSquare, BookOpen, Code, Activity } from 'lucide-react'
import { ActivityItem as ActivityItemType } from '../../lib/types'
import { formatTimeAgo } from '../../lib/utils/time'

interface ActivityItemProps {
  activity: ActivityItemType
  index?: number
  userId?: string
}

export const ActivityItem: React.FC<ActivityItemProps> = ({ 
  activity, 
  index = 0,
  userId 
}) => {
  const userOwnsActivity = !userId || activity.userId === userId

  const getActivityIcon = () => {
    switch (activity.type) {
      case 'chat': return <MessageSquare className="w-4 h-4" />
      case 'task': return <CheckSquare className="w-4 h-4" />
      case 'learning': return <BookOpen className="w-4 h-4" />
      case 'code': return <Code className="w-4 h-4" />
      default: return <Activity className="w-4 h-4" />
    }
  }

  const getStatusColor = () => {
    switch (activity.status) {
      case 'completed': return 'bg-green-100 text-green-700'
      case 'in-progress': return 'bg-yellow-100 text-yellow-700'
      case 'pending': return 'bg-gray-100 text-gray-700'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ x: 5 }}
      className={`flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors cursor-pointer ${
        !userOwnsActivity ? 'opacity-75' : ''
      }`}
    >
      <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600 flex-shrink-0">
        {getActivityIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <h4 className="font-medium text-gray-900 truncate">{activity.title}</h4>
        <p className="text-sm text-gray-600 truncate">{activity.description}</p>
        <div className="flex items-center space-x-2 mt-1">
          <span className="text-xs text-gray-500">{formatTimeAgo(new Date(activity.timestamp))}
</span>
          {activity.agent && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
              {activity.agent}
            </span>
          )}
          {activity.status && (
            <span className={`text-xs px-2 py-0.5 rounded ${getStatusColor()}`}>
              {activity.status}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  )
}