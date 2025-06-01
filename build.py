#!/usr/bin/env python3
"""
Build script for PyQt Auto-Update Demo
This script handles building the application with PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    directories_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            print(f"Cleaning {directory}...")
            shutil.rmtree(directory)
    
    # Clean .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}")
        spec_file.unlink()

def create_pyinstaller_spec():
    """Create a custom PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PyQtAutoUpdateDemo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # Add icon='app.ico' if you have an icon file
)
'''
    
    with open('app.spec', 'w') as f:
        f.write(spec_content)
    
    print("Created app.spec file")

def build_application():
    """Build the application using PyInstaller"""
    print("Building application with PyInstaller...")
    
    # Method 1: Using spec file (recommended for complex apps)
    create_pyinstaller_spec()
    result = subprocess.run([
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        'app.spec'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Build successful!")
        print(f"Executable created in: {os.path.abspath('dist')}")
        
        # List created files
        dist_path = Path('dist')
        if dist_path.exists():
            print("\nCreated files:")
            for item in dist_path.iterdir():
                print(f"  {item}")
    else:
        print("❌ Build failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    
    return True

def build_simple():
    """Alternative simple build method"""
    print("Building with simple PyInstaller command...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--windowed',  # Remove this for console app
        '--name', 'PyQtAutoUpdateDemo',
        '--hidden-import', 'PyQt5.QtCore',
        '--hidden-import', 'PyQt5.QtGui',
        '--hidden-import', 'PyQt5.QtWidgets',
        '--hidden-import', 'requests',
        'main.py'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Simple build successful!")
        return True
    else:
        print("❌ Simple build failed!")
        print("STDERR:", result.stderr)
        return False

def main():
    print("PyQt Auto-Update Demo - Build Script")
    print("=" * 40)
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ main.py not found! Please ensure the main application file exists.")
        return
    
    # Clean previous builds
    clean_build()
    
    # Try to build
    build_method = input("Choose build method:\n1. Spec file (recommended)\n2. Simple command\nEnter choice (1/2): ").strip()
    
    success = False
    if build_method == '2':
        success = build_simple()
    else:
        success = build_application()
    
    if success:
        print("\n🎉 Build completed successfully!")
        print("\nNext steps:")
        print("1. Test the executable in the 'dist' folder")
        print("2. Create releases on GitHub with version tags")
        print("3. Upload the executable as a release asset")
        print("4. Update the UPDATE_SERVER URL in main.py")
    else:
        print("\n💥 Build failed. Check the error messages above.")

if __name__ == '__main__':
    main()