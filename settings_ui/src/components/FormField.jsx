import { useState } from 'react';
import { api } from '../api';

export default function FormField({
  label,
  value,
  type,
  onChange,
  validation = [],
  helpText,
  placeholder,
  disabled = false,
  unit,
  min,
  max,
  step,
  options = [],
  pathType = 'file',
  fileTypes = [],
  onReset,
  highlight = '',
}) {
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  const validateValue = (val) => {
    for (const rule of validation) {
      switch (rule.type) {
        case 'required':
          if (!val && val !== 0 && val !== false) {
            return rule.message;
          }
          break;
        case 'min':
          if (typeof val === 'number' && val < rule.value) {
            return rule.message;
          }
          break;
        case 'max':
          if (typeof val === 'number' && val > rule.value) {
            return rule.message;
          }
          break;
        case 'pattern':
          if (typeof val === 'string' && !new RegExp(rule.value).test(val)) {
            return rule.message;
          }
          break;
        case 'custom':
          if (rule.validator && !rule.validator(val)) {
            return rule.message;
          }
          break;
      }
    }
    return null;
  };

  const handleChange = (newValue) => {
    const validationError = validateValue(newValue);
    setError(validationError);
    onChange(newValue);
  };

  const handleBrowse = async () => {
    setIsValidating(true);
    try {
      const path = pathType === 'folder'
        ? await api.browseFolder(`Select ${label}`)
        : await api.browseFile(`Select ${label}`, fileTypes);

      if (path) {
        handleChange(path);
      }
    } catch (err) {
      console.error('Browse error:', err);
    } finally {
      setIsValidating(false);
    }
  };

  const renderInput = () => {
    switch (type) {
      case 'text':
      case 'password':
        return (
          <input
            type={type}
            value={value || ''}
            onChange={(e) => handleChange(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            className={`
              input-field
              ${error ? 'input-error' : ''}
            `}
          />
        );

      case 'number':
        return (
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={value ?? ''}
              onChange={(e) => handleChange(parseFloat(e.target.value) || 0)}
              placeholder={placeholder}
              disabled={disabled}
              min={min}
              max={max}
              step={step}
              className={`
                input-field flex-1
                ${error ? 'input-error' : ''}
              `}
            />
            {unit && (
              <span className="text-sm font-medium text-muted-foreground bg-secondary px-3 py-2 rounded-lg whitespace-nowrap">
                {unit}
              </span>
            )}
          </div>
        );

      case 'boolean':
        return (
          <label className="flex items-center space-x-3 cursor-pointer group">
            <div className="relative">
              <input
                type="checkbox"
                checked={value || false}
                onChange={(e) => handleChange(e.target.checked)}
                disabled={disabled}
                className="sr-only"
              />
              <div
                className={`
                  w-12 h-6 rounded-full transition-all duration-200 shadow-s
                  ${value ? 'bg-primary' : 'bg-muted'}
                  ${disabled ? 'opacity-50 cursor-not-allowed' : 'group-hover:shadow-m'}
                `}
              >
                <div
                  className={`
                    absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-all duration-200 shadow-m
                    ${value ? 'transform translate-x-6' : ''}
                  `}
                />
              </div>
            </div>
            <span className={`text-sm font-medium ${value ? 'text-primary' : 'text-muted-foreground'}`}>
              {value ? 'Enabled' : 'Disabled'}
            </span>
          </label>
        );

      case 'path':
        return (
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
            <input
              type="text"
              value={value || ''}
              onChange={(e) => handleChange(e.target.value)}
              placeholder={placeholder}
              disabled={disabled}
              className={`
                input-field flex-1 font-mono text-xs sm:text-sm
                ${error ? 'input-error' : ''}
              `}
            />
            <button
              type="button"
              onClick={handleBrowse}
              disabled={disabled || isValidating}
              className="btn-secondary whitespace-nowrap w-full sm:w-auto"
            >
              {isValidating ? (
                <span className="flex items-center justify-center">
                  <span className="spinner w-4 h-4 mr-2"></span>
                  Loading...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                  Browse
                </span>
              )}
            </button>
          </div>
        );

      case 'select':
        return (
          <select
            value={value || ''}
            onChange={(e) => handleChange(e.target.value)}
            disabled={disabled}
            className={`
              input-field
              ${error ? 'input-error' : ''}
            `}
          >
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      default:
        return null;
    }
  };

  const isHighlighted = highlight && (
    label.toLowerCase().includes(highlight.toLowerCase()) ||
    String(value).toLowerCase().includes(highlight.toLowerCase())
  );

  return (
    <div className={`
      mb-4 transition-all duration-200
      ${isHighlighted ? 'bg-accent border-2 border-primary/50 rounded-lg p-2 sm:p-3 -m-1 animate-fade-in' : ''}
    `}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 space-y-1 sm:space-y-0">
        <label className="flex items-center space-x-2">
          <span className="label text-sm sm:text-base">{label}</span>
          {helpText && (
            <div className="relative">
              <button
                type="button"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                className="text-muted-foreground hover:text-foreground transition-colors duration-150"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
              {showTooltip && (
                <div className="tooltip w-64 mt-2 left-0">
                  {helpText}
                </div>
              )}
            </div>
          )}
        </label>
        {onReset && (
          <button
            type="button"
            onClick={onReset}
            className="text-xs font-medium text-primary hover:text-primary/80 transition-colors duration-150 flex items-center space-x-1"
            title="Reset to default"
          >
            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Reset</span>
          </button>
        )}
      </div>

      {renderInput()}

      {error && (
        <p className="error-text flex items-center animate-fade-in">
          <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}

      {!error && helpText && type !== 'boolean' && (
        <p className="help-text">{helpText}</p>
      )}
    </div>
  );
}
