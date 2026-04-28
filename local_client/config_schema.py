"""
Configuration Schema and Defaults for JARVIS Desktop Application

This module defines the default configuration structure, validation rules,
and configuration templates for the JARVIS desktop application.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
import os
from pathlib import Path

# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

DEFAULT_CONFIG = {
    "version": "1.0.0",
    "first_run_complete": False,
    
    "system": {
        "server_url": "http://localhost:5000",
        "windows_username": "",
    },
    
    "llm": {
        "provider": "gemini",
        "gemini_api_key": "",
        "openai_api_key": "",
        "local_model_name": "gemma:2b",
        "local_base_url": "http://localhost:11434/v1",
    },
    
    "paths": {
        "desktop": "",
        "documents": "",
        "downloads": "",
        "stickers": "",
    },
    
    "firebase": {
        "device_id": "",
        "paired": False,
        "paired_device_id": "",
        "credentials_path": "data/firebase-admin-credentials.json",
    },
    
    "timing": {
        "action_delay": 0.3,
        "app_launch_wait": 3,
        "hotkey_delay": 0.5,
        "pre_type_delay": 0.2,
        "screenshot_delay": 0.5,
        "window_activation_timeout": 10,
        "window_poll_interval": 0.5,
        "retry_delay": 2,
        "verification_delay": 1,
    },
    
    "verification": {
        "enabled": False,
        "max_retries": 0,
        "confidence_threshold": 0.7,
    },
    
    "window_manager": {
        "activation_attempts": 3,
        "verbose": True,
    },
    
    "flexisign": {
        "process_name": "Production Suite Scanner 10.5.1 Build 1806 Protected",
        "exe_path": "",
        "window_title": "FlexiSIGN-PRO",
        "startup_modal_enabled": True,
        "startup_modal_title": "FlexiSIGN",
        "startup_modal_button": "OK",
        "startup_modal_timeout": 30,
    },
}

# =============================================================================
# VALIDATION RULES
# =============================================================================

@dataclass
class ValidationRule:
    """Represents a validation rule for a configuration field"""
    field_path: str
    rule_type: str  # 'required', 'type', 'range', 'path_exists', 'url', 'api_key'
    params: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""

# Configuration validation rules
VALIDATION_RULES = [
    # Version
    ValidationRule(
        field_path="version",
        rule_type="required",
        error_message="Configuration version is required"
    ),
    ValidationRule(
        field_path="version",
        rule_type="type",
        params={"expected_type": str},
        error_message="Version must be a string"
    ),
    
    # System
    ValidationRule(
        field_path="system.server_url",
        rule_type="url",
        error_message="Server URL must be a valid URL"
    ),
    
    # LLM
    ValidationRule(
        field_path="llm.provider",
        rule_type="type",
        params={"expected_type": str},
        error_message="LLM provider must be a string"
    ),
    ValidationRule(
        field_path="llm.provider",
        rule_type="choice",
        params={"choices": ["gemini", "openai", "local"]},
        error_message="LLM provider must be 'gemini', 'openai', or 'local'"
    ),
    
    # Timing
    ValidationRule(
        field_path="timing.action_delay",
        rule_type="range",
        params={"min": 0.0, "max": 10.0},
        error_message="Action delay must be between 0 and 10 seconds"
    ),
    ValidationRule(
        field_path="timing.app_launch_wait",
        rule_type="range",
        params={"min": 0.0, "max": 60.0},
        error_message="App launch wait must be between 0 and 60 seconds"
    ),
    
    # Verification
    ValidationRule(
        field_path="verification.enabled",
        rule_type="type",
        params={"expected_type": bool},
        error_message="Verification enabled must be a boolean"
    ),
    ValidationRule(
        field_path="verification.max_retries",
        rule_type="range",
        params={"min": 0, "max": 10},
        error_message="Max retries must be between 0 and 10"
    ),
    ValidationRule(
        field_path="verification.confidence_threshold",
        rule_type="range",
        params={"min": 0.0, "max": 1.0},
        error_message="Confidence threshold must be between 0.0 and 1.0"
    ),
    
    # Windows Username
    ValidationRule(
        field_path="system.windows_username",
        rule_type="required",
        error_message="Windows username is required"
    ),
]

# =============================================================================
# CONFIGURATION DATA CLASSES
# =============================================================================

@dataclass
class SystemConfig:
    """System configuration"""
    server_url: str = "http://localhost:5000"
    windows_username: str = ""

@dataclass
class LLMConfig:
    """LLM provider configuration"""
    provider: str = "gemini"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    local_model_name: str = "gemma:2b"
    local_base_url: str = "http://localhost:11434/v1"

@dataclass
class PathsConfig:
    """System paths configuration"""
    desktop: str = ""
    documents: str = ""
    downloads: str = ""
    stickers: str = ""

@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    device_id: str = ""
    paired: bool = False
    paired_device_id: str = ""
    credentials_path: str = "data/firebase-admin-credentials.json"

@dataclass
class TimingConfig:
    """Timing configuration"""
    action_delay: float = 0.3
    app_launch_wait: float = 3.0
    hotkey_delay: float = 0.5
    pre_type_delay: float = 0.2
    screenshot_delay: float = 0.5
    window_activation_timeout: float = 10.0
    window_poll_interval: float = 0.5
    retry_delay: float = 2.0
    verification_delay: float = 1.0

@dataclass
class VerificationConfig:
    """Verification configuration"""
    enabled: bool = False
    max_retries: int = 0
    confidence_threshold: float = 0.7

@dataclass
class WindowManagerConfig:
    """Window manager configuration"""
    activation_attempts: int = 3
    verbose: bool = True

@dataclass
class FlexiSignConfig:
    """FlexiSign-specific configuration"""
    process_name: str = "Production Suite Scanner 10.5.1 Build 1806 Protected"
    exe_path: str = ""
    window_title: str = "FlexiSIGN-PRO"
    startup_modal_enabled: bool = True
    startup_modal_title: str = "FlexiSIGN"
    startup_modal_button: str = "OK"
    startup_modal_timeout: int = 30

@dataclass
class Configuration:
    """Complete JARVIS configuration"""
    version: str = "1.0.0"
    first_run_complete: bool = False
    system: SystemConfig = field(default_factory=SystemConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    firebase: FirebaseConfig = field(default_factory=FirebaseConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    verification: VerificationConfig = field(default_factory=VerificationConfig)
    window_manager: WindowManagerConfig = field(default_factory=WindowManagerConfig)
    flexisign: FlexiSignConfig = field(default_factory=FlexiSignConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Configuration':
        """Create configuration from dictionary"""
        return cls(
            version=data.get("version", "1.0.0"),
            first_run_complete=data.get("first_run_complete", False),
            system=SystemConfig(**data.get("system", {})),
            llm=LLMConfig(**data.get("llm", {})),
            paths=PathsConfig(**data.get("paths", {})),
            firebase=FirebaseConfig(**data.get("firebase", {})),
            timing=TimingConfig(**data.get("timing", {})),
            verification=VerificationConfig(**data.get("verification", {})),
            window_manager=WindowManagerConfig(**data.get("window_manager", {})),
            flexisign=FlexiSignConfig(**data.get("flexisign", {})),
        )

# =============================================================================
# CONFIGURATION TEMPLATE
# =============================================================================

CONFIG_TEMPLATE = """# JARVIS Desktop Application Configuration
# This file is automatically generated and managed by the Configuration Manager
# Manual edits may be overwritten - use the Settings UI to modify configuration

