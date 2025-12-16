# Design Document

## Overview

The JARVIS Settings Interface is a desktop application that provides a graphical user interface for configuring the JARVIS automation system. The application uses a React frontend hosted within a PyWebView window, creating a native desktop experience while leveraging modern web technologies for the UI. The architecture follows a clear separation between the presentation layer (React), the bridge layer (PyWebView API), and the business logic layer (Python backend).

The interface will be organized into logical sections covering system settings, timing configuration, path management, AI prompt editing, and application packaging. Users will interact with familiar form controls, and changes will be validated before being persisted to the appropriate configuration files.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PyWebView Window                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │           React Settings Interface                │  │
│  │  ┌─────────────┐  ┌──────────────────────────┐  │  │
│  │  │  Sidebar    │  │   Settings Panels        │  │  │
│  │  │  Navigation │  │   - System Settings      │  │  │
│  │  │             │  │   - Timing Config        │  │  │
│  │  │             │  │   - Path Management      │  │  │
│  │  │             │  │   - Planner Prompts      │  │  │
│  │  │             │  │   - Vision Prompts       │  │  │
│  │  │             │  │   - Packaging            │  │  │
│  │  └─────────────┘  └──────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↕                               │
│                   PyWebView API Bridge                   │
│                          ↕                               │
│  ┌───────────────────────────────────────────────────┐  │
│  │         Python Backend (settings_app.py)          │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  ConfigManager                              │ │  │
│  │  │  - Read/Write config.py                     │ │  │
│  │  │  - Read/Write gemini_service.py             │ │  │
│  │  │  - Read/Write vision_service.py             │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  ValidationService                          │ │  │
│  │  │  - Path validation                          │ │  │
│  │  │  - Type validation                          │ │  │
│  │  │  - Constraint validation                    │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────┐ │  │
│  │  │  PackagingService                           │ │  │
│  │  │  - PyInstaller integration                  │ │  │
│  │  │  - Build process management                 │ │  │
│  │  └─────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18.x for UI components
- TypeScript for type safety
- Tailwind CSS for styling
- React Hook Form for form management
- Monaco Editor for prompt editing with syntax highlighting

**Backend:**
- Python 3.8+
- PyWebView for native window hosting
- AST (Abstract Syntax Tree) module for safe Python file manipulation

**Build & Packaging:**
- Vite for React build process
- PyInstaller for creating standalone executables

## Components and Interfaces

### Frontend Components

#### 1. App Component
Root component that manages routing and global state.

```typescript
interface AppState {
  currentSection: string;
  settings: SettingsData;
  hasUnsavedChanges: boolean;
  isLoading: boolean;
}

interface SettingsData {
  system: SystemSettings;
  timing: TimingSettings;
  paths: PathSettings;
  flexisign: FlexiSignSettings;
  verification: VerificationSettings;
  prompts: PromptSettings;
}
```

#### 2. Sidebar Component
Navigation sidebar for switching between settings sections.

```typescript
interface SidebarProps {
  currentSection: string;
  onSectionChange: (section: string) => void;
  hasUnsavedChanges: boolean;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  badge?: string;
}
```

#### 3. SettingsPanel Components
Individual panels for each settings category.

```typescript
interface SettingsPanelProps {
  settings: any;
  onChange: (key: string, value: any) => void;
  onSave: () => Promise<void>;
  onReset: (key: string) => void;
}
```

#### 4. FormField Component
Reusable form field with validation and help text.

```typescript
interface FormFieldProps {
  label: string;
  value: any;
  type: 'text' | 'number' | 'boolean' | 'path' | 'select';
  onChange: (value: any) => void;
  validation?: ValidationRule[];
  helpText?: string;
  placeholder?: string;
  disabled?: boolean;
}
```

#### 5. PromptEditor Component
Monaco-based editor for AI prompts with syntax highlighting.

```typescript
interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: 'markdown' | 'json';
  height: string;
  readOnly?: boolean;
}
```

#### 6. PackagingPanel Component
Interface for building standalone executables.

