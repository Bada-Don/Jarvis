import { useState, useEffect, useRef } from 'react';
import { api } from '../api';

export default function PackagingPanel({ onClose }) {
  const [buildOptions, setBuildOptions] = useState({
    output_name: 'JARVIS',
    include_console: true,
    one_file: true,
    icon: ''
  });
  
  const [buildStatus, setBuildStatus] = useState({
    is_building: false,
    progress: 0,
    current_step: '',
    logs: []
  });
  
  const [error, setError] = useState(null);
  const logsEndRef = useRef(null);
  const statusPollInterval = useRef(null);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [buildStatus.logs]);

  useEffect(() => {
    if (buildStatus.is_building) {
      statusPollInterval.current = setInterval(async () => {
        try {
          const status = await api.getBuildStatus();
          setBuildStatus(status);
          
          if (!status.is_building) {
            if (statusPollInterval.current) {
              clearInterval(statusPollInterval.current);
              statusPollInterval.current = null;
            }
          }
        } catch (err) {
          console.error('Failed to get build status:', err);
        }
      }, 1000);
    }

    return () => {
      if (statusPollInterval.current) {
        clearInterval(statusPollInterval.current);
      }
    };
  }, [buildStatus.is_building]);

  const handleStartBuild = async () => {
    setError(null);
    
    if (!buildOptions.output_name.trim()) {
      setError('Output name is required');
      return;
    }

    try {
      await api.startBuild(buildOptions);
      
      setBuildStatus({
        is_building: true,
        progress: 0,
        current_step: 'Starting build...',
        logs: []
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start build');
      console.error('Failed to start build:', err);
    }
  };

  const handleOpenBuildFolder = async () => {
    try {
      await api.openBuildFolder();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to open build folder');
      console.error('Failed to open build folder:', err);
    }
  };

  const handleBrowseIcon = async () => {
    try {
      const iconPath = await api.browseFile('Select Icon File', ['*.ico']);
      if (iconPath) {
        setBuildOptions({ ...buildOptions, icon: iconPath });
      }
    } catch (err) {
      console.error('Failed to browse for icon:', err);
    }
  };

  const getProgressColor = () => {
    if (buildStatus.success === true) return 'bg-green-600';
    if (buildStatus.success === false) return 'bg-red-600';
    return 'bg-blue-600';
  };

  const getStatusIcon = () => {
    if (buildStatus.is_building) {
      return <span className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></span>;
    }
    if (buildStatus.success === true) {
      return <span className="text-green-600 text-3xl">✓</span>;
    }
    if (buildStatus.success === false) {
      return <span className="text-red-600 text-3xl">✗</span>;
    }
    return <span className="text-gray-400 text-3xl">📦</span>;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-gray-800">Package Application</h2>
          <p className="text-gray-600 mt-1">
            Build a standalone executable for distribution
          </p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Build Options</h3>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Output Name
          </label>
          <input
            type="text"
            value={buildOptions.output_name}
            onChange={(e) => setBuildOptions({ ...buildOptions, output_name: e.target.value })}
            disabled={buildStatus.is_building}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            placeholder="JARVIS"
          />
          <p className="text-xs text-gray-500 mt-1">
            Name for the output executable (without .exe extension)
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="include_console"
            checked={buildOptions.include_console}
            onChange={(e) => setBuildOptions({ ...buildOptions, include_console: e.target.checked })}
            disabled={buildStatus.is_building}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:cursor-not-allowed"
          />
          <label htmlFor="include_console" className="text-sm font-medium text-gray-700">
            Include Console Window
          </label>
        </div>
        <p className="text-xs text-gray-500 ml-7">
          Show a console window for debugging output
        </p>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="one_file"
            checked={buildOptions.one_file}
            onChange={(e) => setBuildOptions({ ...buildOptions, one_file: e.target.checked })}
            disabled={buildStatus.is_building}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 disabled:cursor-not-allowed"
          />
          <label htmlFor="one_file" className="text-sm font-medium text-gray-700">
            Single File Executable
          </label>
        </div>
        <p className="text-xs text-gray-500 ml-7">
          Bundle everything into a single .exe file (recommended)
        </p>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Icon File (Optional)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={buildOptions.icon}
              onChange={(e) => setBuildOptions({ ...buildOptions, icon: e.target.value })}
              disabled={buildStatus.is_building}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              placeholder="Path to .ico file"
            />
            <button
              onClick={handleBrowseIcon}
              disabled={buildStatus.is_building}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
            >
              Browse
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Custom icon for the executable (.ico format)
          </p>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          <div className="flex items-start gap-2">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-semibold">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex items-center gap-4">
        <button
          onClick={handleStartBuild}
          disabled={buildStatus.is_building}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
        >
          {buildStatus.is_building ? 'Building...' : '🚀 Start Build'}
        </button>

        {buildStatus.output_path && (
          <button
            onClick={handleOpenBuildFolder}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            📁 Open Build Folder
          </button>
        )}
      </div>

      {(buildStatus.is_building || buildStatus.success !== undefined) && (
        <div className="bg-white border border-gray-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center gap-4">
            {getStatusIcon()}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-800">
                {buildStatus.is_building ? 'Building...' : 
                 buildStatus.success ? 'Build Successful!' : 
                 'Build Failed'}
              </h3>
              <p className="text-sm text-gray-600">{buildStatus.current_step}</p>
            </div>
            <div className="text-2xl font-bold text-gray-800">
              {buildStatus.progress}%
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-300 ${getProgressColor()}`}
              style={{ width: `${buildStatus.progress}%` }}
            />
          </div>

          {buildStatus.success === true && buildStatus.output_path && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-start gap-3">
                <span className="text-2xl">🎉</span>
                <div className="flex-1">
                  <p className="font-semibold text-green-800">Build completed successfully!</p>
                  <p className="text-sm text-green-700 mt-1">
                    Executable created at:
                  </p>
                  <p className="text-sm text-green-900 font-mono bg-white px-2 py-1 rounded mt-1 break-all">
                    {buildStatus.output_path}
                  </p>
                </div>
              </div>
            </div>
          )}

          {buildStatus.success === false && buildStatus.error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-3">
                <span className="text-2xl">❌</span>
                <div className="flex-1">
                  <p className="font-semibold text-red-800">Build failed</p>
                  <p className="text-sm text-red-700 mt-1">{buildStatus.error}</p>
                </div>
              </div>
            </div>
          )}

          {buildStatus.logs.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Build Logs</h4>
              <div className="bg-gray-900 text-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto font-mono text-xs">
                {buildStatus.logs.map((log, index) => (
                  <div key={index} className="mb-1">
                    {log}
                  </div>
                ))}
                <div ref={logsEndRef} />
              </div>
            </div>
          )}
        </div>
      )}

      {!buildStatus.is_building && buildStatus.success === undefined && (
        <div className="text-center py-12 text-gray-500">
          <div className="text-6xl mb-4">📦</div>
          <p className="text-lg">Configure build options and click "Start Build"</p>
          <p className="text-sm mt-2">
            This will create a standalone executable that can be distributed to users
          </p>
        </div>
      )}
    </div>
  );
}
