import React from 'react';
import { 
  Monitor, 
  Server, 
  Database, 
  Brain, 
  Users, 
  Shield,
  Cloud,
  Zap,
  GitBranch,
  MessageSquare
} from 'lucide-react';

const ArchitectureDiagram: React.FC = () => {
  const architectureComponents = [
    {
      layer: "Frontend Layer",
      color: "bg-blue-500",
      components: [
        { name: "Next.js Application", icon: <Monitor className="w-5 h-5" />, description: "React-based UI with TypeScript" },
        { name: "Authentication UI", icon: <Shield className="w-5 h-5" />, description: "Login, user management" },
        { name: "Dashboard Components", icon: <Users className="w-5 h-5" />, description: "Analytics, tasks, learning paths" }
      ]
    },
    {
      layer: "API Layer",
      color: "bg-green-500",
      components: [
        { name: "FastAPI Backend", icon: <Server className="w-5 h-5" />, description: "Python REST API server" },
        { name: "Authentication Service", icon: <Shield className="w-5 h-5" />, description: "JWT-based auth system" },
        { name: "File Upload Handler", icon: <Cloud className="w-5 h-5" />, description: "Document processing pipeline" }
      ]
    },
    {
      layer: "AI Agent Layer",
      color: "bg-purple-500",
      components: [
        { name: "Knowledge Agent", icon: <Brain className="w-5 h-5" />, description: "General Q&A and search" },
        { name: "Mentor Agent", icon: <Users className="w-5 h-5" />, description: "Troubleshooting and guidance" },
        { name: "Task Agent", icon: <Zap className="w-5 h-5" />, description: "Task generation and assignment" },
        { name: "Guide Agent", icon: <GitBranch className="w-5 h-5" />, description: "Learning path creation" }
      ]
    },
    {
      layer: "Data Processing Layer",
      color: "bg-orange-500",
      components: [
        { name: "Document Parser", icon: <Database className="w-5 h-5" />, description: "Code, docs, and text processing" },
        { name: "Vector Indexer", icon: <Brain className="w-5 h-5" />, description: "Embedding generation and storage" },
        { name: "Data Sources", icon: <GitBranch className="w-5 h-5" />, description: "GitHub, Slack, Jira integration" }
      ]
    },
    {
      layer: "Storage Layer",
      color: "bg-red-500",
      components: [
        { name: "ChromaDB", icon: <Database className="w-5 h-5" />, description: "Vector database for embeddings" },
        { name: "SQLite/PostgreSQL", icon: <Database className="w-5 h-5" />, description: "User and organization data" },
        { name: "File Storage", icon: <Cloud className="w-5 h-5" />, description: "Document and media storage" }
      ]
    }
  ];

  const dataFlow = [
    { from: "User Upload", to: "Document Parser", description: "Files processed and chunked" },
    { from: "Document Parser", to: "Vector Indexer", description: "Text converted to embeddings" },
    { from: "Vector Indexer", to: "ChromaDB", description: "Embeddings stored with metadata" },
    { from: "User Query", to: "AI Agents", description: "Natural language queries" },
    { from: "AI Agents", to: "Vector Search", description: "Semantic search for context" },
    { from: "Vector Search", to: "LLM Processing", description: "Context-aware responses" }
  ];

  const techStack = [
    { category: "Frontend", technologies: ["Next.js", "React", "TypeScript", "Tailwind CSS"] },
    { category: "Backend", technologies: ["FastAPI", "Python", "Uvicorn", "Pydantic"] },
    { category: "AI/ML", technologies: ["OpenAI GPT-4", "Anthropic Claude", "ChromaDB", "LangChain"] },
    { category: "Database", technologies: ["SQLite", "PostgreSQL", "ChromaDB", "Redis"] },
    { category: "Infrastructure", technologies: ["Vercel", "Railway", "Docker", "Nginx"] }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          System Architecture
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          A scalable, multi-tenant AI-powered developer onboarding platform 
          built with modern technologies and enterprise-grade architecture
        </p>
      </div>

      <div className="mb-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-8 text-center">
          Architecture Overview
        </h2>
        <div className="space-y-6">
          {architectureComponents.map((layer, index) => (
            <div key={index} className="relative">
              <div className={`${layer.color} text-white px-4 py-2 rounded-t-lg font-semibold`}>
                {layer.layer}
              </div>
              <div className="bg-white border-2 border-gray-200 rounded-b-lg p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {layer.components.map((component, componentIndex) => (
                    <div key={componentIndex} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className="mt-1">{component.icon}</div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{component.name}</h4>
                        <p className="text-sm text-gray-600">{component.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              {index < architectureComponents.length - 1 && (
                <div className="flex justify-center py-2">
                  <div className="w-0.5 h-6 bg-gray-300"></div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <MessageSquare className="w-6 h-6 mr-2 text-blue-600" />
            Data Flow
          </h3>
          <div className="space-y-4">
            {dataFlow.map((flow, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                  {flow.from}
                </div>
                <div className="flex-1 border-t border-dashed border-gray-300 relative">
                  <div className="absolute right-0 top-0 transform -translate-y-1/2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  </div>
                </div>
                <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  {flow.to}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <Zap className="w-6 h-6 mr-2 text-purple-600" />
            Technology Stack
          </h3>
          <div className="space-y-4">
            {techStack.map((stack, index) => (
              <div key={index}>
                <h4 className="font-semibold text-gray-900 mb-2">{stack.category}</h4>
                <div className="flex flex-wrap gap-2">
                  {stack.technologies.map((tech, techIndex) => (
                    <span key={techIndex} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 border border-gray-200">
        <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Key Architecture Principles
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <Shield className="w-6 h-6 text-blue-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Multi-Tenant</h4>
            <p className="text-sm text-gray-600">Complete data isolation between organizations</p>
          </div>
          <div className="text-center">
            <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <Zap className="w-6 h-6 text-green-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Scalable</h4>
            <p className="text-sm text-gray-600">Horizontal scaling with microservices architecture</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">AI-Powered</h4>
            <p className="text-sm text-gray-600">Advanced AI agents with contextual understanding</p>
          </div>
          <div className="text-center">
            <div className="bg-orange-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
              <GitBranch className="w-6 h-6 text-orange-600" />
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">Modular</h4>
            <p className="text-sm text-gray-600">Loosely coupled components for maintainability</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArchitectureDiagram;