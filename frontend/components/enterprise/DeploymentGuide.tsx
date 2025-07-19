import React, { useState } from 'react';
import { 
  Server, 
  Cloud, 
  Database, 
  Terminal, 
  CheckCircle, 
  AlertCircle,
  Copy,
  ExternalLink,
  Play,
  Settings
} from 'lucide-react';

const DeploymentGuide: React.FC = () => {
  const [activeTab, setActiveTab] = useState('local');
  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const deploymentOptions = [
    { id: 'local', label: 'Local Development', icon: <Terminal className="w-5 h-5" /> },
    { id: 'vercel', label: 'Vercel + Railway', icon: <Cloud className="w-5 h-5" /> },
    { id: 'docker', label: 'Docker', icon: <Server className="w-5 h-5" /> },
    { id: 'vps', label: 'VPS/Server', icon: <Database className="w-5 h-5" /> }
  ];

  const copyToClipboard = (code: string, id: string) => {
    navigator.clipboard.writeText(code);
    setCopiedCode(id);
    setTimeout(() => setCopiedCode(null), 2000);
  };

  const CodeBlock = ({ code, language, id }: { code: string; language: string; id: string }) => (
    <div className="relative bg-gray-900 rounded-lg p-4 mt-4">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-400">{language}</span>
        <button
          onClick={() => copyToClipboard(code, id)}
          className="flex items-center space-x-1 text-gray-400 hover:text-white transition-colors"
        >
          {copiedCode === id ? (
            <CheckCircle className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
          <span className="text-sm">{copiedCode === id ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      <pre className="text-sm text-gray-100 overflow-x-auto">
        <code>{code}</code>
      </pre>
    </div>
  );

  const localDeployment = {
    steps: [
      {
        title: "Clone Repository",
        code: `git clone https://github.com/mukuldesai/ZeroDay.git
cd zeroday`,
        description: "Download the project from GitHub"
      },
      {
        title: "Setup Python Environment",
        code: `python -m venv env
source env/bin/activate  # Windows: env\\Scripts\\activate
pip install -r requirements.txt`,
        description: "Create isolated Python environment"
      },
      {
        title: "Setup Frontend",
        code: `cd frontend
npm install
cd ..`,
        description: "Install Node.js dependencies"
      },
      {
        title: "Configure Environment",
        code: `cp .env.example .env
# Edit .env file with your API keys`,
        description: "Set up environment variables"
      },
      {
        title: "Initialize Database",
        code: `python database/setup.py
python -m scripts.setup_demo`,
        description: "Create database and demo data"
      },
      {
        title: "Start Services",
        code: `# Terminal 1: Backend
python api/main.py

# Terminal 2: Frontend
cd frontend && npm run dev`,
        description: "Launch both backend and frontend servers"
      }
    ]
  };

  const vercelDeployment = {
    frontend: [
      { step: "Connect GitHub repo to Vercel", description: "Link your repository" },
      { step: "Set build command: cd frontend && npm run build", description: "Configure build process" },
      { step: "Set output directory: frontend/.next", description: "Specify build output" },
      { step: "Add environment variables", description: "Configure API keys and settings" }
    ],
    backend: [
      { step: "Connect repo to Railway", description: "Deploy backend service" },
      { step: "Set start command: python api/main.py", description: "Configure startup" },
      { step: "Add environment variables", description: "Set production settings" },
      { step: "Configure custom domain", description: "Setup DNS and SSL" }
    ]
  };

  const dockerDeployment = {
    dockerfile: `FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api/main.py"]`,
    commands: `docker build -t zeroday .
docker run -p 8000:8000 --env-file .env zeroday`
  };

  const envVariables = [
    { name: "OPENAI_API_KEY", description: "OpenAI API key for GPT models", required: true },
    { name: "ANTHROPIC_API_KEY", description: "Anthropic API key for Claude", required: true },
    { name: "DATABASE_URL", description: "Database connection string", required: true },
    { name: "SECRET_KEY", description: "Application secret key", required: true },
    { name: "DEMO_MODE", description: "Enable demo mode (true/false)", required: false },
    { name: "ALLOWED_ORIGINS", description: "CORS allowed origins", required: true }
  ];

  const troubleshooting = [
    {
      issue: "Port already in use",
      solution: "lsof -ti:8000 | xargs kill -9",
      description: "Kill processes using required ports"
    },
    {
      issue: "Database connection failed",
      solution: "python database/setup.py check",
      description: "Verify database setup and connectivity"
    },
    {
      issue: "Vector store issues",
      solution: "python vector_store/chromadb_setup.py health",
      description: "Check ChromaDB status and configuration"
    },
    {
      issue: "Missing demo data",
      solution: "python scripts/setup_demo.py",
      description: "Regenerate demo data and scenarios"
    }
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Deployment Guide
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Complete guide to deploy ZeroDay in development and production environments
        </p>
      </div>

      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {deploymentOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => setActiveTab(option.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === option.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {option.icon}
                <span>{option.label}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="mb-12">
        {activeTab === 'local' && (
          <div className="space-y-8">
            <div className="bg-blue-50 border-l-4 border-blue-400 p-6">
              <div className="flex">
                <AlertCircle className="w-6 h-6 text-blue-600 mr-3" />
                <div>
                  <h3 className="text-lg font-semibold text-blue-800">Prerequisites</h3>
                  <p className="text-blue-700 mt-1">
                    Ensure you have Python 3.9+, Node.js 18+, and Git installed on your system
                  </p>
                </div>
              </div>
            </div>

            {localDeployment.steps.map((step, index) => (
              <div key={index} className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
                <div className="flex items-center mb-4">
                  <div className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold mr-3">
                    {index + 1}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900">{step.title}</h3>
                </div>
                <p className="text-gray-600 mb-4">{step.description}</p>
                <CodeBlock code={step.code} language="bash" id={`local-${index}`} />
              </div>
            ))}
          </div>
        )}

        {activeTab === 'vercel' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                <Cloud className="w-6 h-6 mr-2 text-blue-600" />
                Frontend (Vercel)
              </h3>
              <div className="space-y-4">
                {vercelDeployment.frontend.map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="bg-blue-100 text-blue-800 w-6 h-6 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0 mt-1">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{step.step}</h4>
                      <p className="text-sm text-gray-600">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                <Server className="w-6 h-6 mr-2 text-green-600" />
                Backend (Railway)
              </h3>
              <div className="space-y-4">
                {vercelDeployment.backend.map((step, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="bg-green-100 text-green-800 w-6 h-6 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0 mt-1">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{step.step}</h4>
                      <p className="text-sm text-gray-600">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'docker' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Dockerfile</h3>
              <CodeBlock code={dockerDeployment.dockerfile} language="dockerfile" id="dockerfile" />
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Build and Run</h3>
              <CodeBlock code={dockerDeployment.commands} language="bash" id="docker-commands" />
            </div>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6">
              <div className="flex">
                <AlertCircle className="w-6 h-6 text-yellow-600 mr-3" />
                <div>
                  <h3 className="text-lg font-semibold text-yellow-800">Docker Compose</h3>
                  <p className="text-yellow-700 mt-1">
                    For production, consider using Docker Compose with separate containers for frontend, backend, and database
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'vps' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Server Setup</h3>
              <CodeBlock 
                code={`sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx
git clone https://github.com/mukuldesai/ZeroDay.git
cd zeroday
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt`}
                language="bash" 
                id="vps-setup" 
              />
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Nginx Configuration</h3>
              <CodeBlock 
                code={`server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}`}
                language="nginx" 
                id="nginx-config" 
              />
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <Settings className="w-6 h-6 mr-2 text-purple-600" />
            Environment Variables
          </h3>
          <div className="space-y-4">
            {envVariables.map((env, index) => (
              <div key={index} className="border-l-4 border-gray-200 pl-4">
                <div className="flex items-center space-x-2">
                  <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono">{env.name}</code>
                  {env.required && (
                    <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-semibold">
                      Required
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">{env.description}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center">
            <AlertCircle className="w-6 h-6 mr-2 text-orange-600" />
            Troubleshooting
          </h3>
          <div className="space-y-4">
            {troubleshooting.map((item, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-semibold text-gray-900 mb-2">{item.issue}</h4>
                <p className="text-sm text-gray-600 mb-2">{item.description}</p>
                <code className="bg-gray-100 px-2 py-1 rounded text-sm font-mono block">
                  {item.solution}
                </code>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8 border border-gray-200">
        <h3 className="text-2xl font-semibold text-gray-900 mb-6 text-center">
          Quick Start Checklist
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Clone repository</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Install dependencies</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Configure environment</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Initialize database</span>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Setup demo data</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Start backend server</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Start frontend server</span>
            </div>
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <span className="text-gray-700">Access application</span>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center">
          <div className="flex items-center justify-center space-x-4">
            <a
              href="http://localhost:3000"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <Play className="w-5 h-5" />
              <span>Launch Application</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          <p className="text-sm text-gray-600 mt-4">
            Default development server runs on localhost:3000
          </p>
        </div>
      </div>
    </div>
  );
};

export default DeploymentGuide;