# Configuration Version: {version}
# First Run Complete: {first_run_complete}

# =============================================================================
# SERVER CONNECTION
# =============================================================================
SERVER_URL = r"{system.server_url}"

# =============================================================================
# LLM SETTINGS
# =============================================================================
LLM_PROVIDER = '{llm.provider}'
GEMINI_API_KEY = '{llm.gemini_api_key}'
OPENAI_API_KEY = '{llm.openai_api_key}'
LOCAL_MODEL_NAME = '{llm.local_model_name}'
LOCAL_BASE_URL = '{llm.local_base_url}'

# =============================================================================
# SYSTEM INFORMATION
# =============================================================================
WINDOWS_USERNAME = '{system.windows_username}'

# User-specific paths
DESKTOP_PATH = r"{paths.desktop}"
DOCUMENTS_PATH = r"{paths.documents}"
DOWNLOADS_PATH = r"{paths.downloads}"
STICKERS_PATH = r"{paths.stickers}"

# =============================================================================
# FIREBASE CONFIGURATION
# =============================================================================
FIREBASE_DEVICE_ID = '{firebase.device_id}'
FIREBASE_PAIRED = {firebase.paired}
FIREBASE_PAIRED_DEVICE_ID = '{firebase.paired_device_id}'
FIREBASE_CREDENTIALS_PATH = r"{firebase.credentials_path}"

# =============================================================================
# TIMING SETTINGS (seconds)
# =============================================================================
ACTION_DELAY = {timing.action_delay}
APP_LAUNCH_WAIT = {timing.app_launch_wait}
HOTKEY_DELAY = {timing.hotkey_delay}
PRE_TYPE_DELAY = {timing.pre_type_delay}
SCREENSHOT_DELAY = {timing.screenshot_delay}
WINDOW_ACTIVATION_TIMEOUT = {timing.window_activation_timeout}
WINDOW_POLL_INTERVAL = {timing.window_poll_interval}
RETRY_DELAY = {timing.retry_delay}
VERIFICATION_DELAY = {timing.verification_delay}

# =============================================================================
# VERIFICATION AND RETRY SETTINGS
# =============================================================================
VERIFICATION_ENABLED = {verification.enabled}
MAX_RETRIES = {verification.max_retries}
CONFIDENCE_THRESHOLD = {verification.confidence_threshold}

# =============================================================================
# WINDOW MANAGER SETTINGS
# =============================================================================
WINDOW_ACTIVATION_ATTEMPTS = {window_manager.activation_attempts}
WINDOW_MANAGER_VERBOSE = {window_manager.verbose}

# =============================================================================
# FLEXISIGN-SPECIFIC SETTINGS
# =============================================================================
FLEXISIGN_PROCESS_NAME = '{flexisign.process_name}'
FLEXISIGN_EXE_PATH = r"{flexisign.exe_path}"
FLEXISIGN_WINDOW_TITLE = '{flexisign.window_title}'
STARTUP_MODAL_ENABLED = {flexisign.startup_modal_enabled}
STARTUP_MODAL_TITLE = '{flexisign.startup_modal_title}'
STARTUP_MODAL_BUTTON = '{flexisign.startup_modal_button}'
STARTUP_MODAL_TIMEOUT = {flexisign.startup_modal_timeout}
"""

def get_config_template(config: Configuration) -> str:
    """Generate configuration file content from Configuration object"""
    return CONFIG_TEMPLATE.format(
        version=config.version,
        first_run_complete=config.first_run_complete,
        system=config.system,
        llm=config.llm,
        paths=config.paths,
        firebase=config.firebase,
        timing=config.timing,
        verification=config.verification,
        window_manager=config.window_manager,
        flexisign=config.flexisign,
    )
