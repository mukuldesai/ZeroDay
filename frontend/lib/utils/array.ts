export const groupBy = <T, K extends keyof T>(
  array: T[],
  key: K
): Record<string, T[]> => {
  return array.reduce((groups, item) => {
    const group = String(item[key])
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(item)
    return groups
  }, {} as Record<string, T[]>)
}

export const sortBy = <T>(
  array: T[],
  key: keyof T,
  direction: 'asc' | 'desc' = 'asc'
): T[] => {
  return [...array].sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1
    if (aVal > bVal) return direction === 'asc' ? 1 : -1
    return 0
  })
}

export const filterBy = <T>(
  array: T[],
  filters: Partial<Record<keyof T, any[]>>
): T[] => {
  return array.filter(item => {
    return (Object.entries(filters) as [keyof T, any[]][]).every(([key, values]) => {
      if (!values || values.length === 0) return true
      return values.includes(item[key])
    })
  })
}

export const searchItems = <T>(
  array: T[],
  searchQuery: string,
  searchKeys: (keyof T)[]
): T[] => {
  if (!searchQuery.trim()) return array
  
  const query = searchQuery.toLowerCase()
  return array.filter(item =>
    searchKeys.some(key => {
      const value = item[key]
      return String(value).toLowerCase().includes(query)
    })
  )
}

export const paginate = <T>(
  array: T[],
  page: number,
  pageSize: number
): {
  data: T[]
  totalPages: number
  hasNext: boolean
  hasPrev: boolean
} => {
  const startIndex = (page - 1) * pageSize
  const endIndex = startIndex + pageSize
  const data = array.slice(startIndex, endIndex)
  const totalPages = Math.ceil(array.length / pageSize)
  
  return {
    data,
    totalPages,
    hasNext: page < totalPages,
    hasPrev: page > 1
  }
}

export const unique = <T>(array: T[]): T[] => {
  return Array.from(new Set(array))
}

export const uniqueBy = <T, K extends keyof T>(
  array: T[],
  key: K
): T[] => {
  const seen = new Set()
  return array.filter(item => {
    const value = item[key]
    if (seen.has(value)) return false
    seen.add(value)
    return true
  })
}
