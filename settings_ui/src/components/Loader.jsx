import React from 'react';
import JarvisLogo from './JarvisLogo';
import { useTheme } from './ThemeProvider';

export default function Loader({ 
  variant = 'spinner', 
  size = 'md', 
  text, 
  className = '',
  fullScreen = false
}) {
  const { theme } = useTheme();
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const textSizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg',
  };

  const renderLoader = () => {
    switch (variant) {
      case 'jarvis':
        return (
          <div className={`relative flex items-center justify-center ${className}`}>
            <JarvisLogo 
              className={`${sizeClasses[size]} text-primary animate-pulse`} 
              style={{ filter: isDark ? 'drop-shadow(0 0 8px rgba(22, 226, 215, 0.5))' : 'none' }}
            />
            <div className={`absolute inset-0 ${sizeClasses[size]} border-2 border-primary/30 rounded-full animate-spin-slow`} />
          </div>
        );
      case 'dots':
        return (
          <div className={`flex space-x-1 ${className}`}>
            <div className={`w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]`} />
            <div className={`w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]`} />
            <div className={`w-2 h-2 bg-primary rounded-full animate-bounce`} />
          </div>
        );
      case 'spinner':
      default:
        return (
          <div 
            className={`
              ${sizeClasses[size]} 
              border-2 border-muted border-t-primary 
              rounded-full animate-spin 
              ${className}
            `} 
          />
        );
    }
  };

  const content = (
    <div className={`flex flex-col items-center justify-center gap-3 ${fullScreen ? 'animate-fade-in' : ''}`}>
      {renderLoader()}
      {text && (
        <p className={`text-muted-foreground font-medium animate-pulse ${textSizeClasses[size]}`}>
          {text}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 shadow-l">
        {content}
      </div>
    );
  }

  return content;
}
