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
      // Helper function to check if API methods are actually available
      const isApiReady = () => {
        return window.pywebview?.api &&
          typeof window.pywebview.api.get_settings === 'function' &&
          typeof window.pywebview.api.is_first_run === 'function';
      };

      // Check if already available
      if (typeof window !== 'undefined' && isApiReady()) {
        this.pywebviewReady = true;
        console.log('✓ PyWebView API already available - using Python backend');
        resolve(true);
        return;
      }

      // Listen for pywebviewready event
      if (typeof window !== 'undefined') {
        window.addEventListener('pywebviewready', () => {
          if (isApiReady()) {
            this.pywebviewReady = true;
            console.log('✓ PyWebView API ready event received - using Python backend');
            resolve(true);
          } else {
            console.warn('✗ pywebviewready event fired but API methods not available yet');
            // Don't resolve yet, let the polling continue
          }
        });

        // Fallback: check periodically for 5 seconds
        let attempts = 0;
        const maxAttempts = 50; // 5 seconds
        const checkInterval = setInterval(() => {
          attempts++;
          if (isApiReady()) {
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
      // Only return mock data in development mode if explicitly requested or if no backend is expected
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        console.warn('PyWebView API not available - returning mock data for development');
        return this.getMockSettings();
      }
      throw new Error('JARVIS Backend API not ready. Please try again or check if the backend is running.');
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

  async generatePairingCode() {
    if (!this.isReady()) {
      console.log('Mock: Generating pairing code');
      return {
        token: 'pair_mock123456',
        qrCodeData: 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        expiresAt: Math.floor(Date.now() / 1000) + 300,
      };
    }
    const response = await window.pywebview.api.generate_pairing_code();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to generate pairing code');
    }
    return response.data;
  }

  async checkPairingStatus(token) {
    if (!this.isReady()) {
      console.log('Mock: Checking pairing status for token', token);
      return { paired: false };
    }
    const response = await window.pywebview.api.check_pairing_status(token);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to check pairing status');
    }
    return response.data;
  }

  async isFirstRun() {
    await this.waitForPyWebView();

    if (!this.isReady()) {
      console.log('Mock: Checking first run status');
      return false; // In development, assume not first run
    }

    console.log('Calling Python backend: is_first_run()');
    const response = await window.pywebview.api.is_first_run();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to check first run status');
    }
    return response.data;
  }

  async completeFirstRun(configuration) {
    if (!this.isReady()) {
      console.log('Mock: Completing first run with configuration', configuration);
      return;
    }
    const response = await window.pywebview.api.complete_first_run(configuration);
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to complete first run');
    }
  }

  getMockSettings() {
    return {
      system: {
        server_url: 'http://localhost:5000',
        windows_username: 'user',
      },
      timing: {
        action_delay: 0.3,
        app_launch_wait: 3.0,
        hotkey_delay: 0.5,
        pre_type_delay: 0.2,
        screenshot_delay: 0.5,
        window_activation_timeout: 10.0,
        window_poll_interval: 0.5,
        retry_delay: 2.0,
        verification_delay: 1.0,
      },
      window_manager: {
        activation_attempts: 3,
        verbose: true,
      },
      paths: {
        desktop: '',
        documents: '',
        downloads: '',
        stickers: '',
      },
      llm: {
        provider: 'gemini',
        gemini_api_key: '',
        openai_api_key: '',
      },
      firebase: {
        device_id: '',
        paired: false,
        paired_device_id: '',
        credentials_path: 'data/firebase-admin-credentials.json',
      },
      flexisign: {
        process_name: 'Production Suite Scanner 10.5.1 Build 1806 Protected',
        exe_path: '',
        window_title: 'FlexiSIGN-PRO',
        startup_modal_enabled: true,
        startup_modal_title: 'FlexiSIGN',
        startup_modal_button: 'OK',
        startup_modal_timeout: 30,
      },
      verification: {
        enabled: false,
        max_retries: 0,
        confidence_threshold: 0.7,
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
