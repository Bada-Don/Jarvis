# JARVIS Local Client Configuration

# =============================================================================
# SERVER CONNECTION
# =============================================================================
SERVER_URL = 'http://localhost:5000'

# =============================================================================
# SYSTEM INFORMATION
# =============================================================================
# Windows username for path generation
# This is used by the planner model to generate correct file paths
WINDOWS_USERNAME = 'harsh'

# =============================================================================
# TIMING SETTINGS (seconds)
# =============================================================================
# Default delay after each step
ACTION_DELAY = 0.3

# Extended delay after launching an application
APP_LAUNCH_WAIT = 3.0

# Delay after hotkey combinations (Ctrl+C, Alt+Tab, etc.)
HOTKEY_DELAY = 0.5

# Small delay before typing text
PRE_TYPE_DELAY = 0.2

# Screenshot delay before vision analysis
SCREENSHOT_DELAY = 0.5

# Maximum time to wait for a window to appear after app launch
WINDOW_ACTIVATION_TIMEOUT = 10.0

# How often to poll for window appearance
WINDOW_POLL_INTERVAL = 0.5

# =============================================================================
# WINDOW MANAGER SETTINGS
# =============================================================================
# Maximum attempts to activate a window
WINDOW_ACTIVATION_ATTEMPTS = 3

# Verbose logging for window operations
WINDOW_MANAGER_VERBOSE = True

# =============================================================================
# FLEXISIGN-SPECIFIC SETTINGS (only used in FlexiSIGN mode)
# =============================================================================
FLEXISIGN_PROCESS_NAME = "Production Suite Scanner 10.5.1 Build 1806 Protected"
FLEXISIGN_EXE_PATH = r"D:\Program Files\FLEXI 10 full version _by AARY-meii\FlexiSign_Pro_10.5\STEP 2\Production Suite Scanner 10.5.1 Build 1806 Protected.exe"
FLEXISIGN_WINDOW_TITLE = "FlexiSIGN-PRO"

# Startup Modal Settings
STARTUP_MODAL_ENABLED = True
STARTUP_MODAL_TITLE = "FlexiSIGN"
STARTUP_MODAL_BUTTON = "OK"
STARTUP_MODAL_TIMEOUT = 30

# =============================================================================
# LEGACY TIMING SETTINGS
# =============================================================================
PROCESS_START_WAIT = 5
WINDOW_SWITCH_WAIT = 1
MODAL_CHECK_INTERVAL = 1
