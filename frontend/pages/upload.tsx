import React, { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '${API_BASE}'
import { 
  Database, Zap, Brain, CheckCircle, AlertCircle, Upload, TrendingUp,
  Bell, User, Menu, Settings, FileText, Code, GitBranch, Folder,
  CloudUpload, RefreshCw, Download, Eye, X, Plus, Palette, Shield,
  LogOut, UserCircle, Users, MessageSquare, ArrowRight, Clock,
  File, CheckSquare, XCircle, ExternalLink, Sparkles
} from 'lucide-react';
import { useDocuments } from '../lib/hooks/useDocuments'; 


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
  rightContent?: React.ReactNode
  showNotifications?: boolean
  showSettings?: boolean
}

const NavigationHeader = ({ title, subtitle, rightContent, showNotifications = false, showSettings = false }: NavigationHeaderProps) => { 
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  const [showSettingsDropdown, setShowSettingsDropdown] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  useEffect(() => {
    const handleClickOutside = () => {
      setShowNotificationsDropdown(false);
      setShowSettingsDropdown(false);
      setShowUserMenu(false);
    };
    
    if (showNotificationsDropdown || showSettingsDropdown || showUserMenu) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [showNotificationsDropdown, showSettingsDropdown, showUserMenu]);

  const notifications = [
    {
      id: 1,
      title: 'Upload Complete',
      message: 'Successfully processed 15 files for AI indexing',
      time: new Date(Date.now() - 2 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Knowledge Base Updated',
      message: 'Vector embeddings generated for new documents',
      time: new Date(Date.now() - 8 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Processing Ready',
      message: 'AI agents can now access your uploaded content',
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
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">AI Chat</a>
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Dashboard</a>
            <a href="/tasks" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Tasks</a>
            <a href="/upload" className="text-blue-400 font-medium text-sm">Upload</a>
          </div>

          <div className="flex items-center space-x-3">
            {rightContent}
            
            {showSettings && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowSettingsDropdown(!showSettingsDropdown);
                    setShowNotificationsDropdown(false);
                    setShowUserMenu(false);
                  }}
                  className="p-2 text-gray-400 hover:text-white transition-colors rounded-lg hover:bg-white/10"
                >
                  <Settings className="w-5 h-5" />
                </button>
                
                {showSettingsDropdown && (
                  <div className="absolute right-0 top-full mt-2 w-56 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
                    <div className="py-1">
                      <a href="/setup" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <Palette className="w-4 h-4" />
                        <span>Preferences</span>
                      </a>
                      <a href="/security" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <Shield className="w-4 h-4" />
                        <span>Security</span>
                      </a>
                      <button onClick={() => console.log('Theme toggle')} className="flex items-center space-x-3 w-full px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                        <Brain className="w-4 h-4" />
                        <span>Theme</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {showNotifications && (
              <div className="relative">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowNotificationsDropdown(!showNotificationsDropdown);
                    setShowSettingsDropdown(false);
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
                      <a href="/analytics" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
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
                  setShowSettingsDropdown(false);
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
                    <a href="/dashboard" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                      <UserCircle className="w-4 h-4" />
                      <span>Profile</span>
                    </a>
                    <a href="/setup" className="flex items-center space-x-3 px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors">
                      <Users className="w-4 h-4" />
                      <span>Team Info</span>
                    </a>
                    <button onClick={() => window.location.href = '/login'} className="flex items-center space-x-3 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg transition-colors">
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
              <a href="/tasks" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Tasks</a>
              <a href="/upload" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Upload</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};


type DocumentMetadata = {
  id: string;
  filename: string;
  file_type: string;
  size: number;
  upload_time: string;
  processing_status: 'processing' | 'indexed' | 'failed';
  document_count: number;
  user_id: string;
  source_type: string;
};


const UploadedDocumentsCard = ({ 
  documents, 
  onChatWithDocuments,
  onRefresh,
  onDeleteDocument,  
  documentsLoading  
}: { 
  documents: DocumentMetadata[];
  onChatWithDocuments: () => void;
  onRefresh: () => void;
  onDeleteDocument?: (docId: string) => Promise<boolean>;  
  documentsLoading?: boolean;  
}) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'indexed': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'processing': return <Clock className="w-4 h-4 text-yellow-400 animate-spin" />;
      case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'indexed': return 'text-green-300';
      case 'processing': return 'text-yellow-300';
      case 'failed': return 'text-red-300';
      default: return 'text-gray-300';
    }
  };

  const indexedDocs = documents.filter(d => d.processing_status === 'indexed');
  const processingDocs = documents.filter(d => d.processing_status === 'processing');

  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center">
          <FileText className="w-6 h-6 mr-2 text-blue-400" />
          Your Documents ({documents.length})
          {documentsLoading && (
            <Clock className="w-4 h-4 ml-2 text-blue-400 animate-spin" />
          )}
        </h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={onRefresh}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          {indexedDocs.length > 0 && (
            <button
              onClick={onChatWithDocuments}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all flex items-center space-x-2"
            >
              <MessageSquare className="w-4 h-4" />
              <span>Chat About Documents</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-gray-400">No documents uploaded yet</p>
          <p className="text-gray-500 text-sm">Upload files above to get started</p>
        </div>
      ) : (
        <>
          
          {indexedDocs.length > 0 && (
            <div className="bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-xl p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <h4 className="text-green-300 font-semibold">Ready for AI Chat!</h4>
                    <p className="text-green-200 text-sm">
                      {indexedDocs.length} document{indexedDocs.length > 1 ? 's' : ''} indexed and ready for questions
                    </p>
                  </div>
                </div>
                <button
                  onClick={onChatWithDocuments}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Start Chatting</span>
                </button>
              </div>
            </div>
          )}


          <div className="space-y-3 max-h-64 overflow-y-auto">
            {documents.map((doc) => (
              <div key={doc.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                <div className="flex items-center space-x-3">
                  <File className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="text-white text-sm font-medium">{doc.filename}</div>
                    <div className="text-gray-400 text-xs">
                      {doc.document_count} sections • {(doc.size / 1024).toFixed(1)} KB • {doc.source_type}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {new Date(doc.upload_time).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className={`flex items-center space-x-1 ${getStatusColor(doc.processing_status)}`}>
                    {getStatusIcon(doc.processing_status)}
                    <span className="text-sm capitalize">{doc.processing_status}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {doc.processing_status === 'indexed' && (
                      <button
                        onClick={() => onChatWithDocuments()}
                        className="p-1 text-blue-400 hover:text-blue-300 transition-colors"
                        title="Chat about this document"
                      >
                        <MessageSquare className="w-4 h-4" />
                      </button>
                    )}
                    {onDeleteDocument && (
                      <button
                        onClick={async () => {
                          if (confirm(`Delete "${doc.filename}"?`)) {
                            const success = await onDeleteDocument(doc.id);
                            if (success) {
                              onRefresh(); 
                            }
                          }
                        }}
                        className="p-1 text-red-400 hover:text-red-300 transition-colors"
                        title="Delete document"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

         
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-green-400">{indexedDocs.length}</div>
              <div className="text-green-300 text-xs">Ready</div>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-yellow-400">{processingDocs.length}</div>
              <div className="text-yellow-300 text-xs">Processing</div>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
              <div className="text-lg font-bold text-blue-400">
                {documents.reduce((sum, doc) => sum + doc.document_count, 0)}
              </div>
              <div className="text-blue-300 text-xs">Total Sections</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

type DataUploadInterfaceProps = {
  onUploadComplete: (result: any) => void;
};

const DataUploadInterface = ({ onUploadComplete }: DataUploadInterfaceProps) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadType, setUploadType] = useState('docs'); 
  const [uploadResult, setUploadResult] = useState<any>(null);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => { 
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => { 
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (!e.dataTransfer.files) return;
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => { 
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadResult(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      formData.append('file_type', uploadType); 
      formData.append('auto_index', 'true');  
      formData.append('user_id', 'current_user');

      
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 500);

      const response = await fetch('${API_BASE}/api/upload/files', {
        method: 'POST',
        body: formData
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        console.log('Upload successful:', result);
        setUploadResult(result);
        onUploadComplete?.(result);
        
        
        setTimeout(() => {
          setSelectedFiles([]);
          setUploadProgress(0);
          setUploading(false);
        }, 3000);
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6">
      <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
        <CloudUpload className="w-6 h-6 mr-2 text-blue-400" />
        Upload Data for AI Processing
      </h2>

      
      <div className="mb-6">
        <label className="block text-gray-300 text-sm font-medium mb-3">Upload Type</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setUploadType('docs')}
            className={`p-4 rounded-xl border-2 transition-all ${
              uploadType === 'docs'
                ? 'border-blue-500/50 bg-blue-600/20'
                : 'border-white/20 bg-white/5 hover:border-blue-400/50'
            }`}
          >
            <FileText className="w-6 h-6 text-blue-400 mx-auto mb-2" />
            <div className="text-white font-medium">Documents</div>
            <div className="text-gray-400 text-sm">PDFs, docs, text files</div>
          </button>
          <button
            onClick={() => setUploadType('codebase')}
            className={`p-4 rounded-xl border-2 transition-all ${
              uploadType === 'codebase'
                ? 'border-green-500/50 bg-green-600/20'
                : 'border-white/20 bg-white/5 hover:border-green-400/50'
            }`}
          >
            <Code className="w-6 h-6 text-green-400 mx-auto mb-2" />
            <div className="text-white font-medium">Code Files</div>
            <div className="text-gray-400 text-sm">JS, Python, JSON, etc.</div>
          </button>
          <button
            onClick={() => setUploadType('slack')}
            className={`p-4 rounded-xl border-2 transition-all ${
              uploadType === 'slack'
                ? 'border-purple-500/50 bg-purple-600/20'
                : 'border-white/20 bg-white/5 hover:border-purple-400/50'
            }`}
          >
            <MessageSquare className="w-6 h-6 text-purple-400 mx-auto mb-2" />
            <div className="text-white font-medium">Slack Export</div>
            <div className="text-gray-400 text-sm">Team conversations</div>
          </button>
        </div>
      </div>

     
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          dragActive
            ? 'border-blue-400 bg-blue-500/10'
            : 'border-white/30 hover:border-blue-400/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CloudUpload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-white text-lg font-semibold mb-2">
          Drop files here or click to upload
        </h3>
        <p className="text-gray-400 mb-4">
          Support for PDF, DOC, TXT, MD, JS, PY, JSON and more
        </p>
        <input
          type="file"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          id="file-upload"
          accept=".pdf,.doc,.docx,.txt,.md,.js,.py,.json,.ts,.jsx,.tsx,.zip"
        />
        <label
          htmlFor="file-upload"
          className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors cursor-pointer inline-block"
        >
          Choose Files
        </label>
      </div>

      
      {selectedFiles.length > 0 && (
        <div className="mt-6">
          <h4 className="text-white font-medium mb-4">Selected Files ({selectedFiles.length})</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/10">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <div>
                    <div className="text-white text-sm font-medium">{file.name}</div>
                    <div className="text-gray-400 text-xs">{(file.size / 1024).toFixed(1)} KB</div>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

    
      {uploading && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white text-sm font-medium">
              {uploadProgress === 100 ? 'Processing & Indexing...' : 'Uploading...'}
            </span>
            <span className="text-white text-sm">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-white/20 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
          {uploadProgress === 100 && (
            <p className="text-blue-300 text-sm mt-2">
               Auto-indexing files for AI agents...
            </p>
          )}
        </div>
      )}

    
      {uploadResult && !uploading && (
        <div className="mt-6 bg-green-500/10 border border-green-500/20 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            <span className="text-green-300 font-medium">Upload Successful!</span>
          </div>
          <p className="text-green-200 text-sm mb-3">
            Processed {uploadResult.documents_count} documents from {uploadResult.file_count} files
          </p>
          {uploadResult.indexing?.indexed && (
            <div className="bg-green-600/20 rounded-lg p-3">
              <p className="text-green-200 text-sm font-medium">🚀 Auto-indexed for AI chat!</p>
              <p className="text-green-300 text-xs">Your documents are ready for questions</p>
            </div>
          )}
        </div>
      )}

      
      {selectedFiles.length > 0 && !uploading && !uploadResult && (
        <button
          onClick={handleUpload}
          className="w-full mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all flex items-center justify-center space-x-2"
        >
          <Upload className="w-5 h-5" />
          <span>Upload & Auto-Index Files</span>
          <Sparkles className="w-5 h-5" />
        </button>
      )}
    </div>
  );
};

type UploadStatusCardProps = {
  uploadStatus: UploadStatus | null;
  error?: string | null;
  refreshStatus: () => void;
};

type UploadStatus = {
  ready_for_use: boolean;
  vector_store_status: string;
  documents_indexed: number;
  user_documents?: DocumentMetadata[];
  user_document_count?: number;
};

const UploadStatusCard = ({ uploadStatus, error, refreshStatus }: UploadStatusCardProps) => {
  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white flex items-center">
          <Database className="w-6 h-6 mr-2 text-blue-400" />
          System Status
        </h3>
        <button
          onClick={refreshStatus}
          className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
        >
          <RefreshCw className="w-5 h-5" />
        </button>
      </div>

      {error ? (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300 font-medium">Connection Error</span>
          </div>
          <p className="text-red-200 text-sm">Unable to connect to upload service. Running in demo mode.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <span className="text-gray-300">Vector Store</span>
            <div className="flex items-center space-x-2">
              {uploadStatus?.ready_for_use ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <AlertCircle className="w-5 h-5 text-yellow-400" />
              )}
              <span className={uploadStatus?.ready_for_use ? 'text-green-400' : 'text-yellow-400'}>
                {uploadStatus?.vector_store_status || 'demo_ready'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <span className="text-gray-300">Total Documents</span>
            <span className="text-blue-400 font-bold">
              {uploadStatus?.documents_indexed || 105}
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <span className="text-gray-300">Your Documents</span>
            <span className="text-purple-400 font-bold">
              {uploadStatus?.user_document_count || 0}
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
            <span className="text-gray-300">AI Status</span>
            <span className="text-green-400">
              {uploadStatus?.ready_for_use ? 'Ready for Chat' : 'Available'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

const KnowledgeBaseMetrics = ({
  codeStats,
  uploadStatus,
  error,
  lastUpdated 
}: {
  codeStats: CodeStats | null;
  uploadStatus: UploadStatus | null;
  error?: any;
  lastUpdated: string;
}) => {
  const metrics = {
    indexedFiles: codeStats?.indexed_files || uploadStatus?.documents_indexed || 105,
    status: codeStats?.status || uploadStatus?.vector_store_status || 'demo_ready',
    demoMode: codeStats?.demo_mode || true,
    lastUpdated
  };

  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6">
      <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
        <Brain className="w-6 h-6 mr-2 text-purple-400" />
        Knowledge Base Metrics
      </h3>

      {error ? (
        <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            <span className="text-yellow-300 font-medium">Demo Mode Active</span>
          </div>
          <p className="text-yellow-200 text-sm">Using synthetic data for demonstration purposes.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-400 mb-1">{metrics.indexedFiles}</div>
              <div className="text-blue-300 text-sm">Files Indexed</div>
            </div>
            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-green-400 mb-1 capitalize">{metrics.status}</div>
              <div className="text-green-300 text-sm">Status</div>
            </div>
          </div>

          <div className="bg-white/5 rounded-xl p-4 border border-white/10">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-300 text-sm">Mode</span>
              <span className={`text-sm ${metrics.demoMode ? 'text-yellow-400' : 'text-green-400'}`}>
                {metrics.demoMode ? 'Demo' : 'Production'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300 text-sm">Last Updated</span>
              <span className="text-gray-400 text-sm">{metrics.lastUpdated}</span>
            </div>
          </div>

          <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
            <h4 className="text-purple-300 font-medium mb-2">Available for AI Analysis</h4>
            <div className="space-y-1 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">Document-aware responses</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">Source citations</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-gray-300">Contextual code explanations</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

type CodeStats = {
  indexed_files: number;
  status: string;
  demo_mode: boolean;
};

type AgentStatusMap = {
  [agentId: string]: { available: boolean };
};

export default function UploadPage() {
  const [uploadStatus, setUploadStatus] = useState<UploadStatus | null>(null);
  const [codeStats, setCodeStats] = useState<CodeStats | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatusMap | null>(null);
  const [uploadError, setUploadError] = useState(null);
  const [codeError, setCodeError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState('');
  const { 
    documents: userDocuments, 
    refreshDocuments,
    deleteDocument,
    hasIndexedDocuments,
    indexedDocuments,
    loading: documentsLoading,
    error: documentsError 
  } = useDocuments({ user_id: 'current_user', auto_refresh_interval: 10000 });

  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
    refreshUploadStatus(); 
  }, []);

  const fetcher = async (url: string) => {
    try {
      const response = await fetch(`${API_BASE}${url}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error(`Error fetching ${url}:`, error);
      throw error;
    }
  };

  const refreshUploadStatus = async () => {
    try {
     
      const statusData = await fetcher('/api/upload/status');
      setUploadStatus(statusData);
      setUploadError(null);

      await refreshDocuments();

    } catch (error) {
      setUploadError(error as any);
    }
  };

  
 
  
  const handleChatWithDocuments = () => {
    if (indexedDocuments.length === 0) { 
      alert('No documents are ready for chat yet. Please wait for processing to complete.');
      return;
    }

    
    const docContext = {
      hasUserDocuments: true,
      documentCount: indexedDocuments.length,  
      documentTypes: [...new Set(indexedDocuments.map(d => d.file_type))],  
      latestUpload: indexedDocuments[0]?.upload_time  // 
    };

    
    const contextParam = encodeURIComponent(JSON.stringify(docContext));
    window.location.href = `/chat?context=${contextParam}&source=upload`;
  };

  const processingMetrics = {
    documentsIndexed: uploadStatus?.documents_indexed || codeStats?.indexed_files || 105,
    vectorStoreStatus: uploadStatus?.vector_store_status || codeStats?.status || 'demo_ready',
    readyForUse: uploadStatus?.ready_for_use || false,
    demoMode: codeStats?.demo_mode || true,
    agentsReady: agentStatus ? Object.values(agentStatus).filter((agent) => agent?.available).length : 4,
    userDocumentCount: userDocuments.length,  
    indexedUserDocs: indexedDocuments.length  
  };

  const handleUploadComplete = (result: any) => {
    console.log('Upload completed:', result);
    
    
    refreshUploadStatus();
    setLastUpdated(new Date().toLocaleString());

    setTimeout(() => {
      refreshDocuments();
    }, 1000); 
  };

  const rightContent = (
    <div className="flex items-center space-x-2">
      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
      <span className="text-green-400 text-sm font-medium">Live Demo</span>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <NavigationHeader
        title="ZeroDay"
        subtitle="AI Data Processing & Knowledge Management"
        rightContent={rightContent}
        showNotifications={true}
        showSettings={true}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">AI Data Processing Center</h1>
              <p className="text-sm text-gray-400">Upload and process your team data for AI-powered onboarding</p>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
                <Database className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-blue-300">
                  Knowledge Base: {processingMetrics.vectorStoreStatus}
                </span>
              </div>
              <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
                <Brain className="w-4 h-4 text-green-400" />
                <span className="text-sm font-medium text-green-300">
                  {processingMetrics.agentsReady}/4 Agents Ready
                </span>
              </div>
              
             
              {processingMetrics.indexedUserDocs > 0 && (
                <button
                  onClick={handleChatWithDocuments}
                  className="flex items-center space-x-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-xl hover:from-purple-700 hover:to-pink-700 transition-colors shadow-sm"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Chat Now</span>
                  <ExternalLink className="w-4 h-4" />
                </button>
              )}
              
              <button
                onClick={refreshUploadStatus}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
              >
                <TrendingUp className="w-4 h-4" />
                <span>Refresh Status</span>
              </button>
            </div>
          </div>
        </div>

        
        <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white flex items-center">
              <Database className="w-6 h-6 mr-2 text-blue-400" />
              Knowledge Base Status
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-6"> 
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-blue-300 font-medium">Total Docs</span>
                <Database className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-2xl font-bold text-blue-200">{processingMetrics.documentsIndexed}</div>
              <div className="text-sm text-blue-300">System-wide</div>
            </div>

           
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-purple-300 font-medium">Your Docs</span>
                <FileText className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-2xl font-bold text-purple-200">
                {processingMetrics.indexedUserDocs}/{processingMetrics.userDocumentCount}
              </div>
              <div className="text-sm text-purple-300">Ready/Total</div>
            </div>

            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-green-300 font-medium">Vector Store</span>
                {processingMetrics.readyForUse ? (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-yellow-400" />
                )}
              </div>
              <div className="text-2xl font-bold text-green-200 capitalize">
                {processingMetrics.vectorStoreStatus}
              </div>
              <div className="text-sm text-green-300">
                {processingMetrics.readyForUse ? 'AI queries enabled' : 'Processing required'}
              </div>
            </div>

            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-indigo-300 font-medium">AI Agents</span>
                <Brain className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-indigo-200">{processingMetrics.agentsReady}/4</div>
              <div className="text-sm text-indigo-300">Connected and ready</div>
            </div>

            <div className="bg-orange-500/10 border border-orange-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-orange-300 font-medium">Mode</span>
                <Zap className="w-5 h-5 text-orange-400" />
              </div>
              <div className="text-2xl font-bold text-orange-200">
                {processingMetrics.demoMode ? 'Demo' : 'Live'}
              </div>
              <div className="text-sm text-orange-300">
                {processingMetrics.demoMode ? 'Synthetic data' : 'Real data'}
              </div>
            </div>
          </div>

          
          {processingMetrics.indexedUserDocs > 0 && (
            <div className="mt-6 bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-green-300 font-medium">
                    🎉 {processingMetrics.indexedUserDocs} of your documents are ready for AI chat!
                  </span>
                </div>
                <button
                  onClick={handleChatWithDocuments}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <MessageSquare className="w-4 h-4" />
                  <span>Start Chatting</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>

        
        <div className="mb-8">
          <DataUploadInterface onUploadComplete={handleUploadComplete} />
        </div>

        
        {userDocuments.length > 0 && (
          <div className="mb-8">
            <UploadedDocumentsCard
              documents={userDocuments}
              onChatWithDocuments={handleChatWithDocuments}
              onRefresh={refreshUploadStatus}
              onDeleteDocument={deleteDocument}  
              documentsLoading={documentsLoading}  
            />
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <UploadStatusCard
            uploadStatus={uploadStatus}
            error={uploadError}
            refreshStatus={refreshUploadStatus}
          />
          
          <KnowledgeBaseMetrics
            codeStats={codeStats}
            uploadStatus={uploadStatus}
            error={codeError || uploadError}
            lastUpdated={lastUpdated}
          />
        </div>

        
        <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6 mb-8">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center">
            <Zap className="w-6 h-6 mr-2 text-yellow-400" />
            Processing Capabilities
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6">
              <Code className="w-8 h-8 text-blue-400 mb-4" />
              <h4 className="text-white font-semibold mb-2">Code Analysis</h4>
              <p className="text-gray-300 text-sm mb-4">
                Automatically analyze and index your codebase for intelligent search and explanations.
              </p>
              <ul className="space-y-1 text-xs text-gray-400">
                <li>• Function documentation</li>
                <li>• Code relationships</li>
                <li>• Best practices detection</li>
              </ul>
            </div>

            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
              <FileText className="w-8 h-8 text-green-400 mb-4" />
              <h4 className="text-white font-semibold mb-2">Document Processing</h4>
              <p className="text-gray-300 text-sm mb-4">
                Extract and understand content from various document formats for AI-powered insights.
              </p>
              <ul className="space-y-1 text-xs text-gray-400">
                <li>• PDF text extraction</li>
                <li>• Markdown parsing</li>
                <li>• Content summarization</li>
              </ul>
            </div>

            <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-6">
              <Brain className="w-8 h-8 text-purple-400 mb-4" />
              <h4 className="text-white font-semibold mb-2">AI Integration</h4>
              <p className="text-gray-300 text-sm mb-4">
                Connect processed data with specialized AI agents for intelligent developer assistance.
              </p>
              <ul className="space-y-1 text-xs text-gray-400">
                <li>• Document-aware responses</li>
                <li>• Source citations</li>
                <li>• Learning path generation</li>
              </ul>
            </div>
          </div>
        </div>

       
        <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6">
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Plus className="w-6 h-6 mr-2 text-blue-400" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <button
              onClick={handleChatWithDocuments}
              disabled={processingMetrics.indexedUserDocs === 0}
              className={`w-full p-4 rounded-xl transition-all duration-300 flex items-center space-x-3 ${
                processingMetrics.indexedUserDocs > 0
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:shadow-md'
                  : 'bg-white/5 text-gray-500 cursor-not-allowed'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
              <span>Chat with Documents</span>
            </button>
            <button
              onClick={() => window.location.href = '/chat'}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <Brain className="w-5 h-5 text-blue-400" />
              <span>General AI Chat</span>
            </button>
            <button
              onClick={() => window.location.href = '/dashboard'}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <TrendingUp className="w-5 h-5 text-green-400" />
              <span>View Analytics</span>
            </button>
            <button
              onClick={refreshUploadStatus}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <RefreshCw className="w-5 h-5 text-purple-400" />
              <span>Refresh All</span>
            </button>
          </div>
          <div className="mt-4 text-sm text-gray-400">
            Last updated: {lastUpdated}
          </div>
        </div>
      </div>
    </div>
  );
}
