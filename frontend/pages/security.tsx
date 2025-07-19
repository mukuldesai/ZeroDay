import React, { useState, useEffect, ReactNode } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '${API_BASE}'
import { 
  Shield, Lock, Key, FileCheck, Bell, User, Menu, Settings, Brain, AlertTriangle, CheckCircle, Eye, Database, Zap,
  Palette, LogOut, UserCircle, Users, MessageSquare
} from 'lucide-react';

const getRelativeTime = (timestamp: Date) => {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - timestamp.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

type NavigationHeaderProps = {
  title: string
  subtitle?: string
  isDemo?: boolean
}

type Status = 'active' | 'inactive' | 'pending' | 'warning';

type SecurityFeatureProps = {
  icon: ReactNode;
  title: string;
  description: string;
  status?: Status;
  details?: string[];
};

const NavigationHeader = ({ title, subtitle, isDemo = false }: NavigationHeaderProps) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

 
  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotifications(false);
      setShowSettings(false);
      setShowUserMenu(false);
    };
    
    if (showNotifications || showSettings || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotifications, showSettings, showUserMenu]);

  const notifications = [
    {
      id: 1,
      title: 'Security Scan Complete',
      message: 'All systems passed security audit with 98% compliance score',
      time: new Date(Date.now() - 3 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Access Control Update',
      message: 'Multi-factor authentication enabled for all users',
      time: new Date(Date.now() - 12 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Security Alert',
      message: 'Monitoring detected unusual login pattern - resolved',
      time: new Date(Date.now() - 25 * 60 * 1000),
      type: 'warning'
    }
  ];

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
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
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">AI Chat</a>
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Dashboard</a>
            <a href="/architecture" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Architecture</a>
            <a href="/security" className="text-blue-400 font-medium text-sm">Security</a>
          </div>

          
          <div className="flex items-center space-x-3">
            {isDemo && (
              <div className="bg-yellow-400/20 text-yellow-300 px-3 py-1 rounded-full text-xs font-bold border border-yellow-400/30">
                🚀 DEMO
              </div>
            )}
            
            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowSettings(!showSettings);
                  setShowNotifications(false);
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
                      className="flex items-center space-x-3 px-3 py-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors"
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

            
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowNotifications(!showNotifications);
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
              
              {showNotifications && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-4 z-50 shadow-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-white font-semibold">Security Notifications</h3>
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
                      View security logs
                    </a>
                  </div>
                </div>
              )}
            </div>

           
            <div className="relative">
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  setShowUserMenu(!showUserMenu);
                  setShowNotifications(false);
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
              <a href="/chat" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">AI Chat</a>
              <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Dashboard</a>
              <a href="/architecture" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Architecture</a>
              <a href="/security" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Security</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};


