"""
Example usage of ConfigurationManager

This script demonstrates how to use the ConfigurationManager class
in the JARVIS desktop application.
"""

from pathlib import Path
from config_manager import ConfigurationManager

def main():
    """Example usage of ConfigurationManager"""
    
    # Initialize configuration manager
    # By default, it uses local_client/config.py
    manager = ConfigurationManager()
    
    print("=" * 60)
    print("ConfigurationManager Example Usage")
    print("=" * 60)
    
    # Check if first run
    if manager.is_first_run():
        print("\n✓ First run detected - setup wizard should be shown")
        
        # Simulate first-run configuration
        print("\nConfiguring application...")
        manager.set("system.windows_username", "demo_user")
        manager.set("llm.provider", "gemini")
        manager.set("llm.gemini_api_key", "YOUR_GEMINI_API_KEY_HERE")  # Replace with your actual API key
        manager.set("paths.desktop", r"C:\Users\demo_user\Desktop")
        manager.set("paths.documents", r"C:\Users\demo_user\Documents")
        manager.set("paths.downloads", r"C:\Users\demo_user\Downloads")
        
        # Mark setup as complete
        manager.mark_configured()
        manager.save()
        print("✓ Configuration saved")
    else:
        print("\n✓ Configuration already exists")
    
    # Display current configuration
    print("\nCurrent Configuration:")
    print(f"  Version: {manager.get('version')}")
    print(f"  First Run Complete: {manager.get('first_run_complete')}")
    print(f"  LLM Provider: {manager.get('llm.provider')}")
    print(f"  Windows Username: {manager.get('system.windows_username')}")
    print(f"  Desktop Path: {manager.get('paths.desktop')}")
    
    # Validate configuration
    print("\nValidating configuration...")
    errors = manager.validate()
    if errors:
        print("✗ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration is valid")
    
    # Update a setting
    print("\nUpdating timing settings...")
    manager.set("timing.action_delay", 0.5)
    manager.save()
    print(f"✓ Action delay set to: {manager.get('timing.action_delay')}s")
    
    # List backups
    backups = manager.list_backups()
    print(f"\nAvailable backups: {len(backups)}")
    for backup in backups[:3]:  # Show first 3
        print(f"  - {backup.name}")
    
    # Get configuration as dictionary
    config_dict = manager.get_config_dict()
    print(f"\nConfiguration sections: {list(config_dict.keys())}")
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
