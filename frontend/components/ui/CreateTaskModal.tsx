import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, Plus, Zap, Brain, Target, Sparkles, 
  Calendar, Clock, User, Tag
} from 'lucide-react'
import { MotionButton } from './MotionButton'
import { TaskPriority, TaskStatus } from '../../lib/types'

type TaskFormData = {
  title: string
  description: string
  priority: TaskPriority
  status: TaskStatus
  dueDate: string
}

interface CreateTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onCreateTask: (task: TaskFormData) => void
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen,
  onClose,
  onCreateTask
}) => {
  const [mode, setMode] = useState<'manual' | 'ai'>('manual')
  const [isGenerating, setIsGenerating] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    assignee: '',
    tags: ''
  })
  
  const [aiPrompt, setAiPrompt] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('intermediate')
  const [suggestions, setSuggestions] = useState<any[]>([])

  const handleGenerateAI = async () => {
    setIsGenerating(true)
    
    try {
      const response = await fetch('http://localhost:8000/api/suggest_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_role: "developer",
          experience_level: experienceLevel,
          context: aiPrompt || "Generate task suggestions for onboarding"
        })
      })
      
      const data = await response.json()
      
      if (data.task_suggestions) {
        const suggestions = data.task_suggestions.slice(0, 3).map((task: any, index: number) => ({
          id: `suggestion-${index}`,
          title: task.title || task,
          description: task.description || `AI-generated task based on ${experienceLevel} level`,
          priority: task.priority || 'medium',
          difficulty: task.difficulty || experienceLevel,
          estimatedTime: task.estimatedTime || '2-3 hours',
          skills: task.skills || ['React', 'JavaScript'],
          aiGenerated: true
        }))
        setSuggestions(suggestions)
      } else {
        
        setSuggestions([
          {
            id: 'demo-1',
            title: 'Implement User Authentication Flow',
            description: 'Create login/logout functionality with JWT tokens',
            priority: 'high',
            difficulty: experienceLevel,
            estimatedTime: '4-6 hours',
            skills: ['React', 'Authentication', 'JWT'],
            aiGenerated: true
          },
          {
            id: 'demo-2', 
            title: 'Set up Unit Testing Framework',
            description: 'Configure Jest and write initial test cases',
            priority: 'medium',
            difficulty: experienceLevel,
            estimatedTime: '2-3 hours',
            skills: ['Jest', 'Testing', 'JavaScript'],
            aiGenerated: true
          }
        ])
      }
    } catch (error) {
      console.error('AI task generation failed:', error)
     
      setSuggestions([
        {
          id: 'fallback-1',
          title: 'Learn React Hooks Fundamentals',
          description: 'Master useState, useEffect, and custom hooks',
          priority: 'medium',
          difficulty: experienceLevel,
          estimatedTime: '3-4 hours',
          skills: ['React', 'Hooks', 'JavaScript'],
          aiGenerated: true
        }
      ])
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCreateManual = () => {
    const taskData: TaskFormData = {
      title: formData.title,
      description: formData.description,
      priority: formData.priority as TaskPriority,
      dueDate: formData.dueDate,
      status: 'todo'
    }

    onCreateTask(taskData)
    onClose()
    resetForm()
  }
  const handleSelectAISuggestion = (suggestion: any) => {
    const taskData: TaskFormData = {
      title: suggestion.title,
      description: suggestion.description,
      priority: suggestion.priority || 'medium',
      dueDate: formData.dueDate || new Date().toISOString().split('T')[0], // default to today
      status: 'todo'
    }

    onCreateTask(taskData)
    onClose()
    resetForm()
  }
  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      dueDate: '',
      assignee: '',
      tags: ''
    })
    setAiPrompt('')
    setSuggestions([])
    setMode('manual')
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          className="bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
        >
          
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <Plus className="w-6 h-6 mr-2 text-blue-600" />
              Create New Task
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X className="w-6 h-6" />
            </button>
          </div>

          
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setMode('manual')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  mode === 'manual' 
                    ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Plus className="w-4 h-4" />
                <span>Manual Creation</span>
              </button>
              <button
                onClick={() => setMode('ai')}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  mode === 'ai' 
                    ? 'bg-orange-100 text-orange-700 border border-orange-200' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Brain className="w-4 h-4" />
                <span>AI Generation</span>
              </button>
            </div>
          </div>

          <div className="max-h-[60vh] overflow-y-auto">
            {mode === 'manual' ? (
            
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Task Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Enter task title..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Describe the task..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Priority
                    </label>
                    <select
                      value={formData.priority}
                      onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Due Date
                    </label>
                    <input
                      type="date"
                      value={formData.dueDate}
                      onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            ) : (
              
              <div className="p-6 space-y-4">
                <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4 border border-orange-200">
                  <div className="flex items-center space-x-2 mb-3">
                    <Sparkles className="w-5 h-5 text-orange-600" />
                    <h3 className="font-medium text-orange-900">AI Task Generation</h3>
                  </div>
                  <p className="text-sm text-orange-700">
                    Let our AI Task Agent generate personalized task suggestions based on your experience level and goals.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level
                  </label>
                  <select
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What would you like to work on? (Optional)
                  </label>
                  <textarea
                    value={aiPrompt}
                    onChange={(e) => setAiPrompt(e.target.value)}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder="e.g., Learn React hooks, improve testing skills, work on authentication..."
                  />
                </div>

                <MotionButton
                  onClick={handleGenerateAI}
                  disabled={isGenerating}
                  className="w-full bg-orange-600 text-white py-3 rounded-lg hover:bg-orange-700 disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Generating AI Tasks...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Generate AI Task Suggestions</span>
                    </>
                  )}
                </MotionButton>

              
                {suggestions.length > 0 && (
                  <div className="space-y-3">
                    <h4 className="font-medium text-gray-900 flex items-center">
                      <Target className="w-4 h-4 mr-2 text-orange-600" />
                      AI Generated Suggestions
                    </h4>
                    {suggestions.map((suggestion, index) => (
                      <motion.div
                        key={suggestion.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="bg-gray-50 rounded-lg p-4 border border-gray-200"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h5 className="font-medium text-gray-900 mb-1">{suggestion.title}</h5>
                            <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                            <div className="flex items-center space-x-3 text-xs text-gray-500">
                              <span>📊 {suggestion.difficulty}</span>
                              <span>⏱️ {suggestion.estimatedTime}</span>
                              <span className={`px-2 py-1 rounded ${
                                suggestion.priority === 'high' ? 'bg-red-100 text-red-700' :
                                suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                              }`}>
                                {suggestion.priority}
                              </span>
                            </div>
                            {suggestion.skills && (
                              <div className="flex flex-wrap gap-1 mt-2">
                                {suggestion.skills.map((skill: string, skillIndex: number) => (
                                  <span key={skillIndex} className="bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                          <MotionButton
                            onClick={() => handleSelectAISuggestion(suggestion)}
                            className="bg-orange-600 text-white px-3 py-1 rounded text-sm hover:bg-orange-700 ml-3"
                          >
                            Select
                          </MotionButton>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

         
          {mode === 'manual' && (
            <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200">
              <MotionButton
                onClick={onClose}
                variant="ghost"
                className="text-gray-600 hover:text-gray-800"
              >
                Cancel
              </MotionButton>
              <MotionButton
                onClick={handleCreateManual}
                disabled={!formData.title.trim()}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                Create Task
              </MotionButton>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  )
}