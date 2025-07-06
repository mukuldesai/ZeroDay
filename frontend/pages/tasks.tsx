'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  CheckSquare, Plus, Lightbulb, MessageSquare, GitBranch, TrendingUp, Download
} from 'lucide-react'
import Link from 'next/link'

// Data
import { mockTasks } from '../lib/data/taskData'

// Hooks
import { useTasks } from '../lib/hooks/useTasks'

// Components
import { NavigationHeader } from '../components/layout/NavigationHeader'
import { StatsCard } from '../components/ui/StatsCard'
import { TaskFilters } from '../components/ui/TaskFilters'
import { ViewModeToggle } from '../components/ui/ViewModeToggle'
import { TaskCard } from '../components/ui/TaskCard'
import { TaskListView } from '../components/ui/TaskListView'
import { KanbanBoard } from '../components/ui/KanbanBoard'
import { CreateTaskModal } from '../components/ui/CreateTaskModal'
import { EmptyState } from '../components/ui/EmptyState'
import { MotionButton } from '../components/ui/MotionButton'

export default function TasksPage() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  const {
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
    activeFiltersCount,
    taskStats,
    handleStatusChange,
    handleEdit,
    handleDelete,
    handleDragEnd
  } = useTasks(mockTasks)

  const handleCreateTask = () => {
    // Task creation logic would go here
    console.log('Creating task...')
  }

  const rightContent = (
    <>
      <ViewModeToggle viewMode={viewMode} onViewModeChange={setViewMode} />
      <MotionButton
        onClick={() => setShowCreateModal(true)}
        className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-2 rounded-xl hover:shadow-lg transition-all duration-300 flex items-center space-x-2"
      >
        <Plus className="w-4 h-4" />
        <span>New Task</span>
      </MotionButton>
    </>
  )

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <NavigationHeader
        title="Task Management"
        subtitle="Track and manage your onboarding tasks"
        gradient="from-orange-500 to-red-500"
        rightContent={rightContent}
      />

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            icon={<CheckSquare className="w-6 h-6" />}
            title="Total Tasks"
            value={taskStats.total}
            change="+3 this week"
            color="bg-gradient-to-r from-blue-500 to-blue-600"
          />
          <StatsCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Completed"
            value={taskStats.completed}
            change="+2 today"
            color="bg-gradient-to-r from-green-500 to-green-600"
          />
          <StatsCard
            icon={<CheckSquare className="w-6 h-6" />}
            title="In Progress"
            value={taskStats.inProgress}
            color="bg-gradient-to-r from-orange-500 to-orange-600"
          />
          <StatsCard
            icon={<CheckSquare className="w-6 h-6" />}
            title="Avg. Completion"
            value={taskStats.avgCompletionTime}
            change="-20min"
            color="bg-gradient-to-r from-purple-500 to-purple-600"
          />
        </div>

        <TaskFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          filters={filters}
          onFilterChange={(partial: Partial<Record<string, string[]>>) => {
            const [key, values] = Object.entries(partial)[0] as [string, string[]]
            updateFilter(key as keyof typeof filters, values)
          }}
          sortBy={sortBy}
          onSortChange={(value: string) => setSortBy(value as typeof sortBy)}
          activeFiltersCount={activeFiltersCount}
        />

        {/* Tasks Display */}
        <AnimatePresence mode="wait">
          {viewMode === 'grid' && (
            <motion.div
              key="grid"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6"
            >
              {filteredTasks.map((task, index) => (
                <motion.div
                  key={task.id}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1, duration: 0.6 }}
                >
                  <TaskCard
                    task={task}
                    onStatusChange={handleStatusChange}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}

          {viewMode === 'list' && (
            <motion.div
              key="list"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <TaskListView 
                tasks={filteredTasks}
                onStatusChange={handleStatusChange}
              />
            </motion.div>
          )}

          {viewMode === 'kanban' && (
            <motion.div
              key="kanban"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <KanbanBoard 
                kanbanColumns={kanbanColumns}
                onDragEnd={handleDragEnd}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {filteredTasks.length === 0 && (
          <EmptyState
            icon={<CheckSquare />}
            title="No tasks found"
            description={
              searchQuery || activeFiltersCount > 0
                ? 'Try adjusting your search or filters'
                : 'Create your first task to get started'
            }
            actionLabel="Create Task"
            onAction={() => setShowCreateModal(true)}
          />
        )}

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-8 bg-gradient-to-r from-orange-50 to-red-50 rounded-2xl p-6 border border-orange-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-orange-500" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/chat">
              <MotionButton
                variant="ghost"
                className="w-full bg-white text-gray-700 p-4 rounded-xl hover:shadow-md transition-all duration-300 flex items-center space-x-3"
              >
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <span>Ask for Task Help</span>
              </MotionButton>
            </Link>
            <MotionButton
              variant="ghost"
              className="w-full bg-white text-gray-700 p-4 rounded-xl hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <GitBranch className="w-5 h-5 text-green-600" />
              <span>View Code Review</span>
            </MotionButton>
            <Link href="/dashboard">
              <MotionButton
                variant="ghost"
                className="w-full bg-white text-gray-700 p-4 rounded-xl hover:shadow-md transition-all duration-300 flex items-center space-x-3"
              >
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <span>View Progress</span>
              </MotionButton>
            </Link>
            <MotionButton
              variant="ghost"
              className="w-full bg-white text-gray-700 p-4 rounded-xl hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <Download className="w-5 h-5 text-indigo-600" />
              <span>Export Tasks</span>
            </MotionButton>
          </div>
        </motion.div>
      </div>

      {/* Create Task Modal */}
      <CreateTaskModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreateTask={handleCreateTask}
      />
    </div>
  )
}