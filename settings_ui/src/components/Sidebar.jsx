import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  Settings,
  Clock,
  Folder,
  Printer,
  CheckCircle,
  Bot,
  Eye,
  Package,
  Save,
  FlaskConical,
  Menu,
  X,
  ChevronLeft,
  AlertTriangle,
} from "lucide-react";
import JarvisLogo from "./JarvisLogo";
import { useTheme } from "./ThemeProvider";

const navigationItems = [
  { id: "system", label: "System Settings", icon: Settings },
  { id: "timing", label: "Timing Configuration", icon: Clock },
  { id: "paths", label: "Path Management", icon: Folder },
  { id: "flexisign", label: "FlexiSIGN Settings", icon: Printer },
  { id: "verification", label: "Verification & Retry", icon: CheckCircle },
  { id: "planner-prompts", label: "Planner Prompts", icon: Bot },
  { id: "vision-prompts", label: "Vision Prompts", icon: Eye },
  { id: "packaging", label: "Application Packaging", icon: Package },
  { id: "profiles", label: "Configuration Profiles", icon: Save },
  { id: "testing", label: "Test Configuration", icon: FlaskConical },
];

export default function Sidebar({ hasUnsavedChanges }) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const { theme } = useTheme();
  
  // Determine if we're in dark mode (for logo glow effect)
  const isDark = theme === 'dark' || (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);

  const handleNavigation = (e, path) => {
    if (hasUnsavedChanges) {
      const confirmed = window.confirm(
        "You have unsaved changes. Are you sure you want to leave this section?"
      );
      if (!confirmed) {
        e.preventDefault();
        return;
      }
    }
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-background rounded-lg shadow-m border border-border hover:shadow-l transition-shadow duration-200"
      >
        {isMobileMenuOpen ? (
          <X className="w-6 h-6 text-muted-foreground" />
        ) : (
          <Menu className="w-6 h-6 text-muted-foreground" />
        )}
      </button>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40 animate-fade-in"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
        bg-card shadow-l flex flex-col border-r border-border z-40
        fixed lg:relative inset-y-0 left-0
        transition-all duration-300 ease-in-out
        ${isCollapsed ? "w-20" : "w-64"}
        ${
          isMobileMenuOpen
            ? "translate-x-0"
            : "-translate-x-full lg:translate-x-0"
        }
      `}
      >
        {/* Header */}
        <div className="p-6 border-b border-border bg-card">
          <div className="flex items-center justify-between  ">
            <div
              className={`flex items-center transition-all duration-300 ${
                isCollapsed ? "justify-center w-full" : ""
              }`}
            >
              <JarvisLogo
                className={`transition-all duration-300 text-primary ${
                  isCollapsed ? "w-8 h-8" : "w-8 h-8 mr-3 ml-auto"
                }`}
                style={{ filter: isDark ? "drop-shadow(0 0 8px #16e2d7)" : "none" }}
              />
              <h1
                className={`text-l font-bold text-foreground whitespace-nowrap transition-all duration-300 ${
                  isCollapsed ? "hidden" : "block"
                }`}
              >
                JARVIS SETTINGS
              </h1>
            </div>

            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="hidden lg:block p-1  rounded transition-colors duration-150 ml-auto"
              title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            >
              <ChevronLeft
                className={`w-5 h-5 text-muted-foreground transition-transform duration-300 ${
                  isCollapsed ? "rotate-180" : ""
                }`}
              />
            </button>
          </div>
          {hasUnsavedChanges && !isCollapsed && (
            <div className="mt-3 flex items-center text-sm text-warning-700 bg-warning-50 px-3 py-2 rounded-lg border border-warning-200 animate-fade-in">
              <AlertTriangle className="w-4 h-4 ml-2" />
              <span className="font-medium">Unsaved changes</span>
            </div>
          )}
          {hasUnsavedChanges && isCollapsed && (
            <div
              className="mt-2 w-3 h-3 bg-warning-500 rounded-full mx-auto animate-pulse"
              title="Unsaved changes"
            />
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {navigationItems.map((item) => (
              <li key={item.id}>
                <NavLink
                  to={`/${item.id}`}
                  onClick={(e) => handleNavigation(e, item.id)}
                  className={({ isActive }) => `
                    w-full text-left px-4 py-3 rounded-lg transition-all duration-200
                    flex items-center group
                    ${isCollapsed ? "justify-center" : "space-x-3"}
                    ${
                      isActive
                        ? "bg-primary text-primary-foreground shadow-m scale-[1.02]"
                        : "text-muted-foreground hover:bg-secondary hover:text-foreground hover:shadow-s"
                    }
                  `}
                  title={isCollapsed ? item.label : undefined}
                >
                  {({ isActive }) => (
                    <>
                      <span
                        className={`transition-transform duration-200 ${
                          isActive ? "" : "group-hover:scale-110"
                        }`}
                      >
                        <item.icon className="w-5 h-5" />
                      </span>
                      {!isCollapsed && (
                        <>
                          <span className="font-medium text-sm flex-1">
                            {item.label}
                          </span>
                          {item.badge && (
                            <span className="badge-danger">{item.badge}</span>
                          )}
                          {isActive && (
                            <div className="w-1.5 h-1.5 rounded-full bg-primary-foreground animate-fade-in" />
                          )}
                        </>
                      )}
                    </>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-border bg-muted/50">
          <div
            className={`text-xs text-muted-foreground ${
              isCollapsed ? "text-center" : "text-center"
            }`}
          >
            {isCollapsed ? (
              <JarvisLogo className="w-6 h-6 mx-auto opacity-50 text-primary" />
            ) : (
              <>
                <p className="font-medium">JARVIS Settings</p>
                <p className="text-muted-foreground mt-1">Version 1.0.0</p>
              </>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
