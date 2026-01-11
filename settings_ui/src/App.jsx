import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AlertTriangle, RefreshCw, Search, X, Info } from 'lucide-react';
import './App.css';
import { api } from './api';
import Loader from './components/Loader';
import Sidebar from './components/SideBar';
import SystemSettingsPanel from './components/SystemSettingsPanel';
import TimingSettingsPanel from './components/TimingSettingsPanel';
import PathSettingsPanel from './components/PathSettingsPanel';
import FlexiSignSettingsPanel from './components/FlexiSignSettingsPanel';
import LLMSettingsPanel from './components/LLMSettingsPanel';
import VerificationSettingsPanel from './components/VerificationSettingsPanel';
import PlannerPromptsPanel from './components/PlannerPromptsPanel';
import VisionPromptsPanel from './components/VisionPromptsPanel';
import ConfigurationProfilesPanel from './components/ConfigurationProfilesPanel';
import TestResultsPanel from './components/TestResultsPanel';
import PackagingPanel from './components/PackagingPanel';
import ToastContainer, { useToast } from './components/ToastContainer';
import { ThemeProvider } from './components/ThemeProvider';
import { ThemeToggle } from './components/ThemeToggle';

// Dashboard Components
import DashboardLayout from './components/dashboard/DashboardLayout';
import LeftPanel from './components/dashboard/LeftPanel';
import ChatPanel from './components/dashboard/ChatPanel';
import VoiceOrb from './components/dashboard/VoiceOrb';
import SettingsOverlay from './components/dashboard/SettingsOverlay';

function AppContent() {
  const [settings, setSettings] = useState(null);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const { toasts, removeToast, showSuccess, showError } = useToast();
  const location = useLocation();
  const navigate = useNavigate();

  // Load settings on mount
  useEffect(() => {
    loadSettings();
  }, []);

  // Sync route with settings overlay
  useEffect(() => {
    if (location.pathname !== '/' && location.pathname !== '/dashboard') {
      setIsSettingsOpen(true);
    }
  }, [location]);

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

    const confirmed = window.confirm(
      `Are you sure you want to reset "${key}" to its default value? This action cannot be undone.`
    );

    if (!confirmed) return;

    try {
      const result = await api.resetSetting(key);

      if (result && result.value !== undefined) {
        if (section === 'prompts') {
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

  const handleCloseSettings = () => {
    setIsSettingsOpen(false);
    navigate('/');
  };

  if (isLoading && !settings) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <Loader variant="jarvis" size="xl" text="Loading settings..." fullScreen={false} />
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center max-w-md animate-fade-in">
          <div className="bg-destructive/20 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
            <AlertTriangle className="w-12 h-12 text-destructive" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-3">Error Loading Settings</h2>
          <p className="text-muted-foreground mb-6 leading-relaxed">{error}</p>
          <button
            onClick={loadSettings}
            className="btn-primary flex items-center justify-center mx-auto"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  const panelClass = "animate-fade-in";

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />

      <DashboardLayout
        leftPanel={
          <LeftPanel
            onOpenSettings={() => {
              setIsSettingsOpen(true);
              navigate('/system');
            }}
            isListening={isListening}
            toggleListening={() => setIsListening(!isListening)}
          />
        }
        centerPanel={
          <VoiceOrb
            isListening={isListening}
            chromaRGBr={isListening ? 9.0 : 7.5}
            cameraZoom={isListening ? 180 : 150}
          />
        }
        rightPanel={<ChatPanel />}
        overlay={
          <SettingsOverlay isOpen={isSettingsOpen} onClose={handleCloseSettings}>
            <div className="flex h-full bg-background">
              <Sidebar hasUnsavedChanges={hasUnsavedChanges} />

              <main className="flex-1 overflow-auto lg:ml-0">
                <div className="max-w-5xl mx-auto p-4 sm:p-6 lg:p-8 pt-16 lg:pt-6">
                  {/* Search Header */}
                  <div className="card p-3 sm:p-4 mb-4 sm:mb-6 animate-slide-up">
                    <div className="flex items-center">
                      <div className="relative flex-1">
                        <input
                          type="text"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          placeholder="Search settings..."
                          className="input-field pl-10 pr-10 text-sm sm:text-base"
                        />
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                        {searchQuery && (
                          <button
                            onClick={() => setSearchQuery('')}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors duration-150"
                          >
                            <X className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                      <div className="ml-4">
                        <ThemeToggle />
                      </div>
                    </div>
                    {searchQuery && (
                      <div className="mt-3 flex items-center text-sm text-muted-foreground bg-accent px-3 py-2 rounded-lg animate-fade-in">
                        <Info className="w-4 h-4 mr-2 text-primary" />
                        <span>Searching for: <span className="font-semibold text-primary">{searchQuery}</span></span>
                      </div>
                    )}
                  </div>

                  <div key={location.pathname} className="card p-4 sm:p-6 mb-4 sm:mb-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                    <Routes>
                      <Route path="/" element={<Navigate to="/system" replace />} />
                      <Route path="/dashboard" element={<Navigate to="/" replace />} />
                      <Route path="/system" element={
                        <div className={panelClass}>
                          <SystemSettingsPanel
                            settings={settings.system}
                            onChange={(key, value) => handleSettingChange('system', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('system', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/llm" element={
                        <div className={panelClass}>
                          <LLMSettingsPanel
                            settings={settings.llm}
                            onChange={(key, value) => handleSettingChange('llm', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('llm', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/timing" element={
                        <div className={panelClass}>
                          <TimingSettingsPanel
                            settings={settings.timing}
                            onChange={(key, value) => handleSettingChange('timing', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('timing', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/paths" element={
                        <div className={panelClass}>
                          <PathSettingsPanel
                            settings={settings.paths}
                            onChange={(key, value) => handleSettingChange('paths', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('paths', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/flexisign" element={
                        <div className={panelClass}>
                          <FlexiSignSettingsPanel
                            settings={settings.flexisign}
                            onChange={(key, value) => handleSettingChange('flexisign', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('flexisign', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/verification" element={
                        <div className={panelClass}>
                          <VerificationSettingsPanel
                            settings={settings.verification}
                            onChange={(key, value) => handleSettingChange('verification', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('verification', key)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/planner-prompts" element={
                        <div className={panelClass}>
                          <PlannerPromptsPanel
                            prompts={settings.prompts.planner}
                            onChange={(key, value) => handlePromptChange('planner', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('prompts', `planner.${key}`)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/vision-prompts" element={
                        <div className={panelClass}>
                          <VisionPromptsPanel
                            prompts={settings.prompts.vision}
                            onChange={(key, value) => handlePromptChange('vision', key, value)}
                            onSave={handleSave}
                            onReset={(key) => handleReset('prompts', `vision.${key}`)}
                            searchQuery={searchQuery}
                          />
                        </div>
                      } />
                      <Route path="/profiles" element={
                        <div className={panelClass}>
                          <ConfigurationProfilesPanel
                            onImportComplete={loadSettings}
                          />
                        </div>
                      } />
                      <Route path="/testing" element={
                        <div className={panelClass}>
                          <TestResultsPanel />
                        </div>
                      } />
                      <Route path="/packaging" element={
                        <div className={panelClass}>
                          <PackagingPanel />
                        </div>
                      } />
                      <Route path="*" element={
                        <div className={`${panelClass} text-muted-foreground`}>
                          <p>Page not found</p>
                        </div>
                      } />
                    </Routes>
                  </div>
                </div>
              </main>
            </div>
          </SettingsOverlay>
        }
      />
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
        <AppContent />
      </ThemeProvider>
    </BrowserRouter>
  );
}

export default App;
