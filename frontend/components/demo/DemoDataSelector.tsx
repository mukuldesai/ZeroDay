import { useState } from 'react';

interface DemoScenario {
  id: string;
  name: string;
  description: string;
  company: string;
  role: string;
  teamSize: number;
  industry: string;
}

interface DemoDataSelectorProps {
  onSelectScenario: (scenarioId: string) => void;
  selectedScenario?: string;
}

const scenarios: DemoScenario[] = [
  {
    id: 'startup',
    name: 'TechStartup Inc',
    description: 'Early-stage fintech startup building payment solutions',
    company: 'TechStartup Inc',
    role: 'Senior Full Stack Developer',
    teamSize: 12,
    industry: 'Fintech'
  },
  {
    id: 'enterprise',
    name: 'Enterprise Solutions Corp',
    description: 'Large healthcare company with complex compliance requirements',
    company: 'Enterprise Solutions Corp',
    role: 'Senior Software Engineer',
    teamSize: 250,
    industry: 'Healthcare'
  },
  {
    id: 'freelancer',
    name: 'Independent Developer',
    description: 'Solo developer working on AI-powered web applications',
    company: 'Freelance',
    role: 'Full Stack Developer',
    teamSize: 1,
    industry: 'Web Development'
  }
];

export default function DemoDataSelector({ onSelectScenario, selectedScenario }: DemoDataSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleSelectScenario = (scenarioId: string) => {
    onSelectScenario(scenarioId);
    setIsOpen(false);
  };

  const currentScenario = scenarios.find(s => s.id === selectedScenario) || scenarios[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-left hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <div>
          <div className="text-sm font-medium text-gray-900">{currentScenario.name}</div>
          <div className="text-xs text-gray-500">{currentScenario.role}</div>
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
          {scenarios.map((scenario) => (
            <button
              key={scenario.id}
              onClick={() => handleSelectScenario(scenario.id)}
              className={`w-full px-4 py-3 text-left hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg ${
                selectedScenario === scenario.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
              }`}
            >
              <div className="text-sm font-medium text-gray-900">{scenario.name}</div>
              <div className="text-xs text-gray-500 mt-1">{scenario.description}</div>
              <div className="flex items-center space-x-4 mt-2 text-xs text-gray-400">
                <span>{scenario.role}</span>
                <span>•</span>
                <span>{scenario.teamSize} people</span>
                <span>•</span>
                <span>{scenario.industry}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}