```typescript
interface PackagingPanelProps {
  onStartBuild: (options: BuildOptions) => void;
  buildStatus: BuildStatus;
  buildLogs: string[];
}

interface BuildOptions {
  outputName: string;
  includeConsole: boolean;
  oneFile: boolean;
  icon?: string;
}

interface BuildStatus {
  isBuilding: boolean;
  progress: number;
  currentStep: string;
  success?: boolean;
  outputPath?: string;
}
```

### Backend Services

#### 1. ConfigManager
Handles reading and writing configuration files.

```python
class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.backup_path = config_path + '.backup'
    
    def read_config(self) -> dict:
        """Read current configuration from config.py"""
        pass
    
    def write_config(self, settings: dict) -> bool:
        """Write settings back to config.py, preserving structure"""
        pass
    
    def create_backup(self) -> None:
        """Create backup of current config before modifications"""
        pass
    
    def restore_backup(self) -> bool:
        """Restore config from backup"""
        pass
    
    def get_default_value(self, key: str) -> any:
        """Get default value for a setting"""
        pass
```

#### 2. PromptManager
Manages AI model prompts in Python source files.

```python
class PromptManager:
    def __init__(self, service_path: str):
        self.service_path = service_path
    
    def read_prompts(self) -> dict:
        """Extract prompt constants from Python file"""
        pass
    
    def write_prompts(self, prompts: dict) -> bool:
        """Update prompt constants in Python file"""
        pass
    
    def validate_prompt(self, prompt: str, required_placeholders: list) -> bool:
        """Validate prompt contains required placeholders"""
        pass
```

#### 3. ValidationService
Validates user input and settings.

```python
class ValidationService:
    @staticmethod
    def validate_path(path: str, must_exist: bool = True, 
                     is_directory: bool = False) -> tuple[bool, str]:
        """Validate file/directory path"""
        pass
    
    @staticmethod
    def validate_number(value: any, min_val: float = None, 
                       max_val: float = None) -> tuple[bool, str]:
        """Validate numeric value"""
        pass
    
    @staticmethod
    def validate_string(value: str, pattern: str = None, 
                       min_length: int = 0) -> tuple[bool, str]:
        """Validate string value"""
        pass
    
    @staticmethod
    def validate_settings_dict(settings: dict, schema: dict) -> dict:
        """Validate entire settings dictionary against schema"""
        pass
```

#### 4. PackagingService
Handles application packaging with PyInstaller.

```python
class PackagingService:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.build_dir = os.path.join(project_root, 'dist')
    
    def build_executable(self, options: dict, 
                        progress_callback: callable) -> bool:
        """Build standalone executable using PyInstaller"""
        pass
    
    def get_build_spec(self, options: dict) -> str:
        """Generate PyInstaller spec file content"""
        pass
    
    def clean_build_artifacts(self) -> None:
        """Remove temporary build files"""
        pass
```

### PyWebView API Bridge

The bridge exposes Python functions to JavaScript:

```python
class SettingsAPI:
    def __init__(self):
        self.config_manager = ConfigManager('local_client/config.py')
        self.gemini_prompt_manager = PromptManager('backend/gemini_service.py')
        self.vision_prompt_manager = PromptManager('local_client/vision_service.py')
        self.validation_service = ValidationService()
        self.packaging_service = PackagingService('.')
    
    # Configuration Methods
    def get_settings(self) -> dict:
        """Get all current settings"""
        pass
    
    def save_settings(self, settings: dict) -> dict:
        """Save settings to config files"""
        pass
    
    def reset_setting(self, key: str) -> dict:
        """Reset a setting to default value"""
        pass
    
    def validate_setting(self, key: str, value: any) -> dict:
        """Validate a single setting"""
        pass
    
    # Prompt Methods
    def get_prompts(self) -> dict:
        """Get all AI prompts"""
        pass
    
    def save_prompts(self, prompts: dict) -> dict:
        """Save AI prompts to source files"""
        pass
    
    def reset_prompt(self, prompt_name: str) -> dict:
        """Reset prompt to default"""
        pass
    
    # Path Methods
    def browse_file(self, title: str, file_types: list) -> str:
        """Open native file browser"""
        pass
    
    def browse_folder(self, title: str) -> str:
        """Open native folder browser"""
        pass
    
    def validate_path(self, path: str, is_directory: bool) -> dict:
        """Validate a file/folder path"""
        pass
    
    # Configuration Profile Methods
    def export_config(self, file_path: str) -> dict:
        """Export configuration to JSON file"""
        pass
    
    def import_config(self, file_path: str) -> dict:
        """Import configuration from JSON file"""
        pass
    
    # Testing Methods
    def test_configuration(self) -> dict:
        """Run validation tests on current configuration"""
        pass
    
    # Packaging Methods
    def start_build(self, options: dict) -> dict:
        """Start building executable"""
        pass
    
    def get_build_status(self) -> dict:
        """Get current build status"""
        pass
    
    def open_build_folder(self) -> None:
        """Open folder containing built executable"""
        pass
```

