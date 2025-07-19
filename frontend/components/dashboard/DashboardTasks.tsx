import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Target, CheckSquare, Clock, TrendingUp, Zap, RefreshCw, Play } from 'lucide-react'
import Link from 'next/link'
import useSWR from 'swr'
import { Task } from '@/lib/types'


interface DashboardTasksProps {
  progressData: any[]
  stats: any
  userName: string
  isDemo: boolean
}


const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const fetcher = (url: string) => fetch(`${API_BASE}${url}`).then(res => res.json())
const postFetcher = ([url, body]: [string, any]) => fetch(`http://localhost:8000${url}`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body)
}).then(res => res.json())

export default function DashboardTasks({ progressData, stats, userName, isDemo }: DashboardTasksProps) {
  const [experienceLevel, setExperienceLevel] = useState('intermediate')
  const [userRole, setUserRole] = useState('developer')


  const { data: taskSuggestions, mutate: refreshTasks } = useSWR(
    ['/api/suggest_task', { user_role: userRole, experience_level: experienceLevel }],
    postFetcher,
    { refreshInterval: 60000 }
  )

  const { data: agentStatus } = useSWR('/agents', fetcher, { refreshInterval: 15000 })

 
  const aiGeneratedTasks = taskSuggestions?.task_suggestions || [
    {
      id: 1,
      title: "Implement React Hook for API State Management",
      difficulty: "intermediate",
      estimatedTime: "2-3 hours",
      skills: ["React", "TypeScript", "API Integration"],
      priority: "high",
      aiGenerated: true
    },
    {
      id: 2,
      title: "Create Unit Tests for Authentication Module",
      difficulty: "beginner",
      estimatedTime: "1-2 hours", 
      skills: ["Jest", "Testing", "JavaScript"],
      priority: "medium",
      aiGenerated: true
    }
  ]

  const taskStats = {
    totalTasks: aiGeneratedTasks.length + 3,
    completed: 5,
    inProgress: 2,
    aiGenerated: aiGeneratedTasks.length,
    averageCompletion: "1.8 hours"
  }

  const handleGenerateNewTask = async () => {
    await refreshTasks()
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-6"
    >
      
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Target className="w-7 h-7 mr-3 text-orange-600" />
            AI Task Management
          </h2>
          <p className="text-gray-600 mt-1">
            Personalized task suggestions powered by AI
            {isDemo && <span className="ml-2 text-blue-600">(Demo Mode)</span>}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select 
            value={experienceLevel}
            onChange={(e) => setExperienceLevel(e.target.value)}
            className="text-sm bg-gray-100 border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            onClick={handleGenerateNewTask}
            className="flex items-center space-x-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors"
          >
            <Zap className="w-4 h-4" />
            <span>Generate Task</span>
          </button>
        </div>
      </div>

    
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">AI Generated</p>
              <p className="text-2xl font-bold">{taskStats.aiGenerated}</p>
              <p className="text-orange-200 text-xs mt-1">Smart suggestions</p>
            </div>
            <Zap className="w-8 h-8 text-orange-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-green-500 to-green-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Completed</p>
              <p className="text-2xl font-bold">{taskStats.completed}</p>
              <p className="text-green-200 text-xs mt-1">+2 this week</p>
            </div>
            <CheckSquare className="w-8 h-8 text-green-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">In Progress</p>
              <p className="text-2xl font-bold">{taskStats.inProgress}</p>
              <p className="text-blue-200 text-xs mt-1">Active tasks</p>
            </div>
            <Clock className="w-8 h-8 text-blue-200" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-xl p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Avg Time</p>
              <p className="text-2xl font-bold">{taskStats.averageCompletion}</p>
              <p className="text-purple-200 text-xs mt-1">Per task</p>
            </div>
            <TrendingUp className="w-8 h-8 text-purple-200" />
          </div>
        </motion.div>
      </div>

     
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Target className="w-5 h-5 mr-2 text-orange-600" />
            Task Agent Status
          </h3>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              agentStatus?.task?.available ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}></div>
            <span className="text-sm text-gray-600">
              {agentStatus?.task?.available ? 'Active' : 'Offline'}
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-orange-50 rounded-lg p-4">
            <div className="text-orange-600 font-medium">Task Generation</div>
            <div className="text-2xl font-bold text-orange-700">Ready</div>
            <div className="text-sm text-orange-600">AI analyzing your skill level</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="text-blue-600 font-medium">Personalization</div>
            <div className="text-2xl font-bold text-blue-700">98%</div>
            <div className="text-sm text-blue-600">Match accuracy</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <div className="text-green-600 font-medium">Response Time</div>
            <div className="text-2xl font-bold text-green-700">1.1s</div>
            <div className="text-sm text-green-600">Average generation time</div>
          </div>
        </div>
      </div>

      
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Zap className="w-5 h-5 mr-2 text-yellow-500" />
            AI Generated Tasks
          </h3>
          <Link href="/tasks">
            <button className="flex items-center space-x-2 text-orange-600 hover:text-orange-700 font-medium">
              <span>View All Tasks</span>
              <TrendingUp className="w-4 h-4" />
            </button>
          </Link>
        </div>

        <div className="space-y-4">
          {aiGeneratedTasks.map((task: Task, index: number) => (
            <motion.div
              key={task.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gradient-to-r from-orange-50 to-yellow-50 border border-orange-200 rounded-lg p-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="font-medium text-gray-900">{task.title}</h4>
                    <span className="bg-orange-100 text-orange-700 text-xs px-2 py-1 rounded-full">
                      AI Generated
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      task.priority === 'high' ? 'bg-red-100 text-red-700' :
                      task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {task.priority}
                    </span>
                  </div>

                  <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                    <span>📊 {task.difficulty}</span>
                    <span>⏱️ {task.estimatedTime}</span>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    {task.skills?.map((skill: string, skillIndex: number) => (
                      <span key={skillIndex} className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded">
                        {skill}
                      </span>
                    ))}
                  </div>

                  <button className="flex items-center space-x-2 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition-colors">
                    <Play className="w-4 h-4" />
                    <span>Start</span>
                  </button>
                </div> 
              </div>   
            </motion.div>
          ))}

        </div>

        {aiGeneratedTasks.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Target className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="mb-2">No AI tasks generated yet</p>
            <button 
              onClick={handleGenerateNewTask}
              className="text-orange-600 hover:text-orange-700 font-medium"
            >
              Generate your first AI task →
            </button>
          </div>
        )}
      </div>
    </motion.div>
  
  )
}