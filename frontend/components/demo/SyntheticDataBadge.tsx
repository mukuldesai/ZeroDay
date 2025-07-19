interface SyntheticDataBadgeProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'subtle' | 'warning';
  showIcon?: boolean;
  className?: string;
}

export default function SyntheticDataBadge({ 
  size = 'md', 
  variant = 'default', 
  showIcon = true,
  className = '' 
}: SyntheticDataBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };

  const variantClasses = {
    default: 'bg-green-100 text-green-800 border border-green-200',
    subtle: 'bg-gray-100 text-gray-600 border border-gray-200',
    warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200'
  };

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4', 
    lg: 'w-5 h-5'
  };

  return (
    <span className={`inline-flex items-center space-x-1 rounded-full font-medium ${sizeClasses[size]} ${variantClasses[variant]} ${className}`}>
      {showIcon && (
        <svg className={iconSize[size]} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )}
      <span>Demo Data</span>
    </span>
  );
}