## Data Models

### Settings Schema

```python
SETTINGS_SCHEMA = {
    "system": {
        "SERVER_URL": {
            "type": "string",
            "default": "http://localhost:5000",
            "validation": "url",
            "description": "Backend server URL"
        },
        "WINDOWS_USERNAME": {
            "type": "string",
            "default": "",
            "required": True,
            "description": "Windows username for path generation"
        }
    },
    "timing": {
        "ACTION_DELAY": {
            "type": "float",
            "default": 0.3,
            "min": 0.0,
            "max": 10.0,
            "unit": "seconds",
            "description": "Default delay after each step"
        },
        "APP_LAUNCH_WAIT": {
            "type": "float",
            "default": 3.0,
            "min": 0.5,
            "max": 30.0,
            "unit": "seconds",
            "description": "Extended delay after launching an application"
        },
        "HOTKEY_DELAY": {
            "type": "float",
            "default": 0.5,
            "min": 0.0,
            "max": 5.0,
            "unit": "seconds",
            "description": "Delay after hotkey combinations"
        },
        "PRE_TYPE_DELAY": {
            "type": "float",
            "default": 0.2,
            "min": 0.0,
            "max": 2.0,
            "unit": "seconds",
            "description": "Small delay before typing text"
        },
        "SCREENSHOT_DELAY": {
            "type": "float",
            "default": 0.5,
            "min": 0.0,
            "max": 5.0,
            "unit": "seconds",
            "description": "Screenshot delay before vision analysis"
        },
        "WINDOW_ACTIVATION_TIMEOUT": {
            "type": "float",
            "default": 10.0,
            "min": 1.0,
            "max": 60.0,
            "unit": "seconds",
            "description": "Maximum time to wait for window appearance"
        },
        "WINDOW_POLL_INTERVAL": {
            "type": "float",
            "default": 0.5,
            "min": 0.1,
            "max": 5.0,
            "unit": "seconds",
            "description": "How often to poll for window appearance"
        }
    },
    "window_manager": {
        "WINDOW_ACTIVATION_ATTEMPTS": {
            "type": "int",
            "default": 3,
            "min": 1,
            "max": 10,
            "description": "Maximum attempts to activate a window"
        },
        "WINDOW_MANAGER_VERBOSE": {
            "type": "bool",
            "default": True,
            "description": "Verbose logging for window operations"
        }
    },
    "flexisign": {
        "FLEXISIGN_PROCESS_NAME": {
            "type": "string",
            "default": "Production Suite Scanner 10.5.1 Build 1806 Protected",
            "description": "FlexiSIGN process name"
        },
        "FLEXISIGN_EXE_PATH": {
            "type": "path",
            "default": "",
            "file_type": "executable",
            "description": "Path to FlexiSIGN executable"
        },
        "FLEXISIGN_WINDOW_TITLE": {
            "type": "string",
            "default": "FlexiSIGN-PRO",
            "description": "FlexiSIGN window title"
        },
        "STARTUP_MODAL_ENABLED": {
            "type": "bool",
            "default": True,
            "description": "Enable startup modal handling"
        },
        "STARTUP_MODAL_TITLE": {
            "type": "string",
            "default": "FlexiSIGN",
            "description": "Startup modal window title"
        },
        "STARTUP_MODAL_BUTTON": {
            "type": "string",
            "default": "OK",
            "description": "Startup modal button text"
        },
        "STARTUP_MODAL_TIMEOUT": {
            "type": "int",
            "default": 30,
            "min": 5,
            "max": 120,
            "unit": "seconds",
            "description": "Startup modal timeout"
        }
    },
    "verification": {
        "VERIFICATION_ENABLED": {
            "type": "bool",
            "default": False,
            "description": "Enable task verification after execution"
        },
        "MAX_RETRIES": {
            "type": "int",
            "default": 0,
            "min": 0,
            "max": 10,
            "description": "Maximum retry attempts if verification fails"
        },
        "RETRY_DELAY": {
            "type": "float",
            "default": 2.0,
            "min": 0.5,
            "max": 30.0,
            "unit": "seconds",
            "description": "Delay before retrying after verification failure"
        },
        "VERIFICATION_DELAY": {
            "type": "float",
            "default": 1.0,
            "min": 0.0,
            "max": 10.0,
            "unit": "seconds",
            "description": "Delay before starting verification"
        },
        "CONFIDENCE_THRESHOLD": {
            "type": "float",
            "default": 0.7,
            "min": 0.0,
            "max": 1.0,
            "description": "Minimum confidence score for successful verification"
        }
    }
}

PROMPT_SCHEMA = {
    "planner": {
        "GENERAL_SYSTEM_PROMPT": {
            "file": "backend/gemini_service.py",
            "variable": "GENERAL_SYSTEM_PROMPT",
            "language": "markdown",
            "description": "System prompt for general computer automation"
        },
        "FLEXISIGN_SYSTEM_PROMPT": {
            "file": "backend/gemini_service.py",
            "variable": "FLEXISIGN_SYSTEM_PROMPT",
            "language": "markdown",
            "description": "System prompt for FlexiSIGN automation"
        }
    },
    "vision": {
        "GENERAL_VISION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "GENERAL_VISION_PROMPT",
            "language": "markdown",
            "description": "Vision prompt for general UI element identification"
        },
        "VERIFICATION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "VERIFICATION_PROMPT",
            "language": "markdown",
            "description": "Prompt for task verification"
        },
        "FLEXISIGN_VISION_PROMPT": {
            "file": "local_client/vision_service.py",
            "variable": "FLEXISIGN_VISION_PROMPT",
            "language": "markdown",
            "description": "Vision prompt for FlexiSIGN UI elements"
        }
    }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration persistence (Round-trip)
*For any* valid settings dictionary, saving the settings and then reading them back should produce an equivalent settings dictionary with all values preserved.
**Validates: Requirements 2.3**

### Property 2: API bridge bidirectional communication
*For any* valid API call from the frontend, the backend should respond with a properly formatted response, and for any backend event, the frontend should receive it correctly.
**Validates: Requirements 1.3**

### Property 3: Settings validation completeness
*For any* settings dictionary, if validation passes, then all individual setting values must pass their respective validation rules.
**Validates: Requirements 2.2**

### Property 4: Invalid input rejection
*For any* setting with validation rules, providing an invalid value should prevent saving and display an error message.
**Validates: Requirements 2.5**

### Property 5: Default value restoration
*For any* setting that has been modified, resetting it should restore the exact default value defined in the schema.
**Validates: Requirements 2.4**

### Property 6: Path validation consistency
*For any* path string, validating it multiple times should always produce the same validation result.
**Validates: Requirements 3.3**

### Property 7: Directory vs file validation
*For any* path that points to a directory, validating it as a directory should pass, and validating it as a file should fail, and vice versa.
**Validates: Requirements 3.4**

### Property 8: Executable validation
*For any* file path, if it has an executable extension (.exe, .bat, .cmd) and exists, it should pass executable validation, otherwise it should fail.
**Validates: Requirements 3.5**

### Property 9: Numeric validation bounds
*For any* numeric setting with min/max constraints, values within the range should pass validation, and values outside should fail.
**Validates: Requirements 4.2, 7.3**

### Property 10: Prompt round-trip preservation
*For any* valid prompt string, saving it to the source file and then reading it back should produce the identical prompt string.
**Validates: Requirements 5.4, 6.3**

### Property 11: Prompt placeholder validation
*For any* prompt that requires specific placeholders, removing any required placeholder should cause validation to fail.
**Validates: Requirements 6.2**

### Property 12: Export-import configuration equivalence (Round-trip)
*For any* valid configuration, exporting it to a file and then importing that file should produce an equivalent configuration with all settings preserved.
**Validates: Requirements 10.3**

### Property 13: Partial import with invalid values
*For any* configuration file containing both valid and invalid settings, importing should apply all valid settings and skip invalid ones while reporting warnings.
**Validates: Requirements 10.4**

### Property 14: Path existence validation in tests
*For any* configured path setting, the test configuration function should verify the path exists and is accessible.
**Validates: Requirements 11.2**

### Property 15: Search filtering correctness
*For any* search query, all displayed settings should match the query, and all settings matching the query should be displayed.
**Validates: Requirements 12.4**

## Error Handling

### Frontend Error Handling

1. **Network Errors**: When PyWebView API calls fail, display user-friendly error messages and provide retry options.

2. **Validation Errors**: Display inline validation errors next to form fields with clear guidance on how to fix them.

3. **Unsaved Changes**: Prompt user before navigating away from a section with unsaved changes.

4. **File Browser Errors**: Handle cases where native file dialogs fail or are cancelled by the user.

### Backend Error Handling

1. **File I/O Errors**: Catch and report errors when reading/writing configuration files, with automatic backup restoration on failure.

2. **Parse Errors**: Handle syntax errors when parsing Python source files, preventing corruption of config files.

3. **Validation Errors**: Return structured error responses with field-specific error messages.

4. **Build Errors**: Capture and display PyInstaller errors with actionable suggestions for resolution.

### Error Response Format

```python
{
    "success": bool,
    "data": any,  # Present on success
    "error": {    # Present on failure
        "code": str,
        "message": str,
        "details": dict,
        "suggestions": list[str]
    }
}
```

## Testing Strategy

### Unit Testing

**Frontend Unit Tests:**
- Component rendering with various props
- Form validation logic
- State management in hooks
- API call mocking and error handling

**Backend Unit Tests:**
- ConfigManager read/write operations
- PromptManager extraction and injection
- ValidationService rules
- Path resolution and validation

### Property-Based Testing

Property-based tests will use the `hypothesis` library for Python to generate random test cases:

**Test Framework**: Hypothesis (Python)

**Configuration**: Each property test will run a minimum of 100 iterations with randomly generated inputs.

**Property Test Tagging**: Each property-based test will include a comment with the format:
`# Feature: settings-interface, Property {number}: {property_text}`

