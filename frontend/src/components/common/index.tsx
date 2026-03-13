import React from 'react';
import { clsx } from 'clsx';

interface BadgeProps {
  variant?: 'success' | 'error' | 'warning' | 'info' | 'default';
  children: React.ReactNode;
  className?: string;
}

const variantClasses = {
  success: 'bg-green-100 text-green-800',
  error: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
  info: 'bg-blue-100 text-blue-800',
  default: 'bg-gray-100 text-gray-800',
};

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', children, className }) => (
  <span className={clsx('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', variantClasses[variant], className)}>
    {children}
  </span>
);

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

const buttonVariants = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
  secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-primary-500',
};

const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  children,
  className,
  ...props
}) => (
  <button
    disabled={disabled || isLoading}
    className={clsx(
      'inline-flex items-center justify-center font-medium rounded-lg border border-transparent',
      'focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-150',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      buttonVariants[variant],
      buttonSizes[size],
      className
    )}
    {...props}
  >
    {isLoading && (
      <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    )}
    {children}
  </button>
);

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
}

export const Card: React.FC<CardProps> = ({ children, className, title }) => (
  <div className={clsx('bg-white rounded-xl shadow-sm border border-gray-200', className)}>
    {title && (
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-base font-semibold text-gray-900">{title}</h3>
      </div>
    )}
    <div className="p-6">{children}</div>
  </div>
);

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, className, id, ...props }) => (
  <div className="space-y-1">
    {label && (
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">
        {label}
      </label>
    )}
    <input
      id={id}
      className={clsx(
        'block w-full rounded-lg border px-3 py-2 text-sm shadow-sm',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        'placeholder:text-gray-400',
        error ? 'border-red-300 text-red-900' : 'border-gray-300 text-gray-900',
        className
      )}
      {...props}
    />
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
);

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

export const Select: React.FC<SelectProps> = ({ label, error, options, className, id, ...props }) => (
  <div className="space-y-1">
    {label && (
      <label htmlFor={id} className="block text-sm font-medium text-gray-700">
        {label}
      </label>
    )}
    <select
      id={id}
      className={clsx(
        'block w-full rounded-lg border px-3 py-2 text-sm shadow-sm bg-white',
        'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        error ? 'border-red-300' : 'border-gray-300',
        className
      )}
      {...props}
    >
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
);

export const Spinner: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={clsx('animate-spin h-6 w-6 text-primary-600', className)}
    fill="none"
    viewBox="0 0 24 24"
  >
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
  </svg>
);

export const EmptyState: React.FC<{ message: string; icon?: React.ReactNode }> = ({ message, icon }) => (
  <div className="flex flex-col items-center justify-center py-12 text-center">
    {icon && <div className="mb-4 text-gray-400">{icon}</div>}
    <p className="text-gray-500 text-sm">{message}</p>
  </div>
);
