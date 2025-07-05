import { useState, useMemo } from 'react'
import { filterBy, searchItems, sortBy } from '../utils/array'

export interface FilterOptions<T> {
  searchKeys?: (keyof T)[]
  sortKey?: keyof T
  sortDirection?: 'asc' | 'desc'
  initialFilters?: Partial<Record<keyof T, any[]>>
}

export function useFilter<T>(
  data: T[],
  options: FilterOptions<T> = {}
) {
  const { searchKeys = [], sortKey, sortDirection = 'asc' } = options
  
  const [searchQuery, setSearchQuery] = useState('')
  const [filters, setFilters] = useState<Partial<Record<keyof T, any[]>>>(options.initialFilters || {})
  const [currentSortKey, setSortKey] = useState<keyof T | undefined>(sortKey)
  const [currentSortDirection, setSortDirection] = useState<'asc' | 'desc'>(sortDirection)

  const filteredData = useMemo(() => {
    let result = data

    // Apply search
    if (searchQuery && searchKeys.length > 0) {
      result = searchItems(result, searchQuery, searchKeys)
    }

    // Apply filters
    result = filterBy(result, filters)

    // Apply sorting
    if (currentSortKey) {
      result = sortBy(result, currentSortKey, currentSortDirection)
    }

    return result
  }, [data, searchQuery, filters, currentSortKey, currentSortDirection, searchKeys])

  const updateFilter = (key: keyof T, values: any[]) => {
    setFilters(prev => ({
      ...prev,
      [key]: values
    }))
  }

  const removeFilter = (key: keyof T, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: prev[key]?.filter(v => v !== value) || []
    }))
  }

  const clearFilters = () => {
    setFilters({})
    setSearchQuery('')
  }

  const toggleSort = (key: keyof T) => {
    if (currentSortKey === key) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDirection('asc')
    }
  }

  const activeFiltersCount = Object.values(filters).reduce<number>((count, filterValues) => {
    if (Array.isArray(filterValues)) {
      return count + filterValues.length
    }
    return count
  }, 0) + (searchQuery ? 1 : 0)

  return {
    filteredData,
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    removeFilter,
    clearFilters,
    currentSortKey,
    currentSortDirection,
    toggleSort,
    setSortKey,
    setSortDirection,
    activeFiltersCount
  }
}
