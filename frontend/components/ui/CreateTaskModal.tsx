import React, { useState } from 'react'
import { XCircle } from 'lucide-react'
import { Modal } from './Modal'
import { MotionButton } from './MotionButton'
import { toast } from 'react-hot-toast'

interface CreateTaskModalProps {
  isOpen: boolean
  onClose: () => void
  onCreateTask: () => void
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen,
  onClose,
  onCreateTask
}) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    difficulty: 'medium',
    category: 'Frontend',
    estimatedTime: '',
    skillsRequired: ''
  })

  const handleSubmit = () => {
    if (!formData.title.trim()) {
      toast.error('Please enter a task title')
      return
    }
    
    onCreateTask()
    onClose()
    toast.success('Task created successfully!')
    
    // Reset form
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      difficulty: 'medium',
      category: 'Frontend',
      estimatedTime: '',
      skillsRequired: ''
    })
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create New Task"
      size="lg"
    >
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Task Title</label>
          <input
            type="text"
            placeholder="Enter task title..."
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
          <textarea
            rows={4}
            placeholder="Describe the task..."
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
            <select 
              value={formData.priority}
              onChange={(e) => handleChange('priority', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
            <select 
              value={formData.difficulty}
              onChange={(e) => handleChange('difficulty', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select 
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            >
              <option value="Frontend">Frontend</option>
              <option value="Backend">Backend</option>
              <option value="DevOps">DevOps</option>
              <option value="Testing">Testing</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Estimated Time</label>
            <input
              type="text"
              placeholder="e.g., 2 hours"
              value={formData.estimatedTime}
              onChange={(e) => handleChange('estimatedTime', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Skills Required</label>
          <input
            type="text"
            placeholder="e.g., React, TypeScript, API Design"
            value={formData.skillsRequired}
            onChange={(e) => handleChange('skillsRequired', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          />
        </div>
        
        <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
          <MotionButton
            onClick={onClose}
            variant="ghost"
            className="px-6 py-2 text-gray-600 hover:text-gray-800"
          >
            Cancel
          </MotionButton>
          <MotionButton
            onClick={handleSubmit}
            className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-6 py-2 rounded-lg hover:shadow-lg transition-all duration-300"
          >
            Create Task
          </MotionButton>
        </div>
      </div>
    </Modal>
  )
}