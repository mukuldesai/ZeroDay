import React from 'react'
import { Search, X } from 'lucide-react'
import { motion } from 'framer-motion'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  showClearButton?: boolean
  userId?: string
  isDemo?: boolean
}

export const SearchInput: React.FC<SearchInputProps> = ({
  value,
  onChange,
  placeholder = "Search...",
  className = '',
  showClearButton = true,
  userId,
  isDemo = false
}) => {
  const focusRing = isDemo ? 'focus:ring-demo-500' : 'focus:ring-indigo-500'
  
  return (
    <div className={`relative ${className}`}>
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
      <input
        type="text"
        placeholder={isDemo ? `${placeholder} (demo mode)` : placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className={`w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg ${focusRing} focus:border-transparent ${
          isDemo ? 'ring-2 ring-demo-200' : ''
        }`}
      />
      {showClearButton && value && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={() => onChange('')}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100"
        >
          <X className="w-3 h-3" />
        </motion.button>
      )}
    </div>
  )
}
