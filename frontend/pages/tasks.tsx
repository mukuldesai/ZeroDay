import React, { useState, useEffect, ReactNode } from 'react';
import { 
  CheckSquare, Plus, Lightbulb, MessageSquare, GitBranch, TrendingUp, Download,
  Bell, User, Menu, Settings, Brain, Search, Grid, List, Calendar,
  Clock, MoreHorizontal, Edit2, Trash2, LucideIcon, CheckCircle, AlertCircle,
  Palette, Shield, LogOut, UserCircle, Users, Target
} from 'lucide-react';

const getRelativeTime = (timestamp: Date) => {
  const now = new Date();
  const seconds = Math.floor((now.getTime() - timestamp.getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
};

export type TaskStatus = 'todo' | 'in-progress' | 'completed';
export type TaskPriority = 'low' | 'medium' | 'high';
export type ViewMode = 'grid' | 'list' | 'kanban';

type NavigationHeaderProps = {
  title: string
  subtitle?: string
  rightContent?: React.ReactNode
  showNotifications?: boolean
  showSettings?: boolean
}

type ButtonProps = {
  onClick: () => void
  className?: string
  children: React.ReactNode
}



const MotionButton = ({ onClick, className, children }: ButtonProps) => {
  return (
    <button
      onClick={onClick}
      className={className}
    >
      {children}
    </button>
  );
};


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
      title: 'New Task Available',
      message: 'Payment Gateway Integration task has been assigned',
      time: new Date(Date.now() - 5 * 60 * 1000),
      type: 'success'
    },
    {
      id: 2,
      title: 'Task Completed',
      message: 'User Dashboard Redesign milestone reached',
      time: new Date(Date.now() - 15 * 60 * 1000),
      type: 'info'
    },
    {
      id: 3,
      title: 'Due Date Reminder',
      message: 'React component task due in 2 days',
      time: new Date(Date.now() - 25 * 60 * 1000),
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
            <a href="/tasks" className="text-blue-400 font-medium text-sm">Tasks</a>
            <a href="/upload" className="text-gray-300 hover:text-white transition-colors text-sm font-medium">Upload</a>
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
              <a href="/tasks" className="text-blue-400 py-2 px-2 rounded-lg bg-blue-500/10">Tasks</a>
              <a href="/upload" className="text-gray-300 hover:text-white transition-colors py-2 px-2 rounded-lg hover:bg-white/10">Upload</a>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

interface StatsCardProps {
  icon: React.ReactNode;
  title: string;
  value: number | string;
  change: string;
  color: string;
}

const StatsCard = ({ icon, title, value, change, color }: StatsCardProps) => {
  return (
    <div className={`${color} rounded-xl p-6 text-white relative overflow-hidden backdrop-blur-sm shadow-sm border border-white/10`}>
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16"></div>
      <div className="relative">
        <div className="flex items-center justify-between mb-2">
          {icon}
          <span className="text-xs bg-white/20 px-2 py-1 rounded-full">{change}</span>
        </div>
        <div className="text-2xl font-bold mb-1">{value}</div>
        <div className="text-sm opacity-90">{title}</div>
      </div>
    </div>
  );
};

type ViewModeToggleProps = {
  viewMode: ViewMode;
  onViewModeChange: (mode: ViewMode) => void;
};

const ViewModeToggle = ({ viewMode, onViewModeChange }: ViewModeToggleProps) => {
  const modes: { id: ViewMode; icon: LucideIcon; label: string }[] = [
    { id: 'grid', icon: Grid, label: 'Grid' },
    { id: 'list', icon: List, label: 'List' },
    { id: 'kanban', icon: Calendar, label: 'Kanban' }
  ];

  return (
    <div className="flex bg-white/10 rounded-xl p-1 border border-white/20">
      {modes.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          onClick={() => onViewModeChange(id)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm transition-all ${
            viewMode === id 
              ? 'bg-blue-600 text-white shadow-sm' 
              : 'text-gray-300 hover:text-white hover:bg-white/10'
          }`}
        >
          <Icon className="w-4 h-4" />
          <span className="hidden sm:block">{label}</span>
        </button>
      ))}
    </div>
  );
};

type Filters = {
  status: string;
  priority: string;
  assignee?: string;
};

type TaskFiltersProps = {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  filters: Filters;
  onFilterChange: (partial: Partial<Filters>) => void;
  sortBy: string;
  onSortChange: (sort: string) => void;
  activeFiltersCount: number;
};

const TaskFilters = ({ searchQuery, onSearchChange, filters, onFilterChange, sortBy, onSortChange, activeFiltersCount }: TaskFiltersProps) => {
  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6 mb-8">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search tasks..."
            className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div className="flex items-center space-x-4">
          <select
            value={filters.status}
            onChange={(e) => onFilterChange({ status: e.target.value })}
            className="bg-white/10 border border-white/20 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="todo">To Do</option>
            <option value="in-progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>

          <select
            value={filters.priority}
            onChange={(e) => onFilterChange({ priority: e.target.value })}
            className="bg-white/10 border border-white/20 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Priority</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value)}
            className="bg-white/10 border border-white/20 text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500"
          >
            <option value="created">Created Date</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="title">Title</option>
          </select>

          {activeFiltersCount > 0 && (
            <div className="bg-blue-500/20 text-blue-300 px-3 py-2 rounded-lg text-sm border border-blue-500/30">
              {activeFiltersCount} filter{activeFiltersCount > 1 ? 's' : ''}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

type Task = {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  status: 'todo' | 'in-progress' | 'completed';
  dueDate: string;
  assignee?: string;
  estimatedTime?: string;
  progress?: number;
  tags?: string[];
};

type TaskCardProps = {
  task: Task;
  onStatusChange: (id: string, newStatus: Task['status']) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
};

const TaskCard = ({ task, onStatusChange, onEdit, onDelete }: TaskCardProps) => {
  const [showMenu, setShowMenu] = useState(false);

  const getPriorityColor = (priority: TaskPriority): string => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      case 'low': return 'bg-green-500/20 text-green-300 border-green-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  const getStatusColor = (status: TaskStatus): string => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'in-progress': return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'todo': return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6 relative">
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-white font-semibold text-lg">{task.title}</h3>
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <MoreHorizontal className="w-4 h-4" />
          </button>
          {showMenu && (
            <div className="absolute right-0 top-full mt-2 bg-gray-900/80 backdrop-blur-md border border-white/20 rounded-xl p-2 z-50 shadow-lg">
              <button onClick={() => onEdit(task)} className="flex items-center space-x-2 w-full px-3 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg">
                <Edit2 className="w-4 h-4" />
                <span>Edit</span>
              </button>
              <button onClick={() => onDelete(task.id)} className="flex items-center space-x-2 w-full px-3 py-2 text-red-300 hover:text-red-200 hover:bg-red-500/10 rounded-lg">
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            </div>
          )}
        </div>
      </div>

      <p className="text-gray-300 text-sm mb-4 line-clamp-3">{task.description}</p>

      <div className="flex items-center space-x-2 mb-4">
        <span className={`px-2 py-1 rounded-full text-xs border ${getPriorityColor(task.priority)}`}>
          {task.priority}
        </span>
        <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(task.status)}`}>
          {task.status}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2 text-gray-400 text-xs">
          <Clock className="w-4 h-4" />
          <span>{task.dueDate}</span>
        </div>
        <button
          onClick={() => onStatusChange(task.id, task.status === 'completed' ? 'todo' : 'completed')}
          className={`px-3 py-1 rounded-lg text-xs transition-all ${
            task.status === 'completed'
              ? 'bg-green-500/20 text-green-300 border border-green-500/30'
              : 'bg-blue-500/20 text-blue-300 border border-blue-500/30 hover:bg-blue-500/30'
          }`}
        >
          {task.status === 'completed' ? 'Completed' : 'Mark Complete'}
        </button>
      </div>
    </div>
  );
};

type TaskListViewProps = {
  tasks: Task[];
  onStatusChange: (taskId: string, newStatus: Task['status']) => void;
};

const TaskListView = ({ tasks, onStatusChange }: TaskListViewProps) => {
  return (
    <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm overflow-hidden">
      <div className="grid grid-cols-12 gap-4 p-4 bg-white/5 border-b border-white/10 text-gray-300 text-sm font-medium">
        <div className="col-span-4">Task</div>
        <div className="col-span-2">Status</div>
        <div className="col-span-2">Priority</div>
        <div className="col-span-2">Due Date</div>
        <div className="col-span-2">Actions</div>
      </div>
      {tasks.map((task) => (
        <div
          key={task.id}
          className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 hover:bg-white/5 transition-colors"
        >
          <div className="col-span-4">
            <h4 className="text-white font-medium">{task.title}</h4>
            <p className="text-gray-400 text-sm truncate">{task.description}</p>
          </div>
          <div className="col-span-2">
            <span className={`px-2 py-1 rounded-full text-xs ${
              task.status === 'completed' ? 'bg-green-500/20 text-green-300' :
              task.status === 'in-progress' ? 'bg-blue-500/20 text-blue-300' :
              'bg-gray-500/20 text-gray-300'
            }`}>
              {task.status}
            </span>
          </div>
          <div className="col-span-2">
            <span className={`px-2 py-1 rounded-full text-xs ${
              task.priority === 'high' ? 'bg-red-500/20 text-red-300' :
              task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
              'bg-green-500/20 text-green-300'
            }`}>
              {task.priority}
            </span>
          </div>
          <div className="col-span-2 text-gray-300 text-sm">{task.dueDate}</div>
          <div className="col-span-2">
            <button
              onClick={() => onStatusChange(task.id, task.status === 'completed' ? 'todo' : 'completed')}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              Toggle Status
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

type KanbanColumn = {
  id: string;
  title: string;
  color: string;
  tasks: Task[];
};

type KanbanBoardProps = {
  kanbanColumns: KanbanColumn[];
  onDragEnd: (result: any) => void;
};

const KanbanBoard = ({ kanbanColumns, onDragEnd }: KanbanBoardProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {kanbanColumns.map((column) => (
        <div key={column.id} className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-4">
          <h3 className="text-white font-semibold mb-4 flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${column.color}`}></div>
            {column.title} ({column.tasks.length})
          </h3>
          <div className="space-y-3">
            {column.tasks.map((task) => (
              <div
                key={task.id}
                className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-3"
              >
                <h4 className="text-white text-sm font-medium mb-2">{task.title}</h4>
                <p className="text-gray-400 text-xs mb-2 line-clamp-2">{task.description}</p>
                <div className="flex items-center justify-between">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    task.priority === 'high' ? 'bg-red-500/20 text-red-300' :
                    task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300' :
                    'bg-green-500/20 text-green-300'
                  }`}>
                    {task.priority}
                  </span>
                  <span className="text-gray-400 text-xs">{task.dueDate}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

type CreateTaskModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onCreateTask: (task: {
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
    status: 'todo' | 'in-progress' | 'completed';
    dueDate: string;
  }) => void;
};

type TaskFormData = {
  title: string;
  description: string;
  priority: TaskPriority;
  status: TaskStatus;
  dueDate: string;
};

const CreateTaskModal = ({ isOpen, onClose, onCreateTask }: CreateTaskModalProps) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'todo',
    dueDate: ''
  });

  const handleSubmit = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    onCreateTask(formData);
    setFormData({ title: '', description: '', priority: 'medium', status: 'todo', dueDate: '' });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900/80 backdrop-blur-md rounded-xl p-6 border border-white/20 max-w-md w-full shadow-lg" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-xl font-semibold text-white mb-4">Create New Task</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Task title"
            value={formData.title}
            onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            className="w-full p-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400"
          />
          <textarea
            placeholder="Task description"
            value={formData.description}
            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            className="w-full p-3 bg-white/10 border border-white/20 rounded-xl text-white placeholder-gray-400 h-24"
          />
          <div className="grid grid-cols-2 gap-4">
            <select
              value={formData.priority}
              onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as TaskPriority }))}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
            <input
              type="date"
              value={formData.dueDate}
              onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value }))}
              className="p-3 bg-white/10 border border-white/20 rounded-xl text-white"
            />
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="flex-1 p-3 bg-white/10 text-gray-300 rounded-xl hover:bg-white/20 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={!formData.title}
              className="flex-1 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Create Task
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

type EmptyStateProps = {
  icon: React.ReactNode;
  title: string;
  description: string;
  actionLabel: string;
  onAction: () => void;
};

const EmptyState = ({ icon, title, description, actionLabel, onAction }: EmptyStateProps) => {
  return (
    <div className="text-center py-12">
      <div className="text-gray-400 mb-4">{icon}</div>
      <h3 className="text-white text-lg font-semibold mb-2">{title}</h3>
      <p className="text-gray-400 mb-6">{description}</p>
      <button
        onClick={onAction}
        className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors"
      >
        {actionLabel}
      </button>
    </div>
  );
};

const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [sortBy, setSortBy] = useState('created');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    assignee: ''
  });

  const defaultDemoTasks: Task[] = [
    {
      id: 'task_1_1',
      title: 'Set up Payment Gateway Integration environment',
      description: 'Initialize development environment for Payment Gateway Integration',
      status: 'todo',
      priority: 'high',
      dueDate: '2025-08-15',
      assignee: 'Sarah Chen',
      estimatedTime: '2 hours',
      progress: 0,
      tags: ['Stripe API', 'React', 'Node.js']
    },
    {
      id: 'task_1_2',
      title: 'Implement core features for Payment Gateway Integration',
      description: 'Develop main functionality using Stripe API, React, Node.js',
      status: 'in-progress',
      priority: 'high',
      dueDate: '2025-08-15',
      assignee: 'Sarah Chen',
      estimatedTime: '1 day',
      progress: 75,
      tags: ['Stripe API', 'React', 'Node.js']
    },
    {
      id: 'task_2_1',
      title: 'Set up User Dashboard Redesign environment',
      description: 'Initialize development environment for User Dashboard Redesign',
      status: 'todo',
      priority: 'medium',
      dueDate: '2025-09-01',
      assignee: 'Sarah Chen',
      estimatedTime: '2 hours',
      progress: 0,
      tags: ['React', 'TypeScript', 'Tailwind CSS']
    },
    {
      id: 'task_3_1',
      title: 'Code Review Best Practices',
      description: 'Learn and implement code review standards for team collaboration',
      status: 'completed',
      priority: 'medium',
      dueDate: '2025-07-20',
      assignee: 'You',
      estimatedTime: '3 hours',
      progress: 100,
      tags: ['Code Review', 'Best Practices']
    }
  ];

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://127.0.0.1:8000/demo/tasks/startup');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      
      const transformedTasks = data.map((task: any) => ({
        id: task.id,
        title: task.title,
        description: task.description,
        status: task.status.replace('-', '_') as TaskStatus,
        priority: task.priority,
        dueDate: task.deadline,
        assignee: task.assignee,
        estimatedTime: task.estimatedTime,
        progress: task.progress,
        tags: task.tags
      }));
      
      setTasks(transformedTasks);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch tasks:', err);
      setError('Failed to load tasks');
      setTasks(defaultDemoTasks);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !filters.status || task.status === filters.status;
    const matchesPriority = !filters.priority || task.priority === filters.priority;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const updateFilter = (key: keyof typeof filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const activeFiltersCount = Object.values(filters).filter(value => value !== '').length;

  const taskStats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === 'completed').length,
    inProgress: tasks.filter(t => t.status === 'in-progress').length,
    avgCompletionTime: '2.5 days'
  };

  const kanbanColumns = [
    {
      id: 'todo',
      title: 'To Do',
      color: 'bg-gray-400',
      tasks: filteredTasks.filter(t => t.status === 'todo')
    },
    {
      id: 'in-progress',
      title: 'In Progress',
      color: 'bg-blue-400',
      tasks: filteredTasks.filter(t => t.status === 'in-progress')
    },
    {
      id: 'completed',
      title: 'Completed',
      color: 'bg-green-400',
      tasks: filteredTasks.filter(t => t.status === 'completed')
    }
  ];

  const handleStatusChange = async (taskId: string, newStatus: TaskStatus) => {
    try {
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));

      const response = await fetch(`http://127.0.0.1:8000/api/suggest_task`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: taskId,
          status: newStatus,
          progress: newStatus === 'completed' ? 100 : 50,
          notes: `Status updated to ${newStatus}`,
          user_id: "demo_user"
        })
      });

      if (!response.ok) {
        console.warn('Task update API failed, continuing with local update');
      }
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  const handleCreateTask = async (taskData: TaskFormData) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/suggest_task', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: "demo_user",
          user_role: "frontend",
          experience_level: "intermediate",
          task_type: "feature",
          difficulty: "medium",
          task_data: taskData
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Task created successfully:', result);
        
        const newTask: Task = {
          id: `task_${Date.now()}`,
          title: taskData.title,
          description: taskData.description,
          status: taskData.status,
          priority: taskData.priority,
          dueDate: taskData.dueDate,
          assignee: "You"
        };
        
        setTasks(prev => [...prev, newTask]);
      } else {
        const errorText = await response.text();
        console.error('Backend rejected task creation:', errorText);
        throw new Error(`Failed to create task: ${errorText}`);

      }
    } catch (error) {
      console.error('Failed to create task:', error);
      
      const newTask: Task = {
        id: `task_${Date.now()}`,
        title: taskData.title,
        description: taskData.description,
        status: taskData.status,
        priority: taskData.priority,
        dueDate: taskData.dueDate,
        assignee: "You"
      };
      
      setTasks(prev => [...prev, newTask]);
    }
  };
  
  const handleEdit = (task: Task) => {
    console.log('Editing task:', task);
  };

  const handleDelete = (taskId: string) => {
    setTasks(prev => prev.filter(task => task.id !== taskId));
  };

  const handleDragEnd = (result: unknown) => {
    console.log('Drag ended:', result);
  };

  return {
    tasks: filteredTasks,
    kanbanColumns,
    viewMode,
    setViewMode,
    sortBy,
    setSortBy,
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    activeFiltersCount,
    taskStats,
    handleStatusChange,
    handleEdit,
    handleDelete,
    handleDragEnd,
    handleCreateTask,
    loading,
    error,
    refreshTasks: fetchTasks
  };
};

export default function TasksPage() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');
  
  const {
    tasks,
    kanbanColumns,
    viewMode,
    setViewMode,
    sortBy,
    setSortBy,
    searchQuery,
    setSearchQuery,
    filters,
    updateFilter,
    activeFiltersCount,
    taskStats,
    handleStatusChange,
    handleEdit,
    handleDelete,
    handleDragEnd,
    handleCreateTask,
    loading,
    error
  } = useTasks();

  useEffect(() => {
    setLastUpdated(new Date().toLocaleString());
  }, []);

  const handleCreateTaskSubmit = async (taskData: TaskFormData) => { 
    await handleCreateTask(taskData);
    setShowCreateModal(false);
  };

  
  const rightContent = (
    <div className="flex items-center space-x-2">
      <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
      <span className="text-green-400 text-sm font-medium">Live Demo</span>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">  
      <NavigationHeader
        title="ZeroDay"
        subtitle="Task Management & AI-Powered Onboarding"
        rightContent={rightContent}
        showNotifications={true}
        showSettings={true}
      />

      <div className="max-w-7xl mx-auto px-6 py-6">
        
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Task Management</h1>
              <p className="text-sm text-gray-400">Track and manage your onboarding tasks with AI assistance</p>
            </div>
            
            
            <div className="flex items-center space-x-3">
              <ViewModeToggle viewMode={viewMode} onViewModeChange={setViewMode} />
              <button
                onClick={() => setShowCreateModal(true)}
                className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-2 rounded-xl hover:shadow-lg transition-all duration-300 flex items-center space-x-2 shadow-sm"
              >
                <Plus className="w-4 h-4" />
                <span>Create Task</span>
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-8 bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4">
            <div className="text-yellow-300 font-medium">Running in Demo Mode</div>
            <div className="text-yellow-200 text-sm">Using fallback data. API connection failed.</div>
          </div>
        )}

        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            icon={<CheckSquare className="w-6 h-6" />}
            title="Total Tasks"
            value={taskStats.total}
            change="+3 this week"
            color="bg-gradient-to-r from-blue-600/20 to-indigo-600/20"
          />
          <StatsCard
            icon={<Target className="w-6 h-6" />}
            title="Completed"
            value={taskStats.completed}
            change="+2 today"
            color="bg-gradient-to-r from-green-600/20 to-emerald-600/20"
          />
          <StatsCard
            icon={<Clock className="w-6 h-6" />}
            title="In Progress"
            value={taskStats.inProgress}
            change="+1 today"
            color="bg-gradient-to-r from-orange-600/20 to-red-600/20"
          />
          <StatsCard
            icon={<TrendingUp className="w-6 h-6" />}
            title="Avg. Completion"
            value={taskStats.avgCompletionTime}
            change="-20min"
            color="bg-gradient-to-r from-purple-600/20 to-pink-600/20"
          />
        </div>

        <TaskFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          filters={filters}
          onFilterChange={(partial) => {
            const [key, value] = Object.entries(partial)[0] as [keyof typeof filters, string];
            updateFilter(key, value);
          }}
          sortBy={sortBy}
          onSortChange={setSortBy}
          activeFiltersCount={activeFiltersCount}
        />

        
        {viewMode === 'grid' && (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onStatusChange={handleStatusChange}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}

        {viewMode === 'list' && (
          <div className="mb-8">
            <TaskListView 
              tasks={tasks}
              onStatusChange={handleStatusChange}
            />
          </div>
        )}

        {viewMode === 'kanban' && (
          <div className="mb-8">
            <KanbanBoard 
              kanbanColumns={kanbanColumns}
              onDragEnd={handleDragEnd}
            />
          </div>
        )}

        {tasks.length === 0 && (
          <div className="mb-8">
            <EmptyState
              icon={<CheckSquare className="w-12 h-12" />}
              title="No tasks found"
              description={
                searchQuery || activeFiltersCount > 0
                  ? 'Try adjusting your search or filters'
                  : 'Create your first task to get started'
              }
              actionLabel="Create Task"
              onAction={() => setShowCreateModal(true)}
            />
          </div>
        )}

        
        <div className="rounded-xl bg-white/5 border border-white/10 shadow-sm p-6"> 
          <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
            <Lightbulb className="w-6 h-6 mr-2 text-blue-400" />
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MotionButton
              onClick={() => window.location.href = '/chat'}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <MessageSquare className="w-5 h-5 text-blue-400" />
              <span>Ask for Task Help</span>
            </MotionButton>
            <MotionButton
              onClick={() => console.log('Code review')}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <GitBranch className="w-5 h-5 text-green-400" />
              <span>View Code Review</span>
            </MotionButton>
            <MotionButton
              onClick={() => window.location.href = '/dashboard'}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <TrendingUp className="w-5 h-5 text-purple-400" />
              <span>View Progress</span>
            </MotionButton>
            <MotionButton
              onClick={() => console.log('Export tasks')}
              className="w-full bg-white/10 text-gray-300 p-4 rounded-xl hover:bg-white/20 hover:shadow-md transition-all duration-300 flex items-center space-x-3"
            >
              <Download className="w-5 h-5 text-indigo-400" />
              <span>Export Tasks</span>
            </MotionButton>
          </div>
          <div className="mt-4 text-sm text-gray-400">
            Last updated: {lastUpdated}
          </div>
        </div>
      </div>

      <CreateTaskModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCreateTask={handleCreateTaskSubmit}
      />
    </div>
  );
}