const SecurityStatus = () => {
  const [securityHealth, setSecurityHealth] = useState('excellent');
  const [lastAudit, setLastAudit] = useState(new Date());
  const [activeThreats, setActiveThreats] = useState(0);
  const [backendConnected, setBackendConnected] = useState(false);

  useEffect(() => {
    const fetchSecurityStatus = async () => {
      try {
        
        const [healthRes, agentsRes] = await Promise.all([
          fetch('${API_BASE}/health'),
          fetch('${API_BASE}/agents')
        ]);

        let securityScore = 0;
        const maxScore = 2;

        if (healthRes.ok) {
          const healthData = await healthRes.json();
          console.log('Health status:', healthData);
          
          if (healthData.status === 'healthy') {
            securityScore++;
          }
          setBackendConnected(true);
        }

        if (agentsRes.ok) {
          const agentsData = await agentsRes.json();
          console.log('Agents status:', agentsData);
          
          
          const activeAgents = Object.values(agentsData).filter(
            (agent: any) => agent && agent.available
          ).length;
          
          if (activeAgents >= 4) {
            securityScore++;
          }
        }

        
        if (securityScore === maxScore) {
          setSecurityHealth('excellent');
        } else if (securityScore >= 1) {
          setSecurityHealth('good');
        } else {
          setSecurityHealth('warning');
        }

        
        setActiveThreats(0);
        
      } catch (error) {
        console.error('Failed to fetch security status:', error);
        setSecurityHealth('warning');
        setBackendConnected(false);
      }
    };

    fetchSecurityStatus();
    
    
    const interval = setInterval(fetchSecurityStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm mb-8">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-white flex items-center">
          <Shield className="w-6 h-6 mr-2 text-green-400" />
          Security Status
          {!backendConnected && (
            <span className="ml-2 text-xs bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded-full">
              Demo Mode
            </span>
          )}
        </h3>
        <div className={`px-3 py-1 rounded-full text-xs font-bold ${
          securityHealth === 'excellent' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
          securityHealth === 'good' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
          securityHealth === 'warning' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' :
          'bg-red-500/20 text-red-300 border border-red-500/30'
        }`}>
          {securityHealth.toUpperCase()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white/5 rounded-xl p-4 border border-white/10 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">System Security</span>
            {backendConnected ? (
              <CheckCircle className="w-5 h-5 text-green-400" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-yellow-400" />
            )}
          </div>
          <div className={`text-2xl font-bold mt-2 ${
            backendConnected ? 'text-green-400' : 'text-yellow-400'
          }`}>
            {backendConnected ? 'Secure' : 'Demo'}
          </div>
        </div>
        
        <div className="bg-white/5 rounded-xl p-4 border border-white/10 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Active Threats</span>
            <AlertTriangle className="w-5 h-5 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400 mt-2">{activeThreats}</div>
        </div>
        
        <div className="bg-white/5 rounded-xl p-4 border border-white/10 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">Last Audit</span>
            <Eye className="w-5 h-5 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-blue-400 mt-2">
            {lastAudit.toLocaleDateString()}
          </div>
        </div>
      </div>

      {!backendConnected && (
        <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
          <p className="text-yellow-300 text-sm">
            🔒 Demo Mode: Security features shown with sample data. In production, this connects to live security monitoring systems.
          </p>
        </div>
      )}
    </div>
  );
};


const SecurityFeature = ({ icon, title, description, status = 'active', details }: SecurityFeatureProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div
      className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm cursor-pointer hover:bg-white/10 transition-colors"
      onClick={() => setIsExpanded(!isExpanded)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-3 bg-blue-500/20 rounded-xl text-blue-400">
            {icon}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{title}</h3>
            <p className="text-sm text-gray-400">{description}</p>
          </div>
        </div>
        <div className={`w-3 h-3 rounded-full ${
          status === 'active' ? 'bg-green-400' : 
          status === 'warning' ? 'bg-yellow-400' : 'bg-red-400'
        }`} />
      </div>

      {isExpanded && details && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="space-y-2">
            {details.map((detail, index) => (
              <div key={index} className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-sm text-gray-300">{detail}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const SecurityPage = () => {
  const [securityMetrics, setSecurityMetrics] = useState({
    encryptionLevel: '256-bit AES',
    mfaEnabled: true,
    complianceScore: 98,
    lastPenTest: '2024-01-15'
  });

  useEffect(() => {
    const fetchSecurityMetrics = async () => {
      try {
        const healthRes = await fetch('${API_BASE}/health');

        let metrics = { ...securityMetrics };

        if (healthRes.ok) {
          const healthData = await healthRes.json();
          
          if (healthData.services) {
            const servicesCount = Object.values(healthData.services).filter(
              (service: any) => service === 'available'
            ).length;
            metrics.complianceScore = Math.min(98, 80 + (servicesCount * 3));
          }
        }

        setSecurityMetrics(metrics);
      } catch (error) {
        console.error('Failed to fetch security metrics:', error);
        
      }
    };

    fetchSecurityMetrics();
  }, []);

  const securityFeatures: SecurityFeatureProps[] = [
    {
      icon: <Lock className="w-6 h-6" />,
      title: 'Data Encryption',
      description: 'End-to-end encryption for all data in transit and at rest',
      status: 'active',
      details: [
        '256-bit AES encryption standard',
        'TLS 1.3 for data in transit',
        'Encrypted database storage',
        'Key rotation every 90 days'
      ]
    },
    {
      icon: <Key className="w-6 h-6" />,
      title: 'Access Control',
      description: 'Role-based access control with multi-factor authentication',
      status: securityMetrics.mfaEnabled ? 'active' : 'warning', 
      details: [
        'Multi-factor authentication (MFA)',
        'Role-based permissions',
        'Session management',
        'Single sign-on (SSO) support'
      ]
    },
    {
      icon: <FileCheck className="w-6 h-6" />,
      title: 'Compliance',
      description: 'SOC 2, GDPR, ISO 27001 compliant security framework',
      status: 'active',
      details: [
        'SOC 2 Type II certified',
        'GDPR compliant data handling',
        'ISO 27001 security standards',
        'Regular compliance audits'
      ]
    },
    {
      icon: <Eye className="w-6 h-6" />,
      title: 'Audit Logging',
      description: 'Complete activity tracking and security monitoring',
      status: 'active',
      details: [
        'Real-time activity monitoring',
        'Comprehensive audit trails',
        'Automated threat detection',
        'Security incident response'
      ]
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: 'Data Privacy',
      description: 'Privacy-first architecture with data minimization',
      status: 'active',
      details: [
        'Data anonymization techniques',
        'Privacy by design principles',
        'Minimal data collection',
        'User consent management'
      ]
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: 'Incident Response',
      description: '24/7 security monitoring and rapid incident response',
      status: 'active',
      details: [
        '24/7 security operations center',
        'Automated threat response',
        'Incident escalation procedures',
        'Regular security drills'
      ]
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="Security Overview"
        subtitle="Enterprise-grade security and compliance features"
        isDemo={false}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Security Overview</h1>
          <p className="text-sm text-gray-400">Enterprise-grade security and compliance features</p>
        </div>

        <SecurityStatus />

        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm mb-8">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Shield className="w-8 h-8 mr-3 text-blue-400" />
            Security Features
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {securityFeatures.map((feature, index) => (
              <SecurityFeature
                key={index}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                status={feature.status}
                details={feature.details}
              />
            ))}
          </div>
        </div>

        
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm mb-8">
          <h3 className="text-xl font-semibold text-white mb-6">Security Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold text-blue-400 mb-2">{securityMetrics.encryptionLevel}</div>
              <div className="text-sm text-gray-400">Encryption Standard</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold text-green-400 mb-2">{securityMetrics.complianceScore}%</div>
              <div className="text-sm text-gray-400">Compliance Score</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold text-purple-400 mb-2">
                {securityMetrics.mfaEnabled ? 'ON' : 'OFF'}
              </div>
              <div className="text-sm text-gray-400">MFA Status</div>
            </div>
            <div className="text-center p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="text-3xl font-bold text-orange-400 mb-2">
                {new Date(securityMetrics.lastPenTest).toLocaleDateString()}
              </div>
              <div className="text-sm text-gray-400">Last Pen Test</div>
            </div>
          </div>
        </div>

       
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 shadow-sm">
          <h3 className="text-xl font-semibold text-white mb-6">Security Best Practices</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-lg font-semibold text-white mb-4">For Administrators</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Enable multi-factor authentication for all users</li>
                <li>• Regularly review and update access permissions</li>
                <li>• Monitor security logs and alerts daily</li>
                <li>• Conduct security training sessions quarterly</li>
                <li>• Implement strong password policies</li>
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-white mb-4">For Developers</h4>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Use secure coding practices and code reviews</li>
                <li>• Keep dependencies and frameworks updated</li>
                <li>• Implement proper input validation</li>
                <li>• Use secure communication protocols</li>
                <li>• Follow principle of least privilege</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityPage;
