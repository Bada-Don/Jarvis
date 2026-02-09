"""
Pairing Manager for JARVIS Desktop
Handles device pairing, token generation, QR code generation, and pairing status.
"""

import uuid
import time
import json
import os
import qrcode
from io import BytesIO
from typing import Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path


class PairingManager:
    """
    Manages device pairing for desktop application.
    Handles device ID generation, pairing token creation, QR code generation, and pairing status.
    """
    
    def __init__(self, firebase_service, config_dir: Optional[str] = None):
        """
        Initialize PairingManager.
        
        Args:
            firebase_service: FirebaseService instance for database operations
            config_dir: Directory to store device configuration (default: ./data)
        
        Raises:
            ValueError: If firebase_service is None
        """
        if firebase_service is None:
            raise ValueError("firebase_service cannot be None")
        
        self.firebase = firebase_service
        
        # Set up config directory
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.device_config_path = self.config_dir / 'device_config.json'
        
        # Load or create device ID
        self.device_id = self._get_or_create_device_id()
        
        # Set device ID in Firebase service
        self.firebase.set_device_id(self.device_id)
        
        # Current pairing token info
        self.current_token = None
        self.token_expires_at = None
        
        print(f"✅ PairingManager initialized")
        print(f"   Device ID: {self.device_id}")
        print(f"   Config dir: {self.config_dir}")
    
    def _get_or_create_device_id(self) -> str:
        """
        Load existing device ID or generate a new one.
        
        Returns:
            Device ID string
        """
        # Try to load existing device config
        if self.device_config_path.exists():
            try:
                with open(self.device_config_path, 'r') as f:
                    config = json.load(f)
                    device_id = config.get('device_id')
                    if device_id:
                        print(f"📱 Loaded existing device ID: {device_id}")
                        return device_id
            except Exception as e:
                print(f"⚠️ Failed to load device config: {e}")
        
        # Generate new device ID
        device_id = f"desktop_{uuid.uuid4().hex[:16]}"
        
        # Save device config
        self._save_device_config(device_id)
        
        print(f"🆕 Generated new device ID: {device_id}")
        return device_id
    
    def _save_device_config(self, device_id: str, paired_device_id: Optional[str] = None) -> None:
        """
        Save device configuration to disk.
        
        Args:
            device_id: Desktop device ID
            paired_device_id: Mobile device ID (if paired)
        """
        try:
            config = {
                'device_id': device_id,
                'paired_device_id': paired_device_id,
                'last_updated': int(time.time())
            }
            
            with open(self.device_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"💾 Device config saved")
            
        except Exception as e:
            print(f"❌ Failed to save device config: {e}")
    
    def generate_pairing_token(self, ttl: int = 300) -> str:
        """
        Generate a time-limited pairing token.
        
        Args:
            ttl: Time-to-live in seconds (default 300 = 5 minutes)
        
        Returns:
            Pairing token string
        
        Raises:
            Exception: If token generation fails
        """
        try:
            # Generate unique token
            token = f"pair_{uuid.uuid4().hex[:12]}"
            
            # Calculate expiration time
            expires_at = int(time.time()) + ttl
            
            # Store token in Firebase
            pairing_ref = self.firebase.db_ref.child('pairing').child(token)
            pairing_ref.set({
                'desktopId': self.device_id,
                'expiresAt': expires_at,
                'used': False,
                'createdAt': int(time.time())
            })
            
            # Store current token info
            self.current_token = token
            self.token_expires_at = expires_at
            
            print(f"🔑 Pairing token generated: {token}")
            print(f"   Expires at: {datetime.fromtimestamp(expires_at).strftime('%Y-%m-%d %H:%M:%S')}")
            
            return token
            
        except Exception as e:
            raise Exception(f"Failed to generate pairing token: {e}")
    
    def generate_pairing_qr(self, ttl: int = 300) -> Tuple[str, bytes]:
        """
        Generate pairing token and QR code image.
        
        Args:
            ttl: Time-to-live in seconds (default 300 = 5 minutes)
        
        Returns:
            Tuple of (token string, QR code image bytes)
        
        Raises:
            Exception: If QR code generation fails
        """
        # Generate token
        token = self.generate_pairing_token(ttl)
        
        # Create QR code
        qr_image = self._create_qr_code(token)
        
        return token, qr_image
    
    def _create_qr_code(self, data: str) -> bytes:
        """
        Create QR code image from data.
        
        Args:
            data: Data to encode in QR code
        
        Returns:
            QR code image as PNG bytes
        
        Raises:
            Exception: If QR code creation fails
        """
        try:
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_bytes = buffer.getvalue()
            
            print(f"📷 QR code generated ({len(qr_bytes)} bytes)")
            
            return qr_bytes
            
        except Exception as e:
            raise Exception(f"Failed to create QR code: {e}")
    
    def check_pairing_status(self, token: Optional[str] = None) -> bool:
        """
        Check if pairing has been completed for a token.
        
        Args:
            token: Pairing token to check (uses current_token if not provided)
        
        Returns:
            True if pairing completed, False otherwise
        """
        if token is None:
            token = self.current_token
        
        if token is None:
            print("⚠️ No token to check")
            return False
        
        try:
            # Check token in Firebase
            pairing_ref = self.firebase.db_ref.child('pairing').child(token)
            pairing_data = pairing_ref.get()
            
            if pairing_data is None:
                print(f"⚠️ Token not found: {token}")
                return False
            
            # Check if token was used
            if pairing_data.get('used', False):
                # Get mobile device ID
                mobile_device_id = pairing_data.get('mobileId')
                
                if mobile_device_id:
                    # Update device config
                    self._save_device_config(self.device_id, mobile_device_id)
                    
                    # Update Firebase device status
                    device_ref = self.firebase.db_ref.child('devices').child(self.device_id)
                    device_ref.update({
                        'paired': True,
                        'pairedWith': mobile_device_id,
                        'pairedAt': int(time.time())
                    })
                    
                    print(f"✅ Pairing completed with device: {mobile_device_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to check pairing status: {e}")
            return False
    
    def is_paired(self) -> bool:
        """
        Check if this device is currently paired with a mobile device.
        
        Returns:
            True if paired, False otherwise
        """
        try:
            # Check Firebase device status
            device_info = self.firebase.get_device_info(self.device_id)
            
            if device_info:
                return device_info.get('paired', False)
            
            return False
            
        except Exception as e:
            print(f"❌ Failed to check paired status: {e}")
            return False
    
    def get_paired_device_id(self) -> Optional[str]:
        """
        Get the ID of the paired mobile device.
        
        Returns:
            Mobile device ID if paired, None otherwise
        """
        try:
            # Check Firebase device status
            device_info = self.firebase.get_device_info(self.device_id)
            
            if device_info and device_info.get('paired', False):
                return device_info.get('pairedWith')
            
            return None
            
        except Exception as e:
            print(f"❌ Failed to get paired device ID: {e}")
            return None
    
    def unpair(self) -> bool:
        """
        Remove pairing and require re-pairing.
        
        Returns:
            True if unpair successful, False otherwise
        """
        try:
            # Update Firebase device status
            device_ref = self.firebase.db_ref.child('devices').child(self.device_id)
            device_ref.update({
                'paired': False,
                'pairedWith': None,
                'unpairedAt': int(time.time())
            })
            
            # Update local config
            self._save_device_config(self.device_id, None)
            
            print(f"🔓 Device unpaired")
            return True
            
        except Exception as e:
            print(f"❌ Failed to unpair device: {e}")
            return False
    
    def is_token_expired(self, token: Optional[str] = None) -> bool:
        """
        Check if a pairing token has expired.
        
        Args:
            token: Pairing token to check (uses current_token if not provided)
        
        Returns:
            True if expired, False otherwise
        """
        if token is None:
            token = self.current_token
        
        if token is None:
            return True
        
        try:
            # Check token in Firebase
            pairing_ref = self.firebase.db_ref.child('pairing').child(token)
            pairing_data = pairing_ref.get()
            
            if pairing_data is None:
                return True
            
            expires_at = pairing_data.get('expiresAt', 0)
            current_time = int(time.time())
            
            return current_time > expires_at
            
        except Exception as e:
            print(f"❌ Failed to check token expiration: {e}")
            return True
    
    def get_token_time_remaining(self, token: Optional[str] = None) -> int:
        """
        Get remaining time for a pairing token in seconds.
        
        Args:
            token: Pairing token to check (uses current_token if not provided)
        
        Returns:
            Remaining seconds (0 if expired or invalid)
        """
        if token is None:
            token = self.current_token
        
        if token is None:
            return 0
        
        try:
            # Check token in Firebase
            pairing_ref = self.firebase.db_ref.child('pairing').child(token)
            pairing_data = pairing_ref.get()
            
            if pairing_data is None:
                return 0
            
            expires_at = pairing_data.get('expiresAt', 0)
            current_time = int(time.time())
            
            remaining = expires_at - current_time
            return max(0, remaining)
            
        except Exception as e:
            print(f"❌ Failed to get token time remaining: {e}")
            return 0
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired pairing tokens from Firebase.
        
        Returns:
            Number of tokens deleted
        """
        try:
            deleted_count = 0
            current_time = int(time.time())
            
            # Get all pairing tokens
            pairing_ref = self.firebase.db_ref.child('pairing')
            tokens = pairing_ref.get() or {}
            
            for token, token_data in tokens.items():
                expires_at = token_data.get('expiresAt', 0)
                
                # Delete if expired
                if current_time > expires_at:
                    pairing_ref.child(token).delete()
                    deleted_count += 1
            
            if deleted_count > 0:
                print(f"🧹 Cleaned up {deleted_count} expired tokens")
            
            return deleted_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup expired tokens: {e}")
            return 0
