import { useState } from 'react';

interface WalkthroughStep {
  id: string;
  title: string;
  description: string;
  action: string;
  highlight?: string;
}

interface DemoWalkthroughProps {
  onComplete: () => void;
  onSkip: () => void;
}

const walkthroughSteps: WalkthroughStep[] = [
  {
    id: 'welcome',
    title: 'Welcome to ZeroDay Demo',
    description: 'You\'ll experience a realistic developer onboarding scenario with AI-powered assistance.',
    action: 'Start Tour',
    highlight: 'This is completely safe - all data is synthetic'
  },
  {
    id: 'chat',
    title: 'AI Chat Assistant',
    description: 'Ask questions about your codebase, get help with tasks, or discuss technical challenges.',
    action: 'Try the Chat',
    highlight: 'The AI has context about your demo project'
  },
  {
    id: 'dashboard',
    title: 'Development Dashboard',
    description: 'Track your progress, see active tasks, and monitor learning goals.',
    action: 'View Dashboard',
    highlight: 'All metrics are based on realistic developer workflows'
  },
  {
    id: 'upload',
    title: 'Data Integration',
    description: 'In real mode, you can upload docs, connect GitHub, Slack, and other tools.',
    action: 'See Upload Options',
    highlight: 'Demo mode shows how this would work with your data'
  },
  {
    id: 'complete',
    title: 'Explore Freely',
    description: 'You\'re all set! Explore any feature - everything is functional with demo data.',
    action: 'Start Exploring',
    highlight: 'Toggle demo mode off anytime to use real data'
  }
];

export default function DemoWalkthrough({ onComplete, onSkip }: DemoWalkthroughProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const step = walkthroughSteps[currentStep];
  const isLastStep = currentStep === walkthroughSteps.length - 1;

  const handleNext = () => {
    if (isLastStep) {
      setIsVisible(false);
      onComplete();
    } else {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleSkip = () => {
    setIsVisible(false);
    onSkip();
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {currentStep + 1}
              </div>
              <span className="text-sm text-gray-500">
                {currentStep + 1} of {walkthroughSteps.length}
              </span>
            </div>
            <button
              onClick={handleSkip}
              className="text-gray-400 hover:text-gray-600 text-sm"
            >
              Skip tour
            </button>
          </div>

          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            {step.title}
          </h3>

          <p className="text-gray-600 mb-4">
            {step.description}
          </p>

          {step.highlight && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-blue-800">
                💡 {step.highlight}
              </p>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="flex space-x-1">
              {walkthroughSteps.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>

            <div className="flex space-x-3">
              {currentStep > 0 && (
                <button
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800"
                >
                  Back
                </button>
              )}
              <button
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {step.action}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}