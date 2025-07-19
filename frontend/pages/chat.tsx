import React, { useState, useRef, useEffect } from 'react';
import { 
  Brain, BookOpen, Target, Users, MessageSquare, Zap, Send, 
  CheckCircle, AlertCircle, FileText, Clock, File, Upload, RefreshCw, Quote,
  ArrowRight, TrendingUp, Database, Code, Globe, Shield, Bell, User, Settings, Menu,
  Palette, LogOut, UserCircle, Play, Sparkles
} from 'lucide-react';


const getRelativeTime = (timestamp: Date) => {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - timestamp.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

// Types
type NavigationHeaderProps = {
  title: string
  subtitle?: string
  showNotifications?: boolean
  rightContent?: React.ReactNode
}

type Action = {
  text: string
  agent: string
  icon: React.ReactNode
}

type Citation = {
  type: 'user_document' | 'platform_knowledge'
  source_file: string
  document_id?: string
  upload_time?: string
  relevance_score: number
}

type ChatMessage = {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  agent: string
  confidence?: number
  responseTime?: string
  citations?: Citation[]  
  document_sources?: Citation[]  
}

type DocumentMetadata = {
  id: string
  filename: string
  file_type: string
  size: number
  upload_time: string
  processing_status: 'processing' | 'indexed' | 'failed'
  document_count: number
  user_id: string
  source_type: string
}

type AgentAvailability = {
  available: boolean
}

type AgentStatus = {
  knowledge?: AgentAvailability
  task?: AgentAvailability
  mentor?: AgentAvailability
  guide?: AgentAvailability
}


const NavigationHeader = ({ title, subtitle, showNotifications = true, rightContent }: NavigationHeaderProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotificationsDropdown(false);
      setShowSettings(false);
      setShowUserMenu(false);
    };
    
    if (showNotificationsDropdown || showSettings || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotificationsDropdown, showSettings, showUserMenu]);

  const notifications = [
    {
      id: 1,
      title: 'Chat Session Active',
      message: 'AI agents are responding to your queries',
      time: new Date(Date.now() - 2 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Knowledge Base Updated',
      message: 'Your documents are indexed and ready',
      time: new Date(Date.now() - 8 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'New Features Available',
      message: 'Enhanced citation support is now live',
      time: new Date(Date.now() - 15 * 60 * 1000),
      type: 'warning'
    }
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'info': return <MessageSquare className="w-4 h-4 text-blue-400" />;
      default: return <Bell className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <nav className="bg-black/20 backdrop-blur-sm border-b border-white/10 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-400 to-purple-400 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div className="flex items-center space-x-2">
              <h1 className="text-white font-bold text-lg">ZeroDay</h1>
              <span className="hidden sm:block text-gray-400 text-sm">Enterprise AI Developer Onboarding Platform</span>
            </div>
          </div>

          
          <div className="hidden md:flex items-center space-x-6">
            <a href="/" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Home</a>
            <a href="/chat" className="text-blue-400 font-medium text-sm">AI Chat</a>
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Dashboard</a>
            <a href="/tasks" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Tasks</a>
            <a href="/upload" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Upload</a>
          </div>

          
          <div className="flex items-center space-x-3">
            {rightContent}
            
           
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSettings(!showSettings);
                  setShowNotificationsDropdown(false);
                  setShowUserMenu(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              {showSettings && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
                  <div className="py-1">
                    <a
                      href="/setup"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Palette className="w-4 h-4" />
                      <span>Preferences</span>
                    </a>
                    <a
                      href="/security"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Shield className="w-4 h-4" />
                      <span>Security</span>
                    </a>
                    <button
                      onClick={() => console.log('Theme toggle')}
                      className="flex items-center space-x-3 w-full px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Brain className="w-4 h-4" />
                      <span>Theme</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            
            {showNotifications && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowNotificationsDropdown(!showNotificationsDropdown);
                    setShowSettings(false);
                    setShowUserMenu(false);
                  }}
                  className="p-2 text-gray-400 hover:text-white transition-colors relative rounded-lg hover:bg-white/10"
                >
                  <Bell className="w-5 h-5" />
                  {notifications.length > 0 && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
                  )}
                </button>
                
                {showNotificationsDropdown && (
                  <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-4 z-50 shadow-lg">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-white font-semibold">Notifications</h3>
                      <span className="text-xs text-gray-400">{notifications.length} new</span>
                    </div>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {notifications.map((notification) => (
                        <div key={notification.id} className="p-3 bg-white/5 rounded-lg border border-white/10">
                          <div className="flex items-start space-x-3">
                            {getNotificationIcon(notification.type)}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-white truncate">
                                {notification.title}
                              </p>
                              <p className="text-xs text-gray-400 mt-1">
                                {notification.message}
                              </p>
                              <p className="text-xs text-gray-500 mt-1">
                                {getRelativeTime(notification.time)}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="mt-3 pt-3 border-t border-white/10">
                      <a
                        href="/analytics"
                        className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        View all notifications
                      </a>
                    </div>
                  </div>
                )}
              </div>
            )}

           
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowUserMenu(!showUserMenu);
                  setShowNotificationsDropdown(false);
                  setShowSettings(false);
                }}
                className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10 flex items-center justify-center"
              >
                <div className="w-6 h-6 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  D
                </div>
              </button>
              
              {showUserMenu && (
                <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
                  <div className="px-3 py-2 border-b border-white/10">
                    <p className="text-sm font-medium text-white">Developer</p>
                    <p className="text-xs text-gray-400">demo@zeroday.ai</p>
                  </div>
                  <div className="py-1">
                    <a
                      href="/dashboard"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <UserCircle className="w-4 h-4" />
                      <span>Profile</span>
                    </a>
                    <a
                      href="/setup"
                      className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                    >
                      <Users className="w-4 h-4" />
                      <span>Team Info</span>
                    </a>
                    <button
                      onClick={() => window.location.href = '/login'}
                      className="flex items-center space-x-3 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg transition-colors"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

           
            <button 
              className="md:hidden p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>

        
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t border-white/10">
            <div className="flex flex-col space-y-2">
              <a href="/" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Home</a>
              <a href="/chat" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">AI Chat</a>
              <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Dashboard</a>
              <a href="/tasks" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Tasks</a>
              <a href="/upload" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Upload</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};


const ChatMessage = ({ message }: { message: ChatMessage }) => {
  const isUser = message.role === 'user';
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-[85%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div className={`p-4 rounded-xl ${
          isUser 
            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white ml-auto' 
            : 'bg-gray-800/50 border border-gray-700/50 text-gray-100 mr-auto'
        }`}>
          {!isUser && message.agent && (
            <div className="flex items-center space-x-2 mb-2 text-xs">
              <div className="w-4 h-4 bg-blue-500/20 rounded-full flex items-center justify-center">
                <Brain className="w-2 h-2 text-blue-400" />
              </div>
              <span className="text-blue-400 font-medium capitalize">{message.agent} Agent</span>
              {message.confidence && (
                <span className="text-gray-400">
                  • {Math.round(message.confidence * 100)}% confidence
                </span>
              )}
              {message.responseTime && (
                <span className="text-gray-400">• {message.responseTime}</span>
              )}
            </div>
          )}

          
          <div className="whitespace-pre-wrap">
            {message.content.split(/(\*\*.*?\*\*|•)/g).map((part, index) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return (
                  <strong key={index} className="font-semibold">
                    {part.slice(2, -2)}
                  </strong>
                );
              }
              if (part === '•') {
                return <span key={index} className="text-blue-400 font-bold">•</span>;
              }
              return part;
            })}
          </div>
          
          
          {!isUser && message.citations && message.citations.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-600/50">
              <div className="text-xs text-gray-300 mb-2 flex items-center space-x-1">
                <Quote className="w-3 h-3" />
                <span>Sources:</span>
              </div>
              <div className="space-y-2">
                {message.citations.slice(0, 3).map((citation, index) => (
                  <div key={index} className="text-xs p-2 rounded-lg border bg-blue-500/10 border-blue-500/20">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <FileText className="w-3 h-3 text-blue-400" />
                        <span className="text-blue-300">{citation.source_file}</span>
                      </div>
                      <span className="text-gray-400">
                        {Math.round(citation.relevance_score * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {isClient && (
            <div className={`text-xs mt-2 ${isUser ? 'text-blue-100' : 'text-gray-400'}`}>
              {message.timestamp}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};


const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-blue-500/20 rounded-full flex items-center justify-center">
            <Brain className="w-2 h-2 text-blue-400" />
          </div>
          <span className="text-blue-400 text-sm">AI is thinking</span>
          <div className="flex space-x-1">
            <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" />
            <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
            <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default function ChatPage() {
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('knowledge');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  
  const userDocuments: DocumentMetadata[] = [
    {
      id: '1',
      filename: 'project_docs.pdf',
      file_type: 'pdf',
      size: 1024000,
      upload_time: '2024-01-15T10:30:00Z',
      processing_status: 'indexed',
      document_count: 25,
      user_id: 'current_user',
      source_type: 'user_upload'
    },
    {
      id: '2',
      filename: 'api_reference.md',
      file_type: 'markdown',
      size: 512000,
      upload_time: '2024-01-14T15:45:00Z',
      processing_status: 'indexed',
      document_count: 12,
      user_id: 'current_user',
      source_type: 'user_upload'
    }
  ];

  const hasDocuments = userDocuments.length > 0;
  const indexedDocuments = userDocuments.filter(doc => doc.processing_status === 'indexed');

  
  useEffect(() => {
    const defaultWelcome: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: `Hello! I'm your ZeroDay AI assistant with 4 specialized agents ready to help:

🔍 **Knowledge Agent** - Code search, documentation & your uploaded documents
🎯 **Task Agent** - Personalized task suggestions  
👥 **Mentor Agent** - Senior developer guidance
📚 **Guide Agent** - Learning path generation

${hasDocuments ? `💡 **Great!** I can see you have ${indexedDocuments.length} documents ready. Ask me about them!` : '💡 **Tip:** Upload documents to enable document-aware responses with citations!'}

What would you like to explore today?`,
      timestamp: new Date().toLocaleString(),
      agent: 'knowledge'
    };
    setMessages([defaultWelcome]);

    setAgentStatus({
      knowledge: { available: true },
      task: { available: true },
      mentor: { available: true },
      guide: { available: true }
    });
  }, [hasDocuments, indexedDocuments.length]);

  
  const agents = [
    {
      id: 'auto',
      name: 'Auto Select',
      description: 'Let AI choose the best agent',
      icon: <Brain className="w-4 h-4 text-blue-400" />,
      available: true
    },
    {
      id: 'knowledge',
      name: 'Knowledge Agent',
      description: hasDocuments ? 'Your docs + platform knowledge' : 'Code search & documentation',
      icon: <BookOpen className="w-4 h-4 text-blue-400" />,
      available: agentStatus?.knowledge?.available || false
    },
    {
      id: 'task',
      name: 'Task Agent', 
      description: 'Task recommendations',
      icon: <Target className="w-4 h-4 text-orange-400" />,
      available: agentStatus?.task?.available || false
    },
    {
      id: 'mentor',
      name: 'Mentor Agent',
      description: 'Senior developer guidance', 
      icon: <Users className="w-4 h-4 text-purple-400" />,
      available: agentStatus?.mentor?.available || false
    },
    {
      id: 'guide',
      name: 'Guide Agent',
      description: 'Learning path generation',
      icon: <MessageSquare className="w-4 h-4 text-green-400" />,
      available: agentStatus?.guide?.available || false
    }
  ];

  
  const quickActions = [
    { 
      text: "Show me the codebase overview", 
      agent: 'knowledge',
      icon: <BookOpen className="w-4 h-4" />
    },
    { 
      text: "Suggest a task for my skill level", 
      agent: 'task',
      icon: <Target className="w-4 h-4" />
    },
    { 
      text: "Help me with code review best practices", 
      agent: 'mentor',
      icon: <Users className="w-4 h-4" />
    },
    { 
      text: "Create a learning plan for React", 
      agent: 'guide',
      icon: <MessageSquare className="w-4 h-4" />
    },
    { 
      text: "Find related code snippets", 
      agent: 'knowledge',
      icon: <Code className="w-4 h-4" />
    },
    { 
      text: "Summarize recent PRs", 
      agent: 'knowledge',
      icon: <TrendingUp className="w-4 h-4" />
    },
    { 
      text: "Generate onboarding checklist", 
      agent: 'guide',
      icon: <CheckCircle className="w-4 h-4" />
    },
    { 
      text: "Explain architecture patterns", 
      agent: 'mentor',
      icon: <Database className="w-4 h-4" />
    }
  ];

  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  
  const sendMessage = async (content: string, agent: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toLocaleString(),
      agent
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setIsTyping(true);

   
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I understand you asked: "${content}"

This is a **demo response** from the ${agent} agent. In the real implementation, I would:

• Process your question using **${agent} agent**
• Search through relevant knowledge base
${hasDocuments ? '• Reference your **uploaded documents**\n• Provide **citations** from your files\n' : ''}• Provide a detailed, helpful response

The response would be tailored to your specific question and context.`,
        agent: agent,
        timestamp: new Date().toLocaleString(),
        confidence: 0.95,
        responseTime: '1.2s',
        citations: hasDocuments ? [
          {
            type: 'user_document',
            source_file: 'project_docs.pdf',
            document_id: '1',
            upload_time: '2024-01-15T10:30:00Z',
            relevance_score: 0.89
          }
        ] : undefined
      };

      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
      setIsTyping(false);
    }, 2000);
  };

  const handleSendMessage = async () => {
    await sendMessage(inputValue, selectedAgent);
    setInputValue('');
  };

  const handleQuickAction = (action: Action) => {
    setInputValue(action.text);
    setSelectedAgent(action.agent);
  };

  const rightContent = (
    <div className="flex items-center space-x-3">
      {hasDocuments && (
        <div className="flex items-center space-x-2 px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-lg">
          <FileText className="w-4 h-4 text-green-400" />
          <span className="text-green-300 text-sm font-medium">
            {indexedDocuments.length} docs ready
          </span>
        </div>
      )}
      <div className="flex items-center space-x-2">
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
        <span className="text-green-400 text-sm font-medium">Live Demo</span>
      </div>
    </div>
  );

  return (
    <div className="h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex flex-col">
  
      <NavigationHeader
        title="ZeroDay"
        subtitle="Enterprise AI Developer Onboarding Platform"
        showNotifications={true}
        rightContent={rightContent}
      />

      
      <div className="flex-1 flex overflow-hidden">
        
       
        <div className="w-64 flex-shrink-0 border-r border-white/10 bg-white/5 overflow-y-auto">
          <div className="p-4 space-y-3">
            
         
            <div className="bg-white/5 border border-white/10 rounded-lg p-3">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-medium text-white flex items-center">
                  <FileText className="w-4 h-4 mr-2 text-blue-400" />
                  Documents
                </h3>
                <RefreshCw className="w-3 h-3 text-gray-400" />
              </div>
              
              {userDocuments.length === 0 ? (
                <div className="text-center py-2">
                  <p className="text-gray-400 text-xs">No files</p>
                  <a href="/upload" className="text-blue-400 text-xs hover:underline">Upload →</a>
                </div>
              ) : (
                <>
                  <div className="bg-green-500/10 border border-green-500/20 rounded p-2 mb-2">
                    <div className="text-green-300 text-xs font-medium">
                      ✓ {indexedDocuments.length} ready for chat
                    </div>
                  </div>
                  <div className="space-y-1">
                    {userDocuments.slice(0, 2).map((doc) => (
                      <div key={doc.id} className="flex items-center space-x-2 p-1">
                        <File className="w-3 h-3 text-blue-400" />
                        <span className="text-white text-xs truncate">{doc.filename}</span>
                        <CheckCircle className="w-3 h-3 text-green-400" />
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>

           
            <div className="bg-white/5 border border-white/10 rounded-lg p-3">
              <h3 className="text-sm font-medium text-white mb-3 flex items-center">
                <Brain className="w-4 h-4 mr-2 text-blue-400" />
                Agents
              </h3>
              <div className="space-y-2">
                {agents.slice(0, 4).map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent.id)}
                    className={`w-full p-2 rounded text-left transition-colors ${
                      selectedAgent === agent.id
                        ? 'bg-blue-600/40 text-white'
                        : 'hover:bg-white/10 text-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      <div className="text-blue-400">{agent.icon}</div>
                      <div className="flex-1">
                        <div className="text-xs font-medium">{agent.name}</div>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${
                        agent.available ? 'bg-green-400' : 'bg-gray-500'
                      }`} />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            
            <div className="bg-white/5 border border-white/10 rounded-lg p-3">
              <h3 className="text-sm font-medium text-white mb-3 flex items-center">
                <Zap className="w-4 h-4 mr-2 text-purple-400" />
                Suggestions
              </h3>
              <div className="space-y-1">
                {(hasDocuments 
                  ? [
                      { text: "Summarize my docs", agent: 'knowledge', icon: <Quote className="w-3 h-3" /> },
                      { text: "Find in documents", agent: 'knowledge', icon: <FileText className="w-3 h-3" /> },
                      ...quickActions.slice(4, 8) 
                    ]
                  : quickActions.slice(0, 6) 
                ).map((action, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickAction(action)}
                    className="w-full p-2 text-left bg-white/5 hover:bg-white/10 rounded text-xs text-gray-300 hover:text-white transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="text-gray-400">{action.icon}</div>
                      <span className="truncate">{action.text}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

       
        <div className="flex-1 flex flex-col">
          
          
          <div className="flex-1 overflow-y-auto">
            <div className="max-w-4xl mx-auto px-4 md:px-12">
              <div className="py-6 space-y-6">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}

                {isTyping && <TypingIndicator />}

                <div ref={messagesEndRef} />
              </div>
            </div>
          </div>

          
          <div className="flex-shrink-0 border-t border-white/10 bg-white/5 backdrop-blur-sm">
            <div className="max-w-4xl mx-auto px-4 md:px-12">
              <div className="py-4">
                <div className="flex items-end space-x-3">
                  <div className="flex-1">
                    <textarea
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder={hasDocuments && selectedAgent === 'knowledge' 
                        ? "Ask about your documents..." 
                        : `Message ${selectedAgent} agent...`
                      }
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-white placeholder-gray-400 resize-none text-sm"
                      rows={1}
                      style={{ minHeight: '44px', maxHeight: '120px' }}
                    />
                    <div className="mt-2 flex items-center justify-between">
                      <div className="text-xs text-gray-400">
                        {selectedAgent !== 'auto' && `${selectedAgent} agent selected`}
                      </div>
                      {hasDocuments && (
                        <div className="text-xs text-green-400 flex items-center space-x-1">
                          <CheckCircle className="w-3 h-3" />
                          <span>{indexedDocuments.length} docs</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <button
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? (
                      <div className="animate-spin">
                        <Zap className="w-4 h-4" />
                      </div>
                    ) : (
                      <Send className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}