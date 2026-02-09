import { useState, useEffect } from 'react';
import { Folder, AlertCircle, CheckCircle, Home, FileText, Download } from 'lucide-react';
import { api } from '../../api';

/**
 * PathConfigStep Component
 * 
 * Step for configuring system paths (Desktop, Documents, Downloads).
 * Validates paths exist before allowing progression.
 * 
 * Requirements: 2.5, 2.7, 10.1
 */
export default function PathConfigStep({ paths, onChange, onValidationChange }) {
  const [validating, setValidating] = useState(false);
  const [errors, setErrors] = useState({
    desktop: null,
    documents: null,
    downloads: null,
  });
  const [touched, setTouched] = useState({
    desktop: false,
    documents: false,
    downloads: false,
  });

  // Validate paths whenever they change
  useEffect(() => {
    validatePaths();
  }, [paths.desktop, paths.documents, paths.downloads]);

  const validatePaths = async () => {
    const newErrors = {
      desktop: null,
      documents: null,
      downloads: null,
    };

    let allValid = true;

    // Desktop path is required
    if (!paths.desktop || paths.desktop.trim() === '') {
      newErrors.desktop = 'Desktop path is required';
      allValid = false;
    }

    // Documents path is required
    if (!paths.documents || paths.documents.trim() === '') {
      newErrors.documents = 'Documents path is required';
      allValid = false;
    }

    // Downloads path is required
    if (!paths.downloads || paths.downloads.trim() === '') {
      newErrors.downloads = 'Downloads path is required';
      allValid = false;
    }

    setErrors(newErrors);
    onValidationChange(allValid);
  };

  const handlePathChange = (pathType, value) => {
    onChange({ [pathType]: value });
    setTouched((prev) => ({ ...prev, [pathType]: true }));
  };

  const handleBrowse = async (pathType) => {
    try {
      const selectedPath = await api.browseFolder(`Select ${pathType} folder`);
      if (selectedPath) {
        handlePathChange(pathType, selectedPath);
      }
    } catch (error) {
      console.error(`Failed to browse for ${pathType}:`, error);
    }
  };

  const handleValidatePath = async (pathType, path) => {
    if (!path || path.trim() === '') {
      return;
    }

    try {
      const isValid = await api.validatePath(path, true);
      if (!isValid) {
        setErrors((prev) => ({
          ...prev,
          [pathType]: 'Path does not exist or is not accessible',
        }));
        onValidationChange(false);
      } else {
        setErrors((prev) => ({
          ...prev,
          [pathType]: null,
        }));
      }
    } catch (error) {
      console.error(`Failed to validate ${pathType} path:`, error);
      setErrors((prev) => ({
        ...prev,
        [pathType]: 'Failed to validate path',
      }));
      onValidationChange(false);
    }
  };

  const handleAutoDetect = () => {
    // Auto-detect common Windows paths
    const username = window.navigator.userAgent.includes('Windows') ? 'User' : 'user';
    
    onChange({
      desktop: `C:\\Users\\${username}\\Desktop`,
      documents: `C:\\Users\\${username}\\Documents`,
      downloads: `C:\\Users\\${username}\\Downloads`,
    });

    setTouched({
      desktop: true,
      documents: true,
      downloads: true,
    });
  };

  const PathInput = ({ pathType, icon: Icon, label, placeholder }) => {
    const hasError = touched[pathType] && errors[pathType];

    return (
      <div>
        <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
          <div className="flex items-center gap-2">
            <Icon className="w-4 h-4" />
            <span>{label}</span>
            <span className="text-red-500">*</span>
          </div>
        </label>
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={paths[pathType]}
              onChange={(e) => handlePathChange(pathType, e.target.value)}
              onBlur={() => handleValidatePath(pathType, paths[pathType])}
              placeholder={placeholder}
              className={`w-full px-4 py-3 rounded-lg border ${
                hasError
                  ? 'border-red-500 focus:ring-red-500'
                  : 'border-neutral-300 dark:border-neutral-700 focus:ring-primary'
              } bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 focus:outline-none focus:ring-2 transition-colors`}
            />
          </div>
          <button
            onClick={() => handleBrowse(pathType)}
            className="px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors flex items-center gap-2"
          >
            <Folder className="w-5 h-5" />
            <span className="hidden sm:inline">Browse</span>
          </button>
        </div>
        {hasError && (
          <div className="flex items-center gap-2 mt-2 text-sm text-red-600 dark:text-red-400">
            <AlertCircle className="w-4 h-4" />
            <span>{errors[pathType]}</span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Info Box */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-900 dark:text-blue-100">
            <p className="font-medium mb-1">System Paths Configuration</p>
            <p className="text-blue-700 dark:text-blue-300">
              Configure the paths to your Desktop, Documents, and Downloads folders. JARVIS uses
              these paths to interact with files on your system.
            </p>
          </div>
        </div>
      </div>

      {/* Auto-Detect Button */}
      <button
        onClick={handleAutoDetect}
        className="w-full px-4 py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 bg-primary/10 text-primary hover:bg-primary/20 border border-primary/30"
      >
        <CheckCircle className="w-5 h-5" />
        <span>Auto-Detect Paths</span>
      </button>

      {/* Desktop Path */}
      <PathInput
        pathType="desktop"
        icon={Home}
        label="Desktop Path"
        placeholder="C:\Users\YourName\Desktop"
      />

      {/* Documents Path */}
      <PathInput
        pathType="documents"
        icon={FileText}
        label="Documents Path"
        placeholder="C:\Users\YourName\Documents"
      />

      {/* Downloads Path */}
      <PathInput
        pathType="downloads"
        icon={Download}
        label="Downloads Path"
        placeholder="C:\Users\YourName\Downloads"
      />

      {/* Validation Status */}
      {!errors.desktop && !errors.documents && !errors.downloads && 
       paths.desktop && paths.documents && paths.downloads && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" />
            <div className="text-sm text-green-900 dark:text-green-100">
              <p className="font-medium">All paths configured successfully</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
