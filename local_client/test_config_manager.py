"""
Test script for ConfigurationManager

This script tests the basic functionality of the ConfigurationManager class.
"""

import sys
from pathlib import Path
import json
import tempfile
import shutil

# Add local_client to path
sys.path.insert(0, str(Path(__file__).parent))

from config_manager import ConfigurationManager
from config_schema import Configuration, DEFAULT_CONFIG


def test_create_new_config():
    """Test creating a new configuration"""
    print("Test 1: Creating new configuration...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        assert manager.config is not None
        assert manager.config.version == "1.0.0"
        assert manager.config.first_run_complete == False
        print("✓ New configuration created successfully")


def test_save_and_load():
    """Test saving and loading configuration"""
    print("\nTest 2: Saving and loading configuration...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        
        # Create and save
        manager1 = ConfigurationManager(config_path)
        manager1.set("llm.provider", "openai")
        manager1.set("system.windows_username", "testuser")
        manager1.save()
        
        # Load in new instance
        manager2 = ConfigurationManager(config_path)
        
        assert manager2.get("llm.provider") == "openai"
        assert manager2.get("system.windows_username") == "testuser"
        print("✓ Configuration saved and loaded successfully")


def test_validation():
    """Test configuration validation"""
    print("\nTest 3: Configuration validation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        # Valid configuration
        errors = manager.validate()
        print(f"  Validation errors for default config: {len(errors)}")
        
        # Invalid provider
        manager.set("llm.provider", "invalid")
        errors = manager.validate()
        assert len(errors) > 0
        assert any("provider" in err.lower() for err in errors)
        print("✓ Validation correctly detects invalid provider")
        
        # Fix it
        manager.set("llm.provider", "gemini")
        errors = manager.validate()
        print(f"  Validation errors after fix: {len(errors)}")


def test_backup_restore():
    """Test backup and restore functionality"""
    print("\nTest 4: Backup and restore...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        # Set some values
        manager.set("llm.provider", "openai")
        manager.set("system.windows_username", "original")
        manager.save()
        
        # Create backup
        backup_path = manager.backup()
        assert backup_path.exists()
        print(f"  Backup created: {backup_path.name}")
        
        # Change values
        manager.set("system.windows_username", "modified")
        manager.save()
        
        # Restore from backup
        manager.restore(backup_path)
        
        assert manager.get("system.windows_username") == "original"
        print("✓ Backup and restore working correctly")


def test_first_run_detection():
    """Test first-run detection"""
    print("\nTest 5: First-run detection...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        assert manager.is_first_run() == True
        print("  First run detected: True")
        
        manager.mark_configured()
        assert manager.is_first_run() == False
        print("  After marking configured: False")
        
        # Reload and check persistence
        manager2 = ConfigurationManager(config_path)
        assert manager2.is_first_run() == False
        print("✓ First-run detection working correctly")


def test_get_set():
    """Test get and set methods"""
    print("\nTest 6: Get and set methods...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        # Test nested get/set
        manager.set("timing.action_delay", 1.5)
        assert manager.get("timing.action_delay") == 1.5
        
        manager.set("verification.enabled", True)
        assert manager.get("verification.enabled") == True
        
        # Test default value
        assert manager.get("nonexistent.key", "default") == "default"
        
        print("✓ Get and set methods working correctly")


def test_update_from_dict():
    """Test updating configuration from dictionary"""
    print("\nTest 7: Update from dictionary...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.py"
        manager = ConfigurationManager(config_path)
        
        updates = {
            "llm": {
                "provider": "openai",
                "openai_api_key": "test-key-123"
            },
            "timing": {
                "action_delay": 2.0
            }
        }
        
        manager.update_from_dict(updates)
        
        assert manager.get("llm.provider") == "openai"
        assert manager.get("llm.openai_api_key") == "test-key-123"
        assert manager.get("timing.action_delay") == 2.0
        
        print("✓ Update from dictionary working correctly")


def main():
    """Run all tests"""
    print("=" * 60)
    print("ConfigurationManager Test Suite")
    print("=" * 60)
    
    try:
        test_create_new_config()
        test_save_and_load()
        test_validation()
        test_backup_restore()
        test_first_run_detection()
        test_get_set()
        test_update_from_dict()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
