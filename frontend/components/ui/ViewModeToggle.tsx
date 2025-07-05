import React from 'react'
import { MotionButton } from './MotionButton'

type ViewMode = 'grid' | 'list' | 'kanban'

interface ViewModeToggleProps {
  viewMode: ViewMode
  onViewModeChange: (mode: ViewMode) => void
}

export const ViewModeToggle: React.FC<ViewModeToggleProps> = ({
  viewMode,
  onViewModeChange
}) => {
  const modes = [
    { 
      mode: 'grid' as const, 
      icon: (
        <div className="w-3 h-3 grid grid-cols-2 gap-0.5">
          <div className="bg-current"></div>
          <div className="bg-current"></div>
          <div className="bg-current"></div>
          <div className="bg-current"></div>
        </div>
      ),
      label: 'Grid'
    },
    { 
      mode: 'list' as const, 
      icon: (
        <div className="w-3 h-3 space-y-0.5">
          <div className="h-0.5 bg-current"></div>
          <div className="h-0.5 bg-current"></div>
          <div className="h-0.5 bg-current"></div>
        </div>
      ),
      label: 'List'
    },
    { 
      mode: 'kanban' as const, 
      icon: (
        <div className="w-3 h-3 grid grid-cols-3 gap-0.5">
          <div className="bg-current"></div>
          <div className="bg-current"></div>
          <div className="bg-current"></div>
        </div>
      ),
      label: 'Kanban'
    }
  ]

  return (
    <div className="flex items-center bg-gray-100 rounded-lg p-1">
      {modes.map(({ mode, icon, label }) => (
        <MotionButton
          key={mode}
          onClick={() => onViewModeChange(mode)}
          className={`p-2 rounded text-sm font-medium transition-colors ${
            viewMode === mode
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
          variant="ghost"
          title={label}
        >
          {icon}
        </MotionButton>
      ))}
    </div>
  )
}