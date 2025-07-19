import { useState, useEffect, useCallback } from 'react'
import { Task, TaskFilters, TaskStatus, AgentType, TaskPriority } from '../types'
import { useDemo } from './useDemo'
import { demoAPI } from '../api/demoAPI'


type TaskFormData = {
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate: string;
};

export interface TaskStats {
  total: number
  completed: number
  inProgress: number
  todo: number
  completionRate: number
  avgCompletionTime: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useTasks() {
  const { isDemoMode, selectedScenario } = useDemo()
  const [allTasks, setAllTasks] = useState<Task[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [filters, setFilters] = useState<TaskFilters>({
    status: [],
    priority: [],
    difficulty: [],
    category: [],
    assignee: [],
    search: ''
  })
  
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'kanban'>('grid')
  const [sortBy, setSortBy] = useState<string>('created')
  const [searchQuery, setSearchQuery] = useState('')
  
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<TaskStats>({
    total: 0,
    completed: 0,
    inProgress: 0,
    todo: 0,
    completionRate: 0,
    avgCompletionTime: '0h'
  })

  const fetchTasks = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      if (isDemoMode && selectedScenario) {
        const demoTasks = await demoAPI.getTasks(selectedScenario)
        const convertedTasks: Task[] = demoTasks.map((task: any) => ({
          id: task.id.toString(),
          title: task.title,
          description: task.description,
          status: task.status as TaskStatus,
          priority: task.priority,
          difficulty: 'medium',
          category: 'Demo Project',
          estimatedTime: '2h',
          skillsRequired: task.tags || [],
          assignedAgent: 'task' as AgentType,
          prerequisites: [],
          tags: task.tags || [],
          dueDate: task.deadline ? new Date(task.deadline) : undefined,
          createdAt: new Date(),
          updatedAt: new Date(),
          assignee: task.assignee
        }))
        
        setAllTasks(convertedTasks)
        setTasks(convertedTasks)
        setCategories(['Demo Project'])
        return
      }

      const taskResponse = await fetch(`${API_BASE}/api/suggest_task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_role: 'developer',
          skill_level: 'intermediate',
          time_available: '2-4 hours'
        })
      })

      if (!taskResponse.ok) {
        throw new Error(`API Error: ${taskResponse.status}`)
      }

      const data = await taskResponse.json()
      const backendTasks = data.tasks || []
      
      const convertedTasks: Task[] = backendTasks.map((task: any, index: number) => ({
        id: task.id || `task_${index}`,
        title: task.title,
        description: task.description,
        status: 'todo' as TaskStatus,
        priority: task.priority || 'medium',
        difficulty: task.difficulty || 'medium',
        category: task.category || 'General',
        estimatedTime: task.estimated_time || '2h',
        skillsRequired: task.skills_required || [],
        assignedAgent: 'task' as AgentType,
        prerequisites: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        tags: ['backend-generated']
      }))
      
      setAllTasks(convertedTasks)
      setTasks(convertedTasks)
      
      const uniqueCategories = Array.from(new Set(convertedTasks.map(task => task.category)))
      setCategories(uniqueCategories)
      
    } catch (err) {
      console.error('Error fetching tasks:', err)
      setError(err instanceof Error ? err.message : 'Failed to load tasks')
      setAllTasks([])
      setTasks([])
      setCategories([])
    } finally {
      setIsLoading(false)
    }
  }, [isDemoMode, selectedScenario])

  const calculateStats = (taskList: Task[]): TaskStats => {
    const total = taskList.length
    const completed = taskList.filter(t => t.status === 'completed').length
    const inProgress = taskList.filter(t => t.status === 'in-progress').length
    const todo = taskList.filter(t => t.status === 'todo').length
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0
    
    const completedTasks = taskList.filter(t => t.status === 'completed' && t.completedAt && t.createdAt)
    const avgTime = completedTasks.length > 0 
      ? completedTasks.reduce((sum, task) => {
          const timeDiff = new Date(task.completedAt!).getTime() - new Date(task.createdAt).getTime()
          return sum + timeDiff
        }, 0) / completedTasks.length
      : 0
    
    const avgHours = Math.round(avgTime / (1000 * 60 * 60) * 10) / 10
    const avgCompletionTime = `${avgHours}h`

    return {
      total,
      completed,
      inProgress,
      todo,
      completionRate,
      avgCompletionTime
    }
  }

  const generateKanbanColumns = (taskList: Task[]): Record<string, Task[]> => ({
    todo: taskList.filter(t => t.status === 'todo'),
    'in-progress': taskList.filter(t => t.status === 'in-progress'),
    review: taskList.filter(t => t.status === 'review'),
    completed: taskList.filter(t => t.status === 'completed'),
  })

  const applyFilters = (taskList: Task[], currentFilters: TaskFilters, search: string): Task[] => {
    return taskList.filter(task => {
      if (search && !task.title.toLowerCase().includes(search.toLowerCase()) && 
          !task.description.toLowerCase().includes(search.toLowerCase())) {
        return false
      }

      if (currentFilters.status.length > 0 && !currentFilters.status.includes(task.status)) {
        return false
      }

      if (currentFilters.priority.length > 0 && !currentFilters.priority.includes(task.priority)) {
        return false
      }

      if (currentFilters.difficulty.length > 0 && !currentFilters.difficulty.includes(task.difficulty)) {
        return false
      }

      if (currentFilters.category.length > 0 && !currentFilters.category.includes(task.category)) {
        return false
      }

      if (currentFilters.assignee.length > 0 && task.assignee && !currentFilters.assignee.includes(task.assignee)) {
        return false
      }

      return true
    })
  }
    const createTask = async (formData: TaskFormData): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE}/api/create_task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          user_id: 'demo_user',
          assignee: 'You'
        })
      })

      if (!response.ok) throw new Error('Failed to create task')

      const newTask: Task = await response.json()

      const updatedTasks = [...allTasks, newTask]
      setAllTasks(updatedTasks)
      setTasks(applyFilters(updatedTasks, filters, searchQuery))
    } catch (err) {
      console.error('Task creation failed:', err)
    }
  }

  const updateFilters = (newFilters: Partial<TaskFilters>) => {
    const updatedFilters = { ...filters, ...newFilters }
    setFilters(updatedFilters)
    const filtered = applyFilters(allTasks, updatedFilters, searchQuery)
    setTasks(filtered)
  }

  const setSearchQueryWithFilter = (query: string) => {
    setSearchQuery(query)
    const filtered = applyFilters(allTasks, filters, query)
    setTasks(filtered)
  }

  const updateFilter = (filterKey: keyof TaskFilters, values: string[]) => {
    const updatedFilters = { ...filters, [filterKey]: values }
    setFilters(updatedFilters)
    const filtered = applyFilters(allTasks, updatedFilters, searchQuery)
    setTasks(filtered)
  }

  const addTask = async (taskData: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>): Promise<void> => {
    const now = new Date()
    const newTask: Task = {
      ...taskData,
      id: `task_${Date.now()}`,
      createdAt: now,
      updatedAt: now
    }
    
    const updatedTasks = [...allTasks, newTask]
    setAllTasks(updatedTasks)
    setTasks(applyFilters(updatedTasks, filters, searchQuery))
  }

  const updateTask = async (taskId: string, updates: Partial<Task>): Promise<void> => {
    const now = new Date()
    const updatedTasks = allTasks.map(task => 
      task.id === taskId 
        ? { 
            ...task, 
            ...updates, 
            updatedAt: now,
            ...(updates.status === 'completed' ? { completedAt: now } : {})
          }
        : task
    )
    
    setAllTasks(updatedTasks)
    setTasks(applyFilters(updatedTasks, filters, searchQuery))
  }
  
  const deleteTask = async (taskId: string): Promise<void> => {
    const updatedTasks = allTasks.filter(task => task.id !== taskId)
    setAllTasks(updatedTasks)
    setTasks(applyFilters(updatedTasks, filters, searchQuery))
  }

  const handleStatusChange = (taskId: string, newStatus: TaskStatus) => {
    updateTask(taskId, { status: newStatus })
  }

  const handleEdit = (task: Task) => {
    console.log('Edit task:', task)
  }

  const handleDelete = (taskId: string) => {
    deleteTask(taskId)
  }

  const handleDragEnd = (result: any) => {
    if (!result.destination) return

    const { source, destination } = result
    if (source.droppableId === destination.droppableId) return

    const taskId = result.draggableId
    const newStatus = destination.droppableId as TaskStatus
    handleStatusChange(taskId, newStatus)
  }

  const refreshTasks = () => {
    fetchTasks()
  }

  const activeFiltersCount = Object.values(filters).reduce((count, filterArray) => {
    if (Array.isArray(filterArray)) {
      return count + filterArray.length
    }
    return count + (filterArray ? 1 : 0)
  }, 0)

  useEffect(() => {
    setStats(calculateStats(tasks))
  }, [tasks])

  useEffect(() => {
    const filtered = applyFilters(allTasks, filters, searchQuery)
    setTasks(filtered)
  }, [allTasks, filters, searchQuery])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  return {
    tasks,
    allTasks,
    categories,
    filters,
    stats,
    viewMode,
    setViewMode,
    sortBy,
    setSortBy,
    searchQuery,
    setSearchQuery: setSearchQueryWithFilter,
    kanbanColumns: generateKanbanColumns(tasks),
    activeFiltersCount,
    taskStats: stats,
    isLoading,
    error,
    updateFilters,
    updateFilter,
    addTask,
    updateTask,
    deleteTask,
    refreshTasks,
    fetchTasks,
    createTask, 
    handleStatusChange,
    handleEdit,
    handleDelete,
    handleDragEnd
  }
}