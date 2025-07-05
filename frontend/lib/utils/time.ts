export const formatTimeAgo = (timestamp: Date): string => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  
  return timestamp.toLocaleDateString()
}

export const formatDuration = (minutes: number): string => {
  if (minutes < 60) return `${minutes}m`
  
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  
  if (remainingMinutes === 0) return `${hours}h`
  return `${hours}h ${remainingMinutes}m`
}

export const formatEstimatedTime = (timeString: string): string => {
  // Convert strings like "2 hours", "30 minutes", "1.5 hours" to consistent format
  const normalized = timeString.toLowerCase().trim()
  
  if (normalized.includes('hour')) {
    const hours = parseFloat(normalized.match(/[\d.]+/)?.[0] || '0')
    if (hours === 1) return '1 hour'
    if (hours < 1) return `${Math.round(hours * 60)} minutes`
    return `${hours} hours`
  }
  
  if (normalized.includes('min')) {
    const minutes = parseInt(normalized.match(/\d+/)?.[0] || '0')
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60)
      const remainingMin = minutes % 60
      return remainingMin > 0 ? `${hours}h ${remainingMin}m` : `${hours}h`
    }
    return `${minutes}m`
  }
  
  return timeString
}

export const isOverdue = (dueDate?: Date): boolean => {
  if (!dueDate) return false
  return new Date() > dueDate
}

export const getDaysUntilDue = (dueDate?: Date): number | null => {
  if (!dueDate) return null
  const diff = dueDate.getTime() - new Date().getTime()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}