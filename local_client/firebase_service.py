"""
Firebase Service for JARVIS Local Client
Handles Firebase connection, command listening, and status publishing.
"""

import firebase_admin
from firebase_admin import credentials, db
from typing import Optional, Callable, Dict, Any
import time
import uuid
import os
import threading


class FirebaseService:
    """
    Firebase service for local client.
    Manages command listening, status publishing, and presence tracking.
    """
    
    def __init__(self, credentials_path: str, database_url: Optional[str] = None):
        """
        Initialize Firebase Admin SDK for local client.
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            database_url: Firebase Realtime Database URL (optional, can be inferred from credentials)
        
        Raises:
            ValueError: If credentials file not found or invalid
            Exception: If Firebase initialization fails
        """
        if not os.path.exists(credentials_path):
            raise ValueError(f"Firebase credentials file not found: {credentials_path}")
        
        try:
            # Check if Firebase is already initialized
            try:
                firebase_admin.get_app()
                print("✅ Firebase already initialized, using existing instance")
                self.db_ref = db.reference()
            except ValueError:
                # Not initialized yet, initialize now
                cred = credentials.Certificate(credentials_path)
                
                # If database_url not provided, try multiple detection methods
                if database_url is None:
                    # Method 1: Check for firebase_config.json
                    config_path = os.path.join(os.path.dirname(credentials_path), 'firebase_config.json')
                    if os.path.exists(config_path):
                        try:
                            with open(config_path, 'r') as f:
                                import json
                                config_data = json.load(f)
                                database_url = config_data.get('database_url')
                                if database_url:
                                    print(f"📋 Using database URL from firebase_config.json")
                        except Exception as e:
                            print(f"⚠️  Could not read firebase_config.json: {e}")
                    
                    # Method 2: Try to infer from project_id (fallback)
                    if database_url is None:
                        with open(credentials_path, 'r') as f:
                            import json
                            cred_data = json.load(f)
                            project_id = cred_data.get('project_id')
                            if project_id:
                                # Try to detect region from credentials or use default
                                # Common regions: us-central1, europe-west1, asia-southeast1
                                database_url = f"https://{project_id}-default-rtdb.firebaseio.com"
                                print(f"⚠️  Using default database URL: {database_url}")
                                print(f"   If you get region errors, run: python fix_firebase_region.py")
                
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                
                self.db_ref = db.reference()
                
                print(f"✅ Firebase Admin SDK initialized")
                print(f"   Database URL: {database_url}")
            
            self.device_id = None
            self._listeners = []
            self._presence_thread = None
            self._presence_running = False
            
        except Exception as e:
            raise Exception(f"Failed to initialize Firebase: {e}")
    
    def set_device_id(self, device_id: str) -> None:
        """
        Set the device ID for this client instance.
        
        Args:
            device_id: Unique identifier for this desktop device
        """
        self.device_id = device_id
        print(f"✅ Device ID set: {device_id}")
    
    def register_device(self, device_id: str, device_type: str = "desktop", version: str = "1.0.0") -> bool:
        """
        Register this device in Firebase.
        
        Args:
            device_id: Unique identifier for the device
            device_type: Type of device ("desktop" or "mobile")
            version: Application version
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            device_ref = self.db_ref.child('devices').child(device_id)
            device_ref.set({
                'type': device_type,
                'paired': False,
                'lastSeen': int(time.time()),
                'version': version,
                'registeredAt': int(time.time())
            })
            
            print(f"✅ Device registered: {device_id} ({device_type})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to register device: {e}")
            return False
    
    def update_presence(self, device_id: Optional[str] = None) -> bool:
        """
        Update device last-seen timestamp.
        
        Args:
            device_id: Device identifier (uses self.device_id if not provided)
        
        Returns:
            True if update successful, False otherwise
        """
        if device_id is None:
            device_id = self.device_id
        
        if device_id is None:
            print("⚠️ No device ID set for presence update")
            return False
        
        try:
            device_ref = self.db_ref.child('devices').child(device_id)
            device_ref.update({
                'lastSeen': int(time.time())
            })
            return True
            
        except Exception as e:
            print(f"❌ Failed to update presence: {e}")
            return False
    
    def start_presence_tracking(self, device_id: Optional[str] = None, interval: int = 30) -> None:
        """
        Start automatic presence tracking in background thread.
        
        Args:
            device_id: Device identifier (uses self.device_id if not provided)
            interval: Update interval in seconds (default 30)
        """
        if device_id is None:
            device_id = self.device_id
        
        if device_id is None:
            print("⚠️ No device ID set for presence tracking")
            return
        
        if self._presence_running:
            print("⚠️ Presence tracking already running")
            return
        
        def presence_loop():
            """Background thread for presence updates."""
            while self._presence_running:
                self.update_presence(device_id)
                time.sleep(interval)
        
        self._presence_running = True
        self._presence_thread = threading.Thread(target=presence_loop, daemon=True)
        self._presence_thread.start()
        
        print(f"✅ Presence tracking started (interval: {interval}s)")
    
    def stop_presence_tracking(self) -> None:
        """Stop automatic presence tracking."""
        if self._presence_running:
            self._presence_running = False
            if self._presence_thread:
                self._presence_thread.join(timeout=5)
            print("✅ Presence tracking stopped")
    
    def listen_for_commands(self, device_id: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Listen for incoming commands for this device.
        
        Args:
            device_id: Device identifier to listen for
            callback: Function to call when command received
        """
        def on_command_added(event):
            """Handle new command event."""
            if event.data is None:
                return
            
            command_data = event.data
            message_id = event.path.split('/')[-1]
            
            # Check if already processed
            if command_data.get('processed', False):
                return
            
            print(f"📥 Command received: {message_id}")
            
            # Mark as processed
            try:
                command_ref = self.db_ref.child('messages').child(device_id).child('commands').child(message_id)
                command_ref.update({'processed': True})
            except Exception as e:
                print(f"⚠️ Failed to mark command as processed: {e}")
            
            # Call callback with command data
            callback(command_data)
        
        # Listen for new commands
        commands_ref = self.db_ref.child('messages').child(device_id).child('commands')
        listener = commands_ref.listen(on_command_added)
        self._listeners.append(listener)
        
        print(f"👂 Listening for commands on device: {device_id}")
    
    def send_status(self, device_id: str, status: Dict[str, Any]) -> Optional[str]:
        """
        Send a status update to Firebase.
        
        Args:
            device_id: Target device identifier (typically mobile device)
            status: Status data dictionary
        
        Returns:
            Message ID if successful, None otherwise
        """
        try:
            message_id = str(uuid.uuid4())
            status_ref = self.db_ref.child('messages').child(device_id).child('status').child(message_id)
            
            status_data = {
                'type': 'status',
                'timestamp': int(time.time()),
                **status
            }
            
            status_ref.set(status_data)
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to send status: {e}")
            return None
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information from Firebase.
        
        Args:
            device_id: Device identifier
        
        Returns:
            Device info dictionary or None if not found
        """
        try:
            device_ref = self.db_ref.child('devices').child(device_id)
            device_data = device_ref.get()
            return device_data
            
        except Exception as e:
            print(f"❌ Failed to get device info: {e}")
            return None
    
    def is_device_paired(self, device_id: str) -> bool:
        """
        Check if a device is paired.
        
        Args:
            device_id: Device identifier
        
        Returns:
            True if paired, False otherwise
        """
        device_info = self.get_device_info(device_id)
        if device_info:
            return device_info.get('paired', False)
        return False
    
    def cleanup_old_messages(self, device_id: str, max_age_seconds: int = 3600) -> int:
        """
        Clean up old messages from Firebase.
        
        Args:
            device_id: Device identifier
            max_age_seconds: Maximum age of messages to keep (default 1 hour)
        
        Returns:
            Number of messages deleted
        """
        try:
            deleted_count = 0
            current_time = int(time.time())
            cutoff_time = current_time - max_age_seconds
            
            # Clean up commands
            commands_ref = self.db_ref.child('messages').child(device_id).child('commands')
            commands = commands_ref.get() or {}
            
            for message_id, message_data in commands.items():
                if message_data.get('timestamp', 0) < cutoff_time:
                    commands_ref.child(message_id).delete()
                    deleted_count += 1
            
            # Clean up status updates
            status_ref = self.db_ref.child('messages').child(device_id).child('status')
            statuses = status_ref.get() or {}
            
            for message_id, message_data in statuses.items():
                if message_data.get('timestamp', 0) < cutoff_time:
                    status_ref.child(message_id).delete()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} old messages")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup messages: {e}")
            return 0
    
    def close(self) -> None:
        """
        Close all Firebase listeners and cleanup.
        """
        # Stop presence tracking
        self.stop_presence_tracking()
        
        # Close all listeners
        for listener in self._listeners:
            try:
                listener.close()
            except Exception as e:
                print(f"⚠️ Error closing listener: {e}")
        
        self._listeners.clear()
        print("✅ Firebase service closed")
