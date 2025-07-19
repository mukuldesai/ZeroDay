import React, { createContext, useContext, useState, ReactNode } from 'react'

interface DemoContextType {
  isDemoMode: boolean
  selectedScenario: string
  userName: string
  isDemo: boolean
  toggleDemoMode: () => void
  setSelectedScenario: (scenario: string) => void
  setUserName: (name: string) => void
  
}

const DemoContext = createContext<DemoContextType | undefined>(undefined)

interface DemoProviderProps {
  children: ReactNode
}

export const DemoProvider: React.FC<DemoProviderProps> = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState(true)
  const [selectedScenario, setSelectedScenario] = useState('startup')
  const [userName, setUserName] = useState('Developer')

  const toggleDemoMode = () => {
    setIsDemoMode(!isDemoMode)
  }

  const value = {
    isDemoMode,
    isDemo: isDemoMode,
    selectedScenario,
    userName,
    toggleDemoMode,
    setSelectedScenario,
    setUserName
  }

  return (
    <DemoContext.Provider value={value}>
      {children}
    </DemoContext.Provider>
  )
}

export const useDemo = () => {
  const context = useContext(DemoContext)
  if (context === undefined) {
    throw new Error('useDemo must be used within a DemoProvider')
  }
  return context
}