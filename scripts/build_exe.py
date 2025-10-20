"""
Build standalone executable using PyInstaller
"""
import PyInstaller.__main__
import sys
from pathlib import Path
import shutil

def build_executable():
    """Build Windows/Mac executable"""
    
    print("=" * 60)
    print("Building Forenstiq Evidence Analyzer Executable")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # PyInstaller arguments
    args = [
        str(project_root / 'src' / 'main.py'),  # Entry point
        '--name=ForenstiqEvidenceAnalyzer',
        '--windowed',  # No console window
        '--onefile',  # Single executable
        '--clean',  # Clean cache
        
        # Icon (if you have one)
        # '--icon=resources/icon.ico',
        
        # Add data files
        f'--add-data={project_root}/config:config',
        f'--add-data={project_root}/src/database/schema.sql:src/database',
        
        # Hidden imports (packages not auto-detected)
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=pkg_resources.py2_warn',
        
        # Exclude unnecessary packages to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        
        # Output directory
        f'--distpath={project_root}/dist',
        f'--workpath={project_root}/build',
        f'--specpath={project_root}',
    ]
    
    print("\nPyInstaller arguments:")
    for arg in args:
        print(f"  {arg}")
    
    print("\n" + "=" * 60)
    print("Building... This may take 5-10 minutes")
    print("=" * 60 + "\n")
    
    try:
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        print("\n" + "=" * 60)
        print("✓ Build successful!")
        print("=" * 60)
        print(f"\nExecutable location: {project_root}/dist/ForenstiqEvidenceAnalyzer")
        print("\nTo distribute:")
        print("1. Copy the entire 'dist' folder")
        print("2. Include config/settings.ini")
        print("3. Install Tesseract OCR on target machine")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Build failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    build_executable()