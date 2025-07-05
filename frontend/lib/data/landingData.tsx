import { 
  Clock, TrendingUp, Users, Award, Brain, Code, BookOpen, Target 
} from 'lucide-react'

export const stats = [
  { 
    icon: <Clock className="w-6 h-6 text-white" />, 
    value: "2 Days", 
    label: "Average Onboarding Time", 
    color: "bg-gradient-to-r from-blue-500 to-blue-600" 
  },
  { 
    icon: <TrendingUp className="w-6 h-6 text-white" />, 
    value: "85%", 
    label: "Faster Time to First PR", 
    color: "bg-gradient-to-r from-green-500 to-green-600" 
  },
  { 
    icon: <Users className="w-6 h-6 text-white" />, 
    value: "90%", 
    label: "Developer Satisfaction", 
    color: "bg-gradient-to-r from-purple-500 to-purple-600" 
  },
  { 
    icon: <Award className="w-6 h-6 text-white" />, 
    value: "50%", 
    label: "Reduced Mentor Overhead", 
    color: "bg-gradient-to-r from-orange-500 to-orange-600" 
  }
]

export const features = [
  {
    icon: <Brain className="w-8 h-8" />,
    title: "Multi-Agent AI System",
    description: "Four specialized AI agents working together to provide comprehensive onboarding support tailored to your needs.",
    color: "text-purple-600",
    bgColor: "bg-purple-50"
  },
  {
    icon: <Code className="w-8 h-8" />,
    title: "Intelligent Code Search",
    description: "Advanced code understanding that explains complex architectures, patterns, and helps you navigate large codebases instantly.",
    color: "text-blue-600",
    bgColor: "bg-blue-50"
  },
  {
    icon: <BookOpen className="w-8 h-8" />,
    title: "Personalized Learning Paths",
    description: "Dynamic learning plans that adapt to your experience level, role, and team requirements for optimal skill development.",
    color: "text-green-600",
    bgColor: "bg-green-50"
  },
  {
    icon: <Target className="w-8 h-8" />,
    title: "Smart Task Recommendations",
    description: "AI-powered task suggestions that match your skill level and help you make meaningful contributions from day one.",
    color: "text-orange-600",
    bgColor: "bg-orange-50"
  }
]

export const agents = [
  {
    name: "Knowledge Agent",
    description: "Your code exploration companion",
    icon: <Code className="w-6 h-6" />,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    features: [
      "Explains complex code patterns",
      "Searches across entire codebase",
      "Provides context-aware documentation",
      "Identifies dependencies and relationships"
    ]
  },
  {
    name: "Mentor Agent",
    description: "Senior developer guidance on demand",
    icon: <Brain className="w-6 h-6" />,
    color: "text-purple-600",
    bgColor: "bg-purple-50",
    features: [
      "Debugging assistance and troubleshooting",
      "Best practices and code review tips",
      "Architecture guidance and decisions",
      "Career development advice"
    ]
  },
  {
    name: "Guide Agent",
    description: "Personalized learning path creator",
    icon: <BookOpen className="w-6 h-6" />,
    color: "text-green-600",
    bgColor: "bg-green-50",
    features: [
      "Creates custom learning roadmaps",
      "Tracks progress and milestones",
      "Adapts to your learning pace",
      "Suggests relevant resources"
    ]
  },
  {
    name: "Task Agent",
    description: "Smart task recommendation engine",
    icon: <Target className="w-6 h-6" />,
    color: "text-orange-600",
    bgColor: "bg-orange-50",
    features: [
      "Matches tasks to skill level",
      "Prioritizes high-impact contributions",
      "Provides implementation guidance",
      "Tracks completion and feedback"
    ]
  }
]

export const demoSteps = [
  "Ask about authentication flow",
  "Get personalized learning plan", 
  "Receive task recommendations",
  "Debug with AI assistance"
]