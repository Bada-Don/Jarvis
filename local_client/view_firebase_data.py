"""
Firebase Data Viewer
View and inspect data in Firebase Realtime Database.
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from local_client.firebase_service import FirebaseService


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def format_timestamp(timestamp):
    """Format Unix timestamp to readable date."""
    if timestamp:
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp)
    return "N/A"


def print_json(data, indent=2):
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


def view_all_data(firebase):
    """View all data in Firebase."""
    print_header("All Firebase Data")
    
    try:
        all_data = firebase.db_ref.get()
        if all_data:
            print_json(all_data)
        else:
            print("   (No data in database)")
    except Exception as e:
        print(f"❌ Error: {e}")


def view_devices(firebase):
    """View all devices."""
    print_header("Devices")
    
    try:
        devices_ref = firebase.db_ref.child('devices')
        devices = devices_ref.get()
        
        if not devices:
            print("   (No devices registered)")
            return
        
        for device_id, device_data in devices.items():
            print(f"\n📱 Device: {device_id}")
            print(f"   Type: {device_data.get('type', 'unknown')}")
            print(f"   Paired: {device_data.get('paired', False)}")
            print(f"   Version: {device_data.get('version', 'unknown')}")
            print(f"   Last Seen: {format_timestamp(device_data.get('lastSeen'))}")
            
            if device_data.get('paired'):
                print(f"   Paired With: {device_data.get('pairedWith', 'unknown')}")
                print(f"   Paired At: {format_timestamp(device_data.get('pairedAt'))}")
            
            print(f"   Registered: {format_timestamp(device_data.get('registeredAt'))}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def view_pairing_tokens(firebase):
    """View all pairing tokens."""
    print_header("Pairing Tokens")
    
    try:
        pairing_ref = firebase.db_ref.child('pairing')
        tokens = pairing_ref.get()
        
        if not tokens:
            print("   (No pairing tokens)")
            return
        
        current_time = int(datetime.now().timestamp())
        
        for token, token_data in tokens.items():
            expires_at = token_data.get('expiresAt', 0)
            is_expired = current_time > expires_at
            is_used = token_data.get('used', False)
            
            status = "🔴 EXPIRED" if is_expired else "🟢 ACTIVE"
            if is_used:
                status = "✅ USED"
            
            print(f"\n🔑 Token: {token}")
            print(f"   Status: {status}")
            print(f"   Desktop ID: {token_data.get('desktopId', 'unknown')}")
            print(f"   Created: {format_timestamp(token_data.get('createdAt'))}")
            print(f"   Expires: {format_timestamp(expires_at)}")
            
            if is_used:
                print(f"   Mobile ID: {token_data.get('mobileId', 'unknown')}")
                print(f"   Used At: {format_timestamp(token_data.get('usedAt'))}")
            
            if not is_expired and not is_used:
                time_remaining = expires_at - current_time
                print(f"   Time Remaining: {time_remaining} seconds")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def view_messages(firebase):
    """View all messages."""
    print_header("Messages")
    
    try:
        messages_ref = firebase.db_ref.child('messages')
        messages = messages_ref.get()
        
        if not messages:
            print("   (No messages)")
            return
        
        for device_id, device_messages in messages.items():
            print(f"\n📨 Device: {device_id}")
            
            # Commands
            commands = device_messages.get('commands', {})
            if commands:
                print(f"\n   Commands ({len(commands)}):")
                for msg_id, msg_data in list(commands.items())[:5]:  # Show first 5
                    print(f"      • {msg_id[:8]}... - {format_timestamp(msg_data.get('timestamp'))}")
                    print(f"        Processed: {msg_data.get('processed', False)}")
                if len(commands) > 5:
                    print(f"      ... and {len(commands) - 5} more")
            
            # Status
            statuses = device_messages.get('status', {})
            if statuses:
                print(f"\n   Status Updates ({len(statuses)}):")
                for msg_id, msg_data in list(statuses.items())[:5]:  # Show first 5
                    print(f"      • {msg_id[:8]}... - {format_timestamp(msg_data.get('timestamp'))}")
                    print(f"        Message: {msg_data.get('message', 'N/A')}")
                if len(statuses) > 5:
                    print(f"      ... and {len(statuses) - 5} more")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def view_specific_device(firebase, device_id):
    """View specific device details."""
    print_header(f"Device Details: {device_id}")
    
    try:
        device_ref = firebase.db_ref.child('devices').child(device_id)
        device_data = device_ref.get()
        
        if not device_data:
            print(f"   ❌ Device not found: {device_id}")
            return
        
        print_json(device_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def interactive_viewer(firebase):
    """Interactive data viewer."""
    while True:
        print("\n" + "-" * 70)
        print("Firebase Data Viewer")
        print("-" * 70)
        print("1. View all data")
        print("2. View devices")
        print("3. View pairing tokens")
        print("4. View messages")
        print("5. View specific device")
        print("6. Refresh")
        print("7. Exit")
        print("-" * 70)
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == '1':
            view_all_data(firebase)
        elif choice == '2':
            view_devices(firebase)
        elif choice == '3':
            view_pairing_tokens(firebase)
        elif choice == '4':
            view_messages(firebase)
        elif choice == '5':
            device_id = input("Enter device ID: ").strip()
            view_specific_device(firebase, device_id)
        elif choice == '6':
            print("\n🔄 Refreshing...")
            continue
        elif choice == '7':
            print("\nExiting...")
            break
        else:
            print("\n⚠️  Invalid choice")
        
        input("\nPress Enter to continue...")


def main():
    """Main function."""
    print_header("Firebase Data Viewer")
    
    # Check for Firebase credentials
    credentials_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'firebase-admin-credentials.json')
    
    if not os.path.exists(credentials_path):
        print("\n❌ Firebase credentials not found!")
        print(f"   Expected location: {credentials_path}")
        return
    
    try:
        # Initialize Firebase
        firebase = FirebaseService(credentials_path)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'devices':
                view_devices(firebase)
            elif command == 'tokens':
                view_pairing_tokens(firebase)
            elif command == 'messages':
                view_messages(firebase)
            elif command == 'all':
                view_all_data(firebase)
            elif command == 'device' and len(sys.argv) > 2:
                view_specific_device(firebase, sys.argv[2])
            else:
                print(f"\nUnknown command: {command}")
                print("\nAvailable commands:")
                print("  python view_firebase_data.py devices    # View all devices")
                print("  python view_firebase_data.py tokens     # View pairing tokens")
                print("  python view_firebase_data.py messages   # View messages")
                print("  python view_firebase_data.py all        # View all data")
                print("  python view_firebase_data.py device <id> # View specific device")
                print("  python view_firebase_data.py            # Interactive mode")
        else:
            # Interactive mode
            interactive_viewer(firebase)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
