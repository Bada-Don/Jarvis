import React from 'react';
import { cn } from './utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'outline';
  size?: 'sm' | 'lg';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'default',
  size = 'sm',
  className,
  ...props
}) => {
  const baseStyles = 'px-4 py-2 rounded-md font-medium';
  const variantStyles = variant === 'outline' ? 'border border-gray-300' : 'bg-blue-500 text-white';
  const sizeStyles = size === 'lg' ? 'text-lg' : 'text-sm';

  return (
    <button
      className={cn(baseStyles, variantStyles, sizeStyles, className)}
      {...props}
    />
  );
};