import { useState } from 'react';

interface DemoExplanationProps {
  compact?: boolean;
}

export default function DemoExplanation({ compact = false }: DemoExplanationProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (compact) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start space-x-2">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-blue-800">
              You're viewing demo data. All information is synthetic and for demonstration purposes.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Demo Mode Active</h3>
          <p className="text-blue-800 mb-4">
            You're experiencing ZeroDay with realistic but synthetic data. This lets you explore all features safely.
          </p>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-blue-700 underline text-sm hover:text-blue-600"
          >
            {isExpanded ? 'Show less' : 'Learn more about demo vs real data'}
          </button>

          {isExpanded && (
            <div className="mt-4 space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-medium text-green-800 mb-2">✅ Demo Data Includes:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Realistic conversation histories</li>
                    <li>• Sample code repositories</li>
                    <li>• Fictional team members</li>
                    <li>• Mock project timelines</li>
                    <li>• Synthetic document uploads</li>
                  </ul>
                </div>
                
                <div className="bg-white rounded-lg p-4 border border-blue-200">
                  <h4 className="font-medium text-blue-800 mb-2">🔒 Real Data Would Include:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Your actual work conversations</li>
                    <li>• Real GitHub repositories</li>
                    <li>• Actual team members</li>
                    <li>• Live project data</li>
                    <li>• Your uploaded documents</li>
                  </ul>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-blue-200">
                <p className="text-sm text-gray-600">
                  <strong>Privacy First:</strong> In real mode, all your data stays secure and private. 
                  ZeroDay processes information locally and never stores sensitive content on external servers.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}