### Integration Testing

- End-to-end tests for complete workflows (load settings → modify → save → verify)
- PyWebView bridge communication tests
- File system operations with temporary test directories
- Build process tests with minimal test applications

### Manual Testing

- UI/UX testing across different screen sizes
- Native file dialog integration
- Build executable and test on clean system
- Accessibility testing with keyboard navigation

## Implementation Notes

### File Modification Strategy

To safely modify Python source files without breaking them:

1. Use Python's `ast` module to parse the source file into an Abstract Syntax Tree
2. Locate the target variable assignment node
3. Replace the value while preserving formatting
4. Write back to file with proper indentation

Alternative approach for simpler cases:
1. Use regex to locate the variable assignment
2. Replace the value between triple quotes
3. Preserve surrounding code structure

### Build Configuration

PyInstaller spec file template:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['local_client/run_client.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend', 'backend'),
        ('local_client', 'local_client'),
        ('.env', '.'),
    ],
    hiddenimports=[
        'google.generativeai',
        'pyautogui',
        'pygetwindow',
        'PIL',
        'cv2',
        'flask',
        'flask_socketio',
        'flask_cors',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='JARVIS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for GUI-only mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Optional application icon
)
```

### React Build Integration

The React frontend will be built into static files and bundled with the Python application:

1. Run `npm run build` to create production build in `settings_ui/dist`
2. PyWebView will serve these static files from the bundled directory
3. For development, use `npm run dev` with PyWebView pointing to the dev server

### Security Considerations

1. **Input Sanitization**: All user input must be validated before writing to files
2. **Path Traversal Prevention**: Validate that file paths don't escape the project directory
3. **Code Injection Prevention**: Use AST manipulation instead of string concatenation for Python file modifications
4. **Backup Strategy**: Always create backups before modifying configuration files
