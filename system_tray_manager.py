"""
JARVIS System Tray Manager
Provides system tray icon and menu for JARVIS application control.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Callable
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item


class SystemTrayManager:
    """
    Manages the system tray icon and menu for JARVIS.
    
    Responsibilities:
    - Display system tray icon
    - Provide menu for application control
    - Handle minimize to tray
    - Handle restore from tray
    """
    
    def __init__(
        self,
        on_show_settings: Optional[Callable] = None,
        on_restart: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
        get_status: Optional[Callable] = None
    ):
        """
        Initialize the System Tray Manager.
        
        Args:
            on_show_settings: Callback for "Show Settings" action
            on_restart: Callback for "Restart" action
            on_quit: Callback for "Quit" action
            get_status: Callback to get component status
        """
        self.on_show_settings = on_show_settings
        self.on_restart = on_restart
        self.on_quit = on_quit
        self.get_status = get_status
        
        self.icon: Optional[pystray.Icon] = None
        self.logger = logging.getLogger('SystemTrayManager')
        
        # Create tray icon
        self._create_icon()
    
    def _create_icon_image(self) -> Image.Image:
        """
        Create the system tray icon image.
        
        Returns:
            PIL Image for the tray icon
        """
        # Try to load custom icon
        icon_path = Path('assets/icons/jarvis_icon.png')
        if icon_path.exists():
            try:
                return Image.open(icon_path)
            except Exception as e:
                self.logger.warning(f'Failed to load custom icon: {e}')
        
        # Create a simple default icon (circle with "J")
        size = 64
        image = Image.new('RGB', (size, size), color='#14B8A6')  # Teal color
        draw = ImageDraw.Draw(image)
        
        # Draw circle
        draw.ellipse([4, 4, size-4, size-4], fill='#14B8A6', outline='#0D9488', width=2)
        
        # Draw "J" letter (simplified)
        draw.text(
            (size//2 - 8, size//2 - 12),
            'J',
            fill='white',
            font=None  # Use default font
        )
        
        return image
    
    def _create_icon(self) -> None:
        """Create the system tray icon with menu."""
        icon_image = self._create_icon_image()
        
        # Create menu
        menu = pystray.Menu(
            item('JARVIS', self._on_title_click, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Show Settings', self._on_show_settings),
            pystray.Menu.SEPARATOR,
            item('Status', pystray.Menu(
                item('Backend', self._get_backend_status, enabled=False),
                item('Local Client', self._get_client_status, enabled=False),
                item('Settings UI', self._get_ui_status, enabled=False)
            )),
            pystray.Menu.SEPARATOR,
            item('Restart All', self._on_restart),
            item('View Logs', self._on_view_logs),
            pystray.Menu.SEPARATOR,
            item('Quit', self._on_quit)
        )
        
        self.icon = pystray.Icon(
            'JARVIS',
            icon_image,
            'JARVIS - AI Desktop Assistant',
            menu
        )
    
    def _on_title_click(self, icon, item):
        """Handle title click (disabled, just for display)."""
        pass
    
    def _on_show_settings(self, icon, item):
        """Handle "Show Settings" menu item."""
        self.logger.info('Show Settings clicked')
        if self.on_show_settings:
            self.on_show_settings()
    
    def _on_restart(self, icon, item):
        """Handle "Restart" menu item."""
        self.logger.info('Restart clicked')
        if self.on_restart:
            self.on_restart()
    
    def _on_view_logs(self, icon, item):
        """Handle "View Logs" menu item."""
        self.logger.info('View Logs clicked')
        
        # Open logs directory
        log_dir = Path('data/logs')
        if log_dir.exists():
            import os
            import subprocess
            
            try:
                if sys.platform == 'win32':
                    os.startfile(log_dir)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', log_dir])
                else:
                    subprocess.run(['xdg-open', log_dir])
            except Exception as e:
                self.logger.error(f'Failed to open logs directory: {e}')
    
    def _on_quit(self, icon, item):
        """Handle "Quit" menu item."""
        self.logger.info('Quit clicked')
        if self.on_quit:
            self.on_quit()
        self.stop()
    
    def _get_backend_status(self, item) -> str:
        """Get backend status for menu display."""
        if self.get_status:
            status = self.get_status()
            backend = status.get('backend', {})
            if backend.get('status') == 'running':
                return f"Backend: ✓ Running (PID: {backend.get('pid')})"
            else:
                return "Backend: ✗ Stopped"
        return "Backend: ? Unknown"
    
    def _get_client_status(self, item) -> str:
        """Get local client status for menu display."""
        if self.get_status:
            status = self.get_status()
            client = status.get('local_client', {})
            if client.get('status') == 'running':
                return f"Client: ✓ Running (PID: {client.get('pid')})"
            else:
                return "Client: ✗ Stopped"
        return "Client: ? Unknown"
    
    def _get_ui_status(self, item) -> str:
        """Get settings UI status for menu display."""
        if self.get_status:
            status = self.get_status()
            ui = status.get('settings_ui', {})
            if ui.get('status') == 'running':
                return f"UI: ✓ Running (PID: {ui.get('pid')})"
            else:
                return "UI: ✗ Stopped"
        return "UI: ? Unknown"
    
    def run(self) -> None:
        """
        Run the system tray icon.
        This method blocks until the icon is stopped.
        """
        if self.icon:
            self.logger.info('Starting system tray icon...')
            self.icon.run()
    
    def stop(self) -> None:
        """Stop the system tray icon."""
        if self.icon:
            self.logger.info('Stopping system tray icon...')
            self.icon.stop()
    
    def update_icon(self, status: str = 'normal') -> None:
        """
        Update the tray icon based on status.
        
        Args:
            status: Status indicator ('normal', 'warning', 'error')
        """
        if not self.icon:
            return
        
        # Create new icon with status indicator
        size = 64
        image = Image.new('RGB', (size, size), color='#14B8A6')
        draw = ImageDraw.Draw(image)
        
        # Change color based on status
        if status == 'warning':
            color = '#F59E0B'  # Amber
        elif status == 'error':
            color = '#EF4444'  # Red
        else:
            color = '#14B8A6'  # Teal
        
        # Draw circle
        draw.ellipse([4, 4, size-4, size-4], fill=color, outline='#0D9488', width=2)
        
        # Draw "J" letter
        draw.text(
            (size//2 - 8, size//2 - 12),
            'J',
            fill='white',
            font=None
        )
        
        # Update icon
        self.icon.icon = image
    
    def show_notification(self, title: str, message: str) -> None:
        """
        Show a system notification.
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                self.logger.error(f'Failed to show notification: {e}')
    
    def minimize_to_tray(self) -> None:
        """
        Minimize the application to system tray.
        This hides the main window but keeps the application running.
        """
        self.logger.info('Minimizing to tray...')
        # The actual window hiding would be handled by the Settings UI
        # This is just a placeholder for the tray manager's role
        self.show_notification('JARVIS', 'Minimized to system tray')
    
    def restore_from_tray(self) -> None:
        """
        Restore the application from system tray.
        This shows the main window again.
        """
        self.logger.info('Restoring from tray...')
        if self.on_show_settings:
            self.on_show_settings()
