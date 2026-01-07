// API service for communicating with PyWebView backend

class APIService {
  constructor() {
    this.pywebviewReady = false;
    this.readyPromise = null;
    this.initPyWebView();
  }

  initPyWebView() {
    // Create a promise that resolves when PyWebView is ready
    this.readyPromise = new Promise((resolve) => {
      // Check if already available
      if (typeof window !== 'undefined' && window.pywebview?.api) {
        this.pywebviewReady = true;
        console.log('✓ PyWebView API already available - using Python backend');
        resolve(true);
        return;
      }

      // Listen for pywebviewready event
      if (typeof window !== 'undefined') {
        window.addEventListener('pywebviewready', () => {
          if (window.pywebview?.api) {
            this.pywebviewReady = true;
            console.log('✓ PyWebView API ready event received - using Python backend');
            resolve(true);
          } else {
            console.warn('✗ pywebviewready event fired but API not available');
            resolve(false);
          }
        });

        // Fallback: check periodically for 5 seconds
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds
        const checkInterval = setInterval(() => {
          attempts++;
          if (window.pywebview?.api) {
            this.pywebviewReady = true;
            console.log(`✓ PyWebView API detected (attempt ${attempts}) - using Python backend`);
            clearInterval(checkInterval);
            resolve(true);
          } else if (attempts >= maxAttempts) {
            console.log('✗ PyWebView API not found after 5 seconds - using mock data (development mode)');
            clearInterval(checkInterval);
            resolve(false);
          }
        }, 100);
      } else {
        console.log('✗ Window not available - using mock data');
        resolve(false);
      }
    });
  }

  isReady() {
    return this.pywebviewReady;
  }

  async waitForPyWebView() {
    // Wait for the ready promise to resolve
    await this.readyPromise;
    return this.isReady();
  }

