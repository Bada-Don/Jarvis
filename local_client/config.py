# JARVIS Local Client Configuration
# Edit these settings to match your FlexiSIGN installation

# Server connection
SERVER_URL = 'http://localhost:5000'

# FlexiSIGN Process Settings
FLEXISIGN_PROCESS_NAME = "Production Suite Scanner 10.5.1 Build 1806 Protected"
FLEXISIGN_EXE_PATH = r"D:\Program Files\FLEXI 10 full version _by AARY-meii\FlexiSign_Pro_10.5\STEP 2\Production Suite Scanner 10.5.1 Build 1806 Protected.exe"
FLEXISIGN_WINDOW_TITLE = "FlexiSIGN-PRO"

# Startup Modal Settings
# Set STARTUP_MODAL_ENABLED to True if FlexiSIGN shows a modal dialog on startup
STARTUP_MODAL_ENABLED = True
STARTUP_MODAL_TITLE = "FlexiSIGN"  # The title of the modal window (can be partial match)
STARTUP_MODAL_BUTTON = "OK"  # The button text to click
STARTUP_MODAL_TIMEOUT = 30  # How long to wait for the modal (seconds)

# Timing Settings
PROCESS_START_WAIT = 5  # Seconds to wait after starting a process
WINDOW_SWITCH_WAIT = 1  # Seconds to wait after switching windows
MODAL_CHECK_INTERVAL = 1  # How often to check for modal (seconds)
