import React from 'react'
import { motion } from 'framer-motion'
import { TaskFilter } from '../../lib/types'
import { SearchInput } from './SearchInput'

interface TaskFiltersProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  filters: Partial<TaskFilter>
  onFilterChange: (filters: Partial<TaskFilter>) => void
  sortBy: string
  onSortChange: (sortBy: string) => void
  activeFiltersCount: number
  userId?: string
}

export const TaskFilters: React.FC<TaskFiltersProps> = ({
  searchQuery,
  onSearchChange,
  filters,
  onFilterChange,
  sortBy,
  onSortChange,
  activeFiltersCount,
  userId
}) => {
  const handleMultiSelectChange = (
    key: keyof TaskFilter,
    e: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const values = Array.from(e.target.selectedOptions, option => option.value).filter(v => v !== '')
    const updatedFilters = { 
      [key]: values,
      ...(userId && { userId })
    }
    onFilterChange(updatedFilters)
  }

  const removeActiveFilter = (key: keyof TaskFilter, value: string) => {
    const currentValues = (filters[key] ?? []) as string[]
    const newValues = currentValues.filter((v) => v !== value)
    const updatedFilters = { 
      [key]: newValues,
      ...(userId && { userId })
    }
    onFilterChange(updatedFilters)
  }

  const handleSearchChange = (query: string) => {
    onSearchChange(query)
  }

  const clearAllFilters = () => {
    onFilterChange(userId ? { userId } : {})
    onSearchChange('')
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 mb-8">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        <div className="lg:col-span-4">
          <SearchInput
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search tasks..."
          />
        </div>

        <div className="lg:col-span-2">
          <select 
            multiple
            size={1}
            className="w-full py-2 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
            onChange={(e) => handleMultiSelectChange('status', e)}
            value={filters.status || []}
          >
            <option value="">All Status</option>
            <option value="todo">To Do</option>
            <option value="in-progress">In Progress</option>
            <option value="review">Review</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div className="lg:col-span-2">
          <select 
            multiple
            size={1}
            className="w-full py-2 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
            onChange={(e) => handleMultiSelectChange('priority', e)}
            value={filters.priority || []}
          >
            <option value="">All Priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div className="lg:col-span-2">
          <select 
            multiple
            size={1}
            className="w-full py-2 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
            onChange={(e) => handleMultiSelectChange('category', e)}
            value={filters.category || []}
          >
            <option value="">All Categories</option>
            <option value="Frontend">Frontend</option>
            <option value="Backend">Backend</option>
            <option value="DevOps">DevOps</option>
            <option value="Testing">Testing</option>
          </select>
        </div>

        <div className="lg:col-span-2">
          <select 
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="w-full py-2 px-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
          >
            <option value="dueDate">Sort by Due Date</option>
            <option value="priority">Sort by Priority</option>
            <option value="difficulty">Sort by Difficulty</option>
            <option value="progress">Sort by Progress</option>
            <option value="createdAt">Sort by Created</option>
            <option value="updatedAt">Sort by Updated</option>
          </select>
        </div>
      </div>

      {(activeFiltersCount > 0 || searchQuery) && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-600">
              Active filters ({activeFiltersCount + (searchQuery ? 1 : 0)})
            </span>
            <button
              onClick={clearAllFilters}
              className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Clear all
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(filters).map(([key, values]) => 
              key !== 'userId' && (values as string[]).map((value: string) => (
                <motion.span
                  key={`${key}-${value}`}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-700"
                >
                  {value}
                  <button
                    onClick={() => removeActiveFilter(key as keyof TaskFilter, value)}
                    className="ml-2 text-orange-500 hover:text-orange-700"
                  >
                    ×
                  </button>
                </motion.span>
              ))
            )}
            {searchQuery && (
              <motion.span
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700"
              >
                Search: "{searchQuery}"
                <button
                  onClick={() => handleSearchChange('')}
                  className="ml-2 text-blue-500 hover:text-blue-700"
                >
                  ×
                </button>
              </motion.span>
            )}
          </div>
        </div>
      )}
    </div>
  )
}