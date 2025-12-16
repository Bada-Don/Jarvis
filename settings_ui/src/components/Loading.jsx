export default function Loading({ size = 'md', text, fullScreen = false }) {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg',
  };

  const content = (
    <div className="flex flex-col items-center justify-center animate-fade-in">
      <div className={`spinner ${sizeClasses[size]} mb-4`}></div>
      {text && (
        <p className={`text-secondary-700 font-medium ${textSizeClasses[size]}`}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-secondary-50 bg-opacity-90 flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
}

// Inline loading spinner for buttons
export function InlineLoading({ className = '' }) {
  return (
    <span className={`spinner w-4 h-4 inline-block ${className}`}></span>
  );
}
