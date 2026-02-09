#!/usr/bin/env python3
"""
Firebase Setup Verification Script

This script verifies that Firebase is properly configured for JARVIS.
Run this after completing the Firebase setup steps.

Usage:
    python scripts/verify_firebase_setup.py
"""

import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if os.path.exists(filepath):
        print(f"✅ {description}: Found at {filepath}")
        return True
    else:
        print(f"❌ {description}: NOT FOUND at {filepath}")
        return False

def check_env_variable(env_file, var_name, description):
    """Check if an environment variable is set in .env file."""
    if not os.path.exists(env_file):
        print(f"❌ {description}: .env file not found at {env_file}")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if var_name in content and not content.split(var_name)[1].split('\n')[0].strip().endswith('_here'):
            print(f"✅ {description}: Set in {env_file}")
            return True
        else:
            print(f"❌ {description}: NOT SET or using placeholder in {env_file}")
            return False

def validate_firebase_credentials(filepath):
    """Validate Firebase credentials JSON structure."""
    try:
        with open(filepath, 'r') as f:
            creds = json.load(f)
            
        required_fields = [
            'type', 'project_id', 'private_key_id', 'private_key',
            'client_email', 'client_id', 'auth_uri', 'token_uri'
        ]
        
        missing_fields = [field for field in required_fields if field not in creds]
        
        if missing_fields:
            print(f"❌ Firebase credentials: Missing fields: {', '.join(missing_fields)}")
            return False
        
        if creds.get('type') != 'service_account':
            print(f"❌ Firebase credentials: Invalid type (should be 'service_account')")
            return False
        
        if 'YOUR_PROJECT_ID' in creds.get('project_id', ''):
            print(f"❌ Firebase credentials: Still using template values")
            return False
        
        print(f"✅ Firebase credentials: Valid structure")
        print(f"   Project ID: {creds.get('project_id')}")
        return True
        
    except json.JSONDecodeError:
        print(f"❌ Firebase credentials: Invalid JSON format")
        return False
    except Exception as e:
        print(f"❌ Firebase credentials: Error reading file: {e}")
        return False

def test_firebase_connection():
    """Test actual connection to Firebase."""
    try:
        import firebase_admin
        from firebase_admin import credentials, db
        
        creds_path = 'data/firebase-admin-credentials.json'
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv('backend/.env')
        
        database_url = os.getenv('FIREBASE_DATABASE_URL')
        
        if not database_url or 'your-project-id' in database_url:
            print(f"❌ Firebase connection: Database URL not configured")
            return False
        
        # Initialize Firebase
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        
        # Test write
        import time
        ref = db.reference('test/verification')
        ref.set({
            'status': 'connected',
            'timestamp': int(time.time() * 1000)  # Unix timestamp in milliseconds
        })
        
        # Test read
        data = ref.get()
        
        if data and data.get('status') == 'connected':
            print(f"✅ Firebase connection: Successfully connected and tested")
            print(f"   Database URL: {database_url}")
            
            # Clean up test data
            ref.delete()
            return True
        else:
            print(f"❌ Firebase connection: Could not verify read/write")
            return False
            
    except ImportError:
        print(f"⚠️  Firebase connection: firebase-admin package not installed")
        print(f"   Run: pip install firebase-admin")
        return False
    except Exception as e:
        print(f"❌ Firebase connection: {str(e)}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("JARVIS Firebase Setup Verification")
    print("=" * 60)
    print()
    
    checks_passed = 0
    checks_total = 0
    
    # Check credentials file
    checks_total += 1
    if check_file_exists('data/firebase-admin-credentials.json', 'Firebase credentials'):
        if validate_firebase_credentials('data/firebase-admin-credentials.json'):
            checks_passed += 1
    
    print()
    
    # Check .gitignore
    checks_total += 1
    if check_file_exists('.gitignore', '.gitignore file'):
        with open('.gitignore', 'r') as f:
            if 'firebase-admin-credentials.json' in f.read():
                print(f"✅ .gitignore: Firebase credentials are ignored")
                checks_passed += 1
            else:
                print(f"❌ .gitignore: Firebase credentials NOT ignored (security risk!)")
    
    print()
    
    # Check backend .env
    checks_total += 1
    if check_env_variable('backend/.env', 'FIREBASE_DATABASE_URL', 'Backend Firebase URL'):
        checks_passed += 1
    
    checks_total += 1
    if check_env_variable('backend/.env', 'FIREBASE_CREDENTIALS_PATH', 'Backend credentials path'):
        checks_passed += 1
    
    print()
    
    # Check local_client .env
    checks_total += 1
    if check_env_variable('local_client/.env', 'FIREBASE_DATABASE_URL', 'Local client Firebase URL'):
        checks_passed += 1
    
    checks_total += 1
    if check_env_variable('local_client/.env', 'FIREBASE_CREDENTIALS_PATH', 'Local client credentials path'):
        checks_passed += 1
    
    print()
    
    # Check security rules file
    checks_total += 1
    if check_file_exists('firebase-security-rules.json', 'Security rules file'):
        checks_passed += 1
    
    print()
    
    # Test Firebase connection
    checks_total += 1
    if test_firebase_connection():
        checks_passed += 1
    
    print()
    print("=" * 60)
    print(f"Verification Results: {checks_passed}/{checks_total} checks passed")
    print("=" * 60)
    
    if checks_passed == checks_total:
        print("✅ All checks passed! Firebase is properly configured.")
        print()
        print("Next steps:")
        print("1. Proceed to Task 2: Implement Firebase service module")
        print("2. Configure mobile app Firebase settings")
        return 0
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print()
        print("For help, see:")
        print("- docs/FIREBASE_SETUP_GUIDE.md (detailed guide)")
        print("- docs/FIREBASE_QUICK_START.md (quick checklist)")
        return 1

if __name__ == '__main__':
    sys.exit(main())