  async getSettings() {
    // Wait for PyWebView to be ready (important on first load)
    await this.waitForPyWebView();

    if (!this.isReady()) {
      console.warn('PyWebView API not available - returning mock data');
      // Return mock data for development
      return this.getMockSettings();
    }

    console.log('Calling Python backend: get_settings()');
    const response = await window.pywebview.api.get_settings();
    console.log('Response from Python backend:', response.success ? '✓ Success' : '✗ Failed');

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to get settings');
    }
    return response.data;
  }

  async saveSettings(settings) {
    await this.waitForPyWebView();

    if (!this.isReady()) {
      console.warn('Mock: Saving settings (PyWebView not available)', settings);
      return;
    }

    console.log('Calling Python backend: save_settings()');
    const response = await window.pywebview.api.save_settings(settings);

    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to save settings');
    }
  }

  async resetSetting(key) {
    if (!this.isReady()) {
      console.log('Mock: Resetting setting', key);
      return null;
    }
    const response = await window.pywebview.api.reset_setting(key);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to reset setting');
    }
    return response.data;
  }

  async validateSetting(key, value) {
    if (!this.isReady()) {
      return true;
    }
    const response = await window.pywebview.api.validate_setting(key, value);
    if (!response.success) {
      throw new Error(response.error?.message || 'Validation failed');
    }
    return response.data;
  }

  async browseFile(title, fileTypes = [], saveMode = false) {
    if (!this.isReady()) {
      return '/mock/path/to/file.txt';
    }
    return await window.pywebview.api.browse_file(title, fileTypes, saveMode);
  }

  async browseFolder(title) {
    if (!this.isReady()) {
      return '/mock/path/to/folder';
    }
    return await window.pywebview.api.browse_folder(title);
  }

  async validatePath(path, isDirectory) {
    if (!this.isReady()) {
      return true;
    }
    const response = await window.pywebview.api.validate_path(path, isDirectory);
    if (!response.success) {
      throw new Error(response.error?.message || 'Path validation failed');
    }
    return response.data;
  }

  async exportConfig(filePath) {
    if (!this.isReady()) {
      console.log('Mock: Exporting configuration to', filePath);
      return;
    }
    const response = await window.pywebview.api.export_config(filePath);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to export configuration');
    }
  }

  async importConfig(filePath) {
    if (!this.isReady()) {
      console.log('Mock: Importing configuration from', filePath);
      return { warnings: [] };
    }
    const response = await window.pywebview.api.import_config(filePath);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to import configuration');
    }
    return { warnings: response.warnings };
  }

  async testConfiguration() {
    if (!this.isReady()) {
      // Return mock test results for development
      return {
        passed: [
          { test: 'Settings Validation', message: 'All settings are valid' },
          { test: 'Server URL', message: 'Server URL is valid: http://localhost:5000' }
        ],
        failed: [
          { test: 'FlexiSIGN Executable', message: 'FlexiSIGN executable not found', guidance: 'Update FLEXISIGN_EXE_PATH to point to the correct executable' }
        ],
        warnings: [
          { test: 'FlexiSIGN Process', message: 'FlexiSIGN process not currently running' }
        ],
        summary: {
          total_tests: 3,
          passed_count: 2,
          failed_count: 1,
          warning_count: 1
        }
      };
    }
    const response = await window.pywebview.api.test_configuration();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to test configuration');
    }
    return response.data;
  }

  async startBuild(options) {
    if (!this.isReady()) {
      console.log('Mock: Starting build with options', options);
      return;
    }
    const response = await window.pywebview.api.start_build(options);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to start build');
    }
  }

  async getBuildStatus() {
    if (!this.isReady()) {
      // Return mock build status for development
      return {
        is_building: false,
        progress: 0,
        current_step: '',
        logs: []
      };
    }
    const response = await window.pywebview.api.get_build_status();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to get build status');
    }
    return response.data;
  }

  async openBuildFolder() {
    if (!this.isReady()) {
      console.log('Mock: Opening build folder');
      return;
    }
    const response = await window.pywebview.api.open_build_folder();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to open build folder');
    }
  }

  getMockSettings() {
    return {
      system: {
        SERVER_URL: 'http://localhost:5000',
        WINDOWS_USERNAME: 'user',
      },
      timing: {
        ACTION_DELAY: 0.3,
        APP_LAUNCH_WAIT: 3.0,
        HOTKEY_DELAY: 0.5,
        PRE_TYPE_DELAY: 0.2,
        SCREENSHOT_DELAY: 0.5,
        WINDOW_ACTIVATION_TIMEOUT: 10.0,
        WINDOW_POLL_INTERVAL: 0.5,
      },
      window_manager: {
        WINDOW_ACTIVATION_ATTEMPTS: 3,
        WINDOW_MANAGER_VERBOSE: true,
      },
      paths: {},
      flexisign: {
        FLEXISIGN_PROCESS_NAME: 'Production Suite Scanner 10.5.1 Build 1806 Protected',
        FLEXISIGN_EXE_PATH: '',
        FLEXISIGN_WINDOW_TITLE: 'FlexiSIGN-PRO',
        STARTUP_MODAL_ENABLED: true,
        STARTUP_MODAL_TITLE: 'FlexiSIGN',
        STARTUP_MODAL_BUTTON: 'OK',
        STARTUP_MODAL_TIMEOUT: 30,
      },
      verification: {
        VERIFICATION_ENABLED: false,
        MAX_RETRIES: 0,
        RETRY_DELAY: 2.0,
        VERIFICATION_DELAY: 1.0,
        CONFIDENCE_THRESHOLD: 0.7,
      },
      prompts: {
        planner: {
          GENERAL_SYSTEM_PROMPT: 'You are JARVIS, an AI assistant that automates computer tasks...\n\n(This is mock data for development. In production, the actual prompt will be loaded from backend/planner_service.py)',
          FLEXISIGN_SYSTEM_PROMPT: 'You are a FlexiSIGN Automation Agent...\n\n(This is mock data for development. In production, the actual prompt will be loaded from backend/planner_service.py)',
        },
        vision: {
          GENERAL_VISION_PROMPT: 'Vision prompt for general UI element identification...\n\n(This is mock data for development. In production, the actual prompt will be loaded from local_client/vision_service.py)',
          VERIFICATION_PROMPT: 'Prompt for task verification...\n\n(This is mock data for development. In production, the actual prompt will be loaded from local_client/vision_service.py)',
          FLEXISIGN_VISION_PROMPT: 'Vision prompt for FlexiSIGN UI elements...\n\n(This is mock data for development. In production, the actual prompt will be loaded from local_client/vision_service.py)',
        },
      },
    };
  }
}

export const api = new APIService();
