#!/usr/bin/env python3
"""
JARVIS - AI Desktop Assistant
Main launcher script for the JARVIS application.

This script initializes and manages all JARVIS components:
- Backend Server (Flask API)
- Local Client (Automation executor)
- Settings UI (Configuration interface)
- System Tray (Application control)
"""

import sys
import os
import argparse
import logging
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from application_launcher import ApplicationLauncher
from system_tray_manager import SystemTrayManager


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Setup command-line argument parser.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='JARVIS - AI Desktop Assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python JARVIS.py                    # Start with default settings
  python JARVIS.py --no-tray          # Start without system tray
  python JARVIS.py --debug            # Start with debug logging
  python JARVIS.py --component backend # Start only backend component
        """
    )
    
    parser.add_argument(
        '--no-tray',
        action='store_true',
        help='Disable system tray icon'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--component',
        choices=['backend', 'local_client', 'settings_ui'],
        help='Start only a specific component (for testing)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Custom log file path'
    )
    
    parser.add_argument(
        '--no-monitor',
        action='store_true',
        help='Disable automatic component restart on crash'
    )
    
    return parser


def print_banner():
    """Print JARVIS startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║        ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗            ║
    ║        ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝            ║
    ║        ██║███████║██████╔╝██║   ██║██║███████╗            ║
    ║   ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║            ║
    ║   ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║            ║
    ║    ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝            ║
    ║                                                           ║
    ║              AI Desktop Assistant v1.0.0                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point for JARVIS application."""
    # Ensure stdout can handle UTF-8 symbols (emojis)
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
            
    # Parse command-line arguments
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Setup logging level
    log_level = logging.DEBUG if args.debug else logging.INFO
    
    # Initialize Application Launcher
    launcher = ApplicationLauncher(log_level=log_level)
    
    # System tray manager (optional)
    tray_manager = None
    
    try:
        # Start all components
        if not launcher.start():
            print('\n❌ Failed to start JARVIS components')
            print('Check logs for details: data/logs/')
            return 1
        
        # Setup system tray (if not disabled)
        if not args.no_tray:
            print('\n🔧 Setting up system tray...')
            
            def show_settings():
                """Callback to show settings UI."""
                launcher.logger.info('Show settings requested from tray')
                # The settings UI should already be running
                # This would bring it to foreground (implementation depends on UI framework)
            
            def restart_all():
                """Callback to restart all components."""
                launcher.logger.info('Restart all requested from tray')
                launcher.restart_all()
            
            def quit_app():
                """Callback to quit application."""
                launcher.logger.info('Quit requested from tray')
                launcher.shutdown()
            
            def get_status():
                """Callback to get component status."""
                return launcher.get_status()
            
            tray_manager = SystemTrayManager(
                on_show_settings=show_settings,
                on_restart=restart_all,
                on_quit=quit_app,
                get_status=get_status
            )
            
            # Run tray in separate thread
            tray_thread = threading.Thread(target=tray_manager.run, daemon=True)
            tray_thread.start()
            
            print('✅ System tray icon created')
        
        print('\n' + '=' * 60)
        print('✅ JARVIS is now running!')
        print('=' * 60)
        print('\nComponent Status:')
        status = launcher.get_status()
        for component_id, info in status.items():
            status_icon = '✅' if info['status'] == 'running' else '❌'
            print(f'  {status_icon} {info["name"]}: {info["status"]}')
        
        if not args.no_tray:
            print('\n💡 JARVIS is running in the system tray')
            print('   Right-click the tray icon for options')
        
        print('\n📝 Logs: data/logs/')
        print('⌨️  Press Ctrl+C to stop\n')
        
        # Start monitoring (if not disabled)
        if not args.no_monitor:
            launcher.monitor()
        else:
            # Just wait for keyboard interrupt
            try:
                while launcher.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
    except KeyboardInterrupt:
        print('\n\n⌨️  Keyboard interrupt received')
    except Exception as e:
        print(f'\n❌ Fatal error: {e}')
        launcher.logger.exception('Fatal error in main')
        return 1
    finally:
        # Cleanup
        print('\n🛑 Shutting down JARVIS...')
        
        if tray_manager:
            tray_manager.stop()
        
        launcher.shutdown()
        
        print('✅ JARVIS stopped')
        print('👋 Goodbye!\n')
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
