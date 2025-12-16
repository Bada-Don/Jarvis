// API service for communicating with PyWebView backend

class APIService {
  isReady() {
    return typeof window !== 'undefined' && !!window.pywebview?.api;
  }

  async getSettings() {
    if (!this.isReady()) {
      // Return mock data for development
      return this.getMockSettings();
    }
    const response = await window.pywebview.api.get_settings();
    if (!response.success) {
      throw new Error(response.error?.message || 'Failed to get settings');
    }
    return response.data;
  }

  async saveSettings(settings) {
    if (!this.isReady()) {
      console.log('Mock: Saving settings', settings);
      return;
    }
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
          GENERAL_SYSTEM_PROMPT: '',
          FLEXISIGN_SYSTEM_PROMPT: '',
        },
        vision: {
          GENERAL_VISION_PROMPT: '',
          VERIFICATION_PROMPT: '',
          FLEXISIGN_VISION_PROMPT: '',
        },
      },
    };
  }
}

export const api = new APIService();
