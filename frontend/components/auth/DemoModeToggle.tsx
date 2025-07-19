import { useDemo } from '../../lib/hooks/useDemo';

interface DemoModeToggleProps {
  className?: string;
}

export default function DemoModeToggle({ className = '' }: DemoModeToggleProps) {
  const { isDemoMode, toggleDemoMode } = useDemo();

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      <span className="text-sm font-medium text-gray-700">Demo Mode</span>
      
      <button
        onClick={toggleDemoMode}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
          isDemoMode ? 'bg-green-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            isDemoMode ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
      
      <div className="flex items-center space-x-1">
        {isDemoMode ? (
          <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
            Using Sample Data
          </span>
        ) : (
          <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            Using Real Data
          </span>
        )}
      </div>
    </div>
  );
}