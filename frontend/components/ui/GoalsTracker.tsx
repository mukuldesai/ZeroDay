import React from 'react'
import { Target, CheckSquare } from 'lucide-react'

interface Goal {
  task: string
  completed: boolean
}

interface GoalsTrackerProps {
  goals: Goal[]
  title?: string
}

export const GoalsTracker: React.FC<GoalsTrackerProps> = ({ 
  goals, 
  title = "Today's Goals" 
}) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <Target className="w-5 h-5 mr-2 text-red-500" />
        {title}
      </h3>
      <div className="space-y-3">
        {goals.map((goal, index) => (
          <div key={index} className="flex items-center space-x-3">
            <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
              goal.completed ? 'bg-green-500' : 'bg-gray-300'
            }`}>
              {goal.completed && <CheckSquare className="w-2.5 h-2.5 text-white" />}
            </div>
            <span className={`text-sm ${
              goal.completed ? 'text-gray-500 line-through' : 'text-gray-900'
            }`}>
              {goal.task}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}