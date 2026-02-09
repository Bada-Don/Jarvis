#!/usr/bin/env python3
"""
Asset packaging script for JARVIS.
Copies FastSAM weights, icons, configuration templates, and Firebase credentials template.
"""

import os
import sys
import shutil
from pathlib import Path


def create_assets_directory():
    """Create the assets directory structure."""
    assets_dir = Path('dist/assets')
    
    subdirs = [
        'weights',
        'icons',
        'config',
        'audio',
    ]
    
    print("Creating assets directory structure...")
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    for subdir in subdirs:
        subdir_path = assets_dir / subdir
        subdir_path.mkdir(exist_ok=True)
        print(f"  ✓ Created {subdir_path}")
    
    return assets_dir


def copy_fastsam_weights(assets_dir):
    """Copy FastSAM model weights to bundle."""
    print("\nCopying FastSAM weights...")
    
    weights_source = Path('backend/weights/FastSAM-s.pt')
    weights_dest = assets_dir / 'weights' / 'FastSAM-s.pt'
    
    if weights_source.exists():
        shutil.copy2(weights_source, weights_dest)
        size_mb = weights_dest.stat().st_size / (1024 * 1024)
        print(f"  ✓ Copied FastSAM-s.pt ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ⚠ Warning: FastSAM weights not found at {weights_source}")
        print(f"    The application will need to download weights on first run")
        return False


def copy_application_icons(assets_dir):
    """Copy application icons to bundle."""
    print("\nCopying application icons...")
    
    # Look for icon files in various locations
    icon_sources = [
        Path('ChatInterface/assets/Logo/Jarvis.png'),
        Path('ChatInterface/assets/Logo/Jarvis.svg'),
        Path('ChatInterface/assets/Jarvis.svg'),
    ]
    
    icons_copied = 0
    for icon_source in icon_sources:
        if icon_source.exists():
            icon_dest = assets_dir / 'icons' / icon_source.name
            shutil.copy2(icon_source, icon_dest)
            print(f"  ✓ Copied {icon_source.name}")
            icons_copied += 1
    
    if icons_copied == 0:
        print(f"  ⚠ Warning: No application icons found")
        print(f"    Creating placeholder icon info...")
        placeholder = assets_dir / 'icons' / 'README.txt'
        placeholder.write_text("Place application icons here (PNG, ICO, SVG formats)")
    
    return icons_copied > 0


def copy_audio_assets(assets_dir):
    """Copy audio feedback files to bundle."""
    print("\nCopying audio assets...")
    
    audio_sources = [
        Path('local_client/assets/Complete.mp3'),
        Path('local_client/assets/Start.mp3'),
    ]
    
    audio_copied = 0
    for audio_source in audio_sources:
        if audio_source.exists():
            audio_dest = assets_dir / 'audio' / audio_source.name
            shutil.copy2(audio_source, audio_dest)
            print(f"  ✓ Copied {audio_source.name}")
            audio_copied += 1
    
    if audio_copied == 0:
        print(f"  ⚠ Warning: No audio assets found")
    
    return audio_copied > 0


def create_config_templates(assets_dir):
    """Create configuration templates."""
    print("\nCreating configuration templates...")
    
    config_dir = assets_dir / 'config'
    
    # Copy existing example configs
    config_sources = [
        ('backend/.env.example', 'backend.env.example'),
        ('local_client/config.json.example', 'config.json.example'),
        ('local_client/flexisign_config.json.example', 'flexisign_config.json.example'),
        ('data/firebase_config.json.example', 'firebase_config.json.example'),
    ]
    
    templates_created = 0
    for source_path, dest_name in config_sources:
        source = Path(source_path)
        if source.exists():
            dest = config_dir / dest_name
            shutil.copy2(source, dest)
            print(f"  ✓ Copied {dest_name}")
            templates_created += 1
        else:
            print(f"  ⚠ Warning: {source_path} not found")
    
    # Create Firebase credentials template
    firebase_template = config_dir / 'firebase-admin-credentials.json.example'
    firebase_template_content = """{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project-id.iam.gserviceaccount.com"
}
"""
    firebase_template.write_text(firebase_template_content)
    print(f"  ✓ Created firebase-admin-credentials.json.example")
    templates_created += 1
    
    # Create README for configuration
    config_readme = config_dir / 'README.txt'
    config_readme_content = """JARVIS Configuration Templates

This directory contains example configuration files.
Copy these files and remove the .example extension, then fill in your values.

Required Files:
- firebase-admin-credentials.json: Firebase service account credentials
- firebase_config.json: Firebase web app configuration

Optional Files:
- backend.env: Backend server environment variables
- config.json: Local client configuration
- flexisign_config.json: FlexiSign automation configuration

For detailed setup instructions, see the main README.txt in the application root.
"""
    config_readme.write_text(config_readme_content)
    print(f"  ✓ Created configuration README")
    
    return templates_created > 0


