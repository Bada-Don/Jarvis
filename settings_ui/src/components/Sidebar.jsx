import { useState } from 'react';

const navigationItems = [
  { id: 'system', label: 'System Settings', icon: '⚙️' },
  { id: 'timing', label: 'Timing Configuration', icon: '⏱️' },
  { id: 'paths', label: 'Path Management', icon: '📁' },
  { id: 'flexisign', label: 'FlexiSIGN Settings', icon: '🖨️' },
  { id: 'verification', label: 'Verification & Retry', icon: '✓' },
  { id: 'planner-prompts', label: 'Planner Prompts', icon: '🤖' },
  { id: 'vision-prompts', label: 'Vision Prompts', icon: '👁️' },
  { id: 'packaging', label: 'Application Packaging', icon: '📦' },
  { id: 'profiles', label: 'Configuration Profiles', icon: '💾' },
  { id: 'testing', label: 'Test Configuration', icon: '🧪' },
];

export default function Sidebar({ currentSection, onSectionChange, hasUnsavedChanges }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleSectionChange = (section) => {
    onSectionChange(section);
    setIsMobileMenuOpen(false); // Close mobile menu after selection
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-medium border border-secondary-200"
      >
        <svg className="w-6 h-6 text-secondary-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {isMobileMenuOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40 animate-fade-in"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        bg-white shadow-strong flex flex-col border-r border-secondary-200 z-40
        fixed lg:relative inset-y-0 left-0
        transition-all duration-300 ease-in-out
        ${isCollapsed ? 'w-20' : 'w-64'}
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        {/* Header */}
        <div className="p-6 border-b border-secondary-200 bg-gradient-to-br from-primary-50 to-white">
          <div className="flex items-center justify-between">
            <h1 className={`text-2xl font-bold text-secondary-900 mb-1 transition-all duration-300 ${
              isCollapsed ? 'hidden' : 'block'
            }`}>
              JARVIS Settings
            </h1>
            {isCollapsed && (
              <div className="text-base font-bold text-primary-600 mx-auto">⚙️</div>
            )}
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="hidden lg:block p-1 hover:bg-secondary-100 rounded transition-colors duration-150"
              title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              <svg className={`w-5 h-5 text-secondary-600 transition-transform duration-300 ${
                isCollapsed ? 'rotate-180' : ''
              }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          </div>
          {hasUnsavedChanges && !isCollapsed && (
            <div className="mt-3 flex items-center text-sm text-warning-700 bg-warning-50 px-3 py-2 rounded-lg border border-warning-200 animate-fade-in">
              <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Unsaved changes</span>
            </div>
          )}
          {hasUnsavedChanges && isCollapsed && (
            <div className="mt-2 w-3 h-3 bg-warning-500 rounded-full mx-auto animate-pulse" title="Unsaved changes" />
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {navigationItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => handleSectionChange(item.id)}
                  className={`
                    w-full text-left px-4 py-3 rounded-lg transition-all duration-200
                    flex items-center group
                    ${isCollapsed ? 'justify-center' : 'space-x-3'}
                    ${
                      currentSection === item.id
                        ? 'bg-primary-600 text-white shadow-medium scale-[1.02]'
                        : 'text-secondary-700 hover:bg-secondary-100 hover:text-secondary-900 hover:shadow-soft'
                    }
                  `}
                  title={isCollapsed ? item.label : undefined}
                >
                  <span className={`text-sm transition-transform duration-200 ${
                    currentSection === item.id ? '' : 'group-hover:scale-110'
                  }`}>
                    {item.icon}
                  </span>
                  {!isCollapsed && (
                    <>
                      <span className="font-medium text-sm flex-1">{item.label}</span>
                      {item.badge && (
                        <span className="badge-danger">
                          {item.badge}
                        </span>
                      )}
                      {currentSection === item.id && (
                        <svg className="w-4 h-4 animate-fade-in" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      )}
                    </>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-secondary-200 bg-secondary-50">
          <div className={`text-xs text-secondary-500 ${isCollapsed ? 'text-center' : 'text-center'}`}>
            {isCollapsed ? (
              <p className="font-bold text-lg">J</p>
            ) : (
              <>
                <p className="font-medium">JARVIS Settings</p>
                <p className="text-secondary-400 mt-1">Version 1.0.0</p>
              </>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
