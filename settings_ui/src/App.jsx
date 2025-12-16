import { useState, useEffect, useCallback } from 'react';
import './App.css';
import { api } from './api';
import Sidebar from './components/Sidebar';
import SystemSettingsPanel from './components/SystemSettingsPanel';
import TimingSettingsPanel from './components/TimingSettingsPanel';
import PathSettingsPanel from './components/PathSettingsPanel';
import FlexiSignSettingsPanel from './components/FlexiSignSettingsPanel';
import VerificationSettingsPanel from './components/VerificationSettingsPanel';
import PlannerPromptsPanel from './components/PlannerPromptsPanel';
import VisionPromptsPanel from './components/VisionPromptsPanel';
import ConfigurationProfilesPanel from './components/ConfigurationProfilesPanel';
import TestResultsPanel from './components/TestResultsPanel';
import PackagingPanel from './components/PackagingPanel';
import ToastContainer, { useToast } from './components/ToastContainer';

function App() {
  const [currentSection, setCurrentSection] = useState('system');
  const [settings, setSettings] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { toasts, removeToast, showSuccess, showError } = useToast();

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load settings');
      console.error('Failed to load settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSectionChange = useCallback((section) => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        'You have unsaved changes. Are you sure you want to leave this section?'
      );
      if (!confirmed) {
        return;
      }
      setHasUnsavedChanges(false);
    }
    setCurrentSection(section);
  }, [hasUnsavedChanges]);

  const handleSave = async () => {
    if (!settings) return;
    
    setIsLoading(true);
    setError(null);
    try {
      await api.saveSettings(settings);
      setHasUnsavedChanges(false);
      showSuccess('Settings saved successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save settings';
      setError(errorMessage);
      showError(errorMessage);
      console.error('Failed to save settings:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (section, key, value) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      [section]: {
        ...settings[section],
        [key]: value,
      },
    });
    setHasUnsavedChanges(true);
  };

  const handlePromptChange = (category, key, value) => {
    if (!settings) return;
    
    setSettings({
      ...settings,
      prompts: {
        ...settings.prompts,
        [category]: {
          ...settings.prompts[category],
          [key]: value,
        },
      },
    });
    setHasUnsavedChanges(true);
  };

  const handleReset = async (section, key) => {
    if (!settings) return;
    
    // Show confirmation dialog
    const confirmed = window.confirm(
      `Are you sure you want to reset "${key}" to its default value? This action cannot be undone.`
    );
    
    if (!confirmed) {
      return;
    }
    
    try {
      // Call API to get default value
      const result = await api.resetSetting(key);
      
      if (result && result.value !== undefined) {
        // Update the setting with the default value
        if (section === 'prompts') {
          // Handle prompts specially - key format is "planner.PROMPT_NAME" or "vision.PROMPT_NAME"
          const [category, promptKey] = key.split('.');
          if (category && promptKey) {
            setSettings({
              ...settings,
              prompts: {
                ...settings.prompts,
                [category]: {
                  ...settings.prompts[category],
                  [promptKey]: result.value,
                },
              },
            });
          }
        } else {
          // Handle regular settings
          setSettings({
            ...settings,
            [section]: {
              ...settings[section],
              [key]: result.value,
            },
          });
        }
        
        setHasUnsavedChanges(true);
        showSuccess(`Reset "${key}" to default value`);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to reset setting';
      setError(errorMessage);
      showError(errorMessage);
      console.error('Failed to reset setting:', err);
    }
  };

  const renderPanel = () => {
    if (!settings) return null;

    const panelClass = "animate-fade-in";

    switch (currentSection) {
      case 'system':
        return (
          <div className={panelClass}>
            <SystemSettingsPanel
              settings={settings.system}
              onChange={(key, value) => handleSettingChange('system', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('system', key)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'timing':
        return (
          <div className={panelClass}>
            <TimingSettingsPanel
              settings={settings.timing}
              onChange={(key, value) => handleSettingChange('timing', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('timing', key)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'paths':
        return (
          <div className={panelClass}>
            <PathSettingsPanel
              settings={settings.paths}
              onChange={(key, value) => handleSettingChange('paths', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('paths', key)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'flexisign':
        return (
          <div className={panelClass}>
            <FlexiSignSettingsPanel
              settings={settings.flexisign}
              onChange={(key, value) => handleSettingChange('flexisign', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('flexisign', key)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'verification':
        return (
          <div className={panelClass}>
            <VerificationSettingsPanel
              settings={settings.verification}
              onChange={(key, value) => handleSettingChange('verification', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('verification', key)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'planner-prompts':
        return (
          <div className={panelClass}>
            <PlannerPromptsPanel
              prompts={settings.prompts.planner}
              onChange={(key, value) => handlePromptChange('planner', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('prompts', `planner.${key}`)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'vision-prompts':
        return (
          <div className={panelClass}>
            <VisionPromptsPanel
              prompts={settings.prompts.vision}
              onChange={(key, value) => handlePromptChange('vision', key, value)}
              onSave={handleSave}
              onReset={(key) => handleReset('prompts', `vision.${key}`)}
              searchQuery={searchQuery}
            />
          </div>
        );
      
      case 'profiles':
        return (
          <div className={panelClass}>
            <ConfigurationProfilesPanel
              onImportComplete={loadSettings}
            />
          </div>
        );
      
      case 'testing':
        return (
          <div className={panelClass}>
            <TestResultsPanel />
          </div>
        );
      
      case 'packaging':
        return (
          <div className={panelClass}>
            <PackagingPanel />
          </div>
        );
      
      default:
        return (
          <div className={`${panelClass} text-secondary-600`}>
            <p>Section: {currentSection}</p>
            <p className="text-sm mt-2">This section is not yet implemented.</p>
          </div>
        );
    }
  };

  // Warn before closing window with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  if (isLoading && !settings) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-secondary-50 to-primary-50">
        <div className="text-center animate-fade-in">
          <div className="spinner h-16 w-16 mx-auto mb-6"></div>
          <p className="text-secondary-700 text-lg font-medium">Loading settings...</p>
          <p className="text-secondary-500 text-sm mt-2">Please wait while we fetch your configuration</p>
        </div>
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-secondary-50 to-danger-50">
        <div className="text-center max-w-md animate-fade-in">
          <div className="bg-danger-100 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
            <svg className="w-12 h-12 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-secondary-900 mb-3">Error Loading Settings</h2>
          <p className="text-secondary-600 mb-6 leading-relaxed">{error}</p>
          <button
            onClick={loadSettings}
            className="btn-primary"
          >
            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      
      <div className="flex h-screen bg-gradient-to-br from-secondary-50 to-primary-50">
        <Sidebar
          currentSection={currentSection}
          onSectionChange={handleSectionChange}
          hasUnsavedChanges={hasUnsavedChanges}
        />
        
        <main className="flex-1 overflow-auto lg:ml-0">
        <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 pt-16 lg:pt-6">
          {/* Search Header */}
          <div className="card p-3 sm:p-4 mb-4 sm:mb-6 animate-slide-up">
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search settings..."
                className="input-field pl-10 pr-10 text-sm sm:text-base"
              />
              <svg
                className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-secondary-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-secondary-400 hover:text-secondary-600 transition-colors duration-150"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              )}
            </div>
            {searchQuery && (
              <div className="mt-3 flex items-center text-sm text-secondary-600 bg-primary-50 px-3 py-2 rounded-lg animate-fade-in">
                <svg className="w-4 h-4 mr-2 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                </svg>
                <span>Searching for: <span className="font-semibold text-primary-700">{searchQuery}</span></span>
              </div>
            )}
          </div>

          <div key={currentSection} className="card p-4 sm:p-6 mb-4 sm:mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            {error && (
              <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-danger-50 border border-danger-300 text-danger-800 rounded-lg flex items-start animate-fade-in">
                <svg className="w-5 h-5 mr-2 sm:mr-3 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div className="text-sm sm:text-base">
                  <p className="font-medium">Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              </div>
            )}

            {renderPanel()}
          </div>
        </div>
      </main>
    </div>
    </>
  );
}

export default App;