def create_data_directory():
    """Create the data directory structure."""
    print("\nCreating data directory structure...")
    
    data_dir = Path('dist/data')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    subdirs = [
        'logs',
        'config_backups',
    ]
    
    for subdir in subdirs:
        subdir_path = data_dir / subdir
        subdir_path.mkdir(exist_ok=True)
        print(f"  ✓ Created {subdir_path}")
    
    # Create .gitkeep files to preserve empty directories
    for subdir in subdirs:
        gitkeep = data_dir / subdir / '.gitkeep'
        gitkeep.touch()
    
    # Create data directory README
    data_readme = data_dir / 'README.txt'
    data_readme_content = """JARVIS Data Directory

This directory stores application data and user configurations.

Subdirectories:
- logs/: Application log files
- config_backups/: Automatic configuration backups

User configuration files will be created here on first run:
- config.py: Main application configuration
- firebase_config.json: Firebase configuration
- firebase-admin-credentials.json: Firebase service account credentials
- device_config.json: Device pairing information

Do not delete this directory while the application is running.
"""
    data_readme.write_text(data_readme_content)
    print(f"  ✓ Created data directory README")
    
    return data_dir


def verify_assets():
    """Verify that assets were packaged correctly."""
    print("\nVerifying packaged assets...")
    
    assets_dir = Path('dist/assets')
    data_dir = Path('dist/data')
    
    checks = [
        (assets_dir / 'weights', 'Weights directory'),
        (assets_dir / 'icons', 'Icons directory'),
        (assets_dir / 'config', 'Config templates directory'),
        (assets_dir / 'audio', 'Audio assets directory'),
        (data_dir / 'logs', 'Logs directory'),
        (data_dir / 'config_backups', 'Config backups directory'),
    ]
    
    all_good = True
    for path, description in checks:
        if path.exists():
            if path.is_dir():
                file_count = len(list(path.iterdir()))
                print(f"  ✓ {description} ({file_count} items)")
            else:
                print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} missing")
            all_good = False
    
    return all_good


def calculate_total_size():
    """Calculate total size of packaged assets."""
    assets_dir = Path('dist/assets')
    data_dir = Path('dist/data')
    
    total_size = 0
    file_count = 0
    
    for directory in [assets_dir, data_dir]:
        if directory.exists():
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
    
    size_mb = total_size / (1024 * 1024)
    print(f"\nTotal assets: {file_count} files, {size_mb:.2f} MB")


def main():
    """Main asset packaging process."""
    print("JARVIS Asset Packaging Script")
    print("=" * 60)
    
    # Create directory structure
    assets_dir = create_assets_directory()
    data_dir = create_data_directory()
    
    # Copy assets
    copy_fastsam_weights(assets_dir)
    copy_application_icons(assets_dir)
    copy_audio_assets(assets_dir)
    create_config_templates(assets_dir)
    
    # Verify and report
    if verify_assets():
        calculate_total_size()
        print("\n" + "=" * 60)
        print("✓ Assets packaged successfully!")
        print("=" * 60)
        print("\nAssets located in:")
        print("  - dist/assets/")
        print("  - dist/data/")
        return 0
    else:
        print("\n✗ Asset packaging verification failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
