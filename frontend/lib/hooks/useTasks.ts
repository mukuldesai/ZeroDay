import { useState } from 'react'
import { Task, TaskFilter } from '../types'
import { useFilter } from './useFilter'
import { groupBy } from '../utils/array'
import { toast } from 'react-hot-toast'

export function useTasks(initialTasks: Task[]) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'kanban'>('grid')
  const [sortBy, setSortBy] = useState<'dueDate' | 'priority' | 'difficulty' | 'progress'>('dueDate')

  const initialFilters: TaskFilter = {
    status: [],
    priority: [],
    category: [],
    agent: [],
    difficulty: [] // ✅ required
    }

  const filterOptions = {
    searchKeys: ['title', 'description'] as (keyof Task)[],
    sortKey: sortBy as keyof Task,
    sortDirection: 'asc' as const,
    initialFilters // 
  }

  const {
    filteredData: filteredTasks,
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    removeFilter,
    clearFilters,
    activeFiltersCount
  } = useFilter<Task>(tasks, filterOptions)

  const kanbanColumns = {
    todo: filteredTasks.filter(task => task.status === 'todo'),
    'in-progress': filteredTasks.filter(task => task.status === 'in-progress'),
    review: filteredTasks.filter(task => task.status === 'review'),
    completed: filteredTasks.filter(task => task.status === 'completed')
  }

  const handleStatusChange = (id: string, status: Task['status']) => {
    setTasks(prev =>
      prev.map(task =>
        task.id === id
          ? {
              ...task,
              status,
              updatedAt: new Date(),
              ...(status === 'completed'
                ? { completedAt: new Date(), progress: 100 }
                : {})
            }
          : task
      )
    )

    if (status === 'completed') {
      toast.success('Task completed! Great job! 🎉')
    }
  }

  const handleEdit = (task: Task) => {
    toast.success('Edit functionality coming soon!')
  }

  const handleDelete = (id: string) => {
    setTasks(prev => prev.filter(task => task.id !== id))
    toast.success('Task deleted successfully!')
  }

  const handleDragEnd = (result: any) => {
    const { destination, source, draggableId } = result
    if (!destination) return

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) return

    const draggedTask = tasks.find(task => task.id === draggableId)
    if (!draggedTask) return

    const destinationStatus = destination.droppableId as Task['status']

    setTasks(prev =>
      prev.map(task =>
        task.id === draggableId
          ? {
              ...task,
              status: destinationStatus,
              updatedAt: new Date(),
              ...(destinationStatus === 'completed'
                ? { completedAt: new Date(), progress: 100 }
                : {})
            }
          : task
      )
    )

    toast.success(`Task moved to ${destinationStatus.replace('-', ' ')}!`)
  }

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    pending: tasks.filter(t => t.status === 'todo').length,
    avgCompletionTime: '3.2 hours'
  }

  return {
    tasks,
    filteredTasks,
    kanbanColumns,
    viewMode,
    setViewMode,
    sortBy,
    setSortBy,
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    removeFilter,
    clearFilters,
    activeFiltersCount,
    taskStats,
    handleStatusChange,
    handleEdit,
    handleDelete,
    handleDragEnd
  }
}
