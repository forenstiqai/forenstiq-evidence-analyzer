# Forenstiq Evidence Analyzer - Distribution Guide

## 📦 Building Standalone Executables

This guide explains how to create standalone executables for macOS and Windows that can be distributed and run without Python installed.

---

## 🍎 macOS Build Instructions

### Prerequisites
- macOS 10.13 or later
- Python 3.9+ with virtual environment
- All dependencies installed (`pip install -r requirements.txt`)

### Build Steps

1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run the build script:**
   ```bash
   ./build_macos.sh
   ```

3. **Find your application:**
   - The built app will be at: `dist/Forenstiq Evidence Analyzer.app`
   - This is a complete macOS application bundle

### Distribution Options

#### Option 1: Direct Distribution
Simply copy the entire `dist/Forenstiq Evidence Analyzer.app` folder to any Mac and double-click to run.

#### Option 2: Create a DMG (Recommended)
Create a disk image for easier distribution:
```bash
hdiutil create -volname "Forenstiq Evidence Analyzer" \
  -srcfolder "dist/Forenstiq Evidence Analyzer.app" \
  -ov -format UDZO Forenstiq-macOS.dmg
```

### Code Signing (Optional but Recommended)
For distribution outside your organization, you should code sign the app:
```bash
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  "dist/Forenstiq Evidence Analyzer.app"
```

---

## 🪟 Windows Build Instructions

### Prerequisites
- Windows 10 or later
- Python 3.9+ with virtual environment
- All dependencies installed (`pip install -r requirements.txt`)

### Build Steps

1. **Activate your virtual environment:**
   ```cmd
   venv\Scripts\activate.bat
   ```

2. **Run the build script:**
   ```cmd
   build_windows.bat
   ```

3. **Find your application:**
   - The executable and all dependencies will be in: `dist\Forenstiq\`
   - Main executable: `dist\Forenstiq\Forenstiq.exe`

### Distribution Options

#### Option 1: Folder Distribution
- Copy the entire `dist\Forenstiq\` folder to any Windows PC
- All dependencies are included
- Users run `Forenstiq.exe`

#### Option 2: Create an Installer (Recommended)
Use installer creation tools:

**Inno Setup (Free & Popular):**
1. Download from: https://jrsoftware.org/isinfo.php
2. Create a script to package the `dist\Forenstiq\` folder
3. Generates a professional Windows installer

**NSIS (Free):**
- Download from: https://nsis.sourceforge.io/
- Create installer script for the application

**WiX Toolset (Free, Microsoft-standard):**
- Download from: https://wixtoolset.org/
- Creates MSI installers

---

## 📋 What's Included in the Executables

Both macOS and Windows executables include:
- Complete Python runtime
- All required libraries (PyQt5, OpenCV, PyTorch, etc.)
- AI models for image analysis
- Face detection models
- All application source code
- Database initialization

---

## 📊 Build Output Information

### macOS App Bundle Structure
```
Forenstiq Evidence Analyzer.app/
├── Contents/
│   ├── MacOS/              # Executable binary
│   ├── Resources/          # Application resources
│   └── Info.plist         # App metadata
```

### Windows Distribution Structure
```
Forenstiq/
├── Forenstiq.exe          # Main executable
├── *.dll                  # Required libraries
├── _internal/             # Python runtime and dependencies
└── [AI models and data]
```

---

## 🔍 Testing the Executables

### macOS Testing
```bash
# Test the app directly
open "dist/Forenstiq Evidence Analyzer.app"

# Or run from command line to see logs
"dist/Forenstiq Evidence Analyzer.app/Contents/MacOS/Forenstiq"
```

### Windows Testing
```cmd
# Run the executable
dist\Forenstiq\Forenstiq.exe

# Or from command line in that directory
cd dist\Forenstiq
Forenstiq.exe
```

---

## 📦 Expected File Sizes

- **macOS .app**: ~1.5-2 GB (due to PyTorch and AI models)
- **Windows folder**: ~1.5-2 GB
- **macOS DMG (compressed)**: ~800 MB - 1.2 GB
- **Windows Installer**: ~800 MB - 1.2 GB

---

## 🚨 Common Issues & Solutions

### macOS: "App is damaged and can't be opened"
This happens when the app isn't signed. Users can bypass with:
```bash
xattr -cr "/path/to/Forenstiq Evidence Analyzer.app"
```

Or right-click → Open → Open

### macOS: "App from unidentified developer"
Go to System Preferences → Security & Privacy → Allow app to run

### Windows: "Windows protected your PC"
Click "More info" → "Run anyway"

### Large File Size
The executables are large because they include:
- Complete Python runtime
- PyTorch (~500 MB)
- YOLOv8 models (~100 MB)
- Face recognition models (~100 MB)
- All other dependencies

---

## 🔄 Updating the Application

To create a new version:
1. Update your source code
2. Run the build script again
3. The new executable will replace the old one in `dist/`

---

## 🎯 System Requirements

### macOS
- **OS:** macOS 10.13 High Sierra or later
- **Architecture:** Intel or Apple Silicon (M1/M2)
- **RAM:** Minimum 4 GB (8 GB recommended)
- **Storage:** 2 GB free space

### Windows
- **OS:** Windows 10 or Windows 11
- **Architecture:** 64-bit
- **RAM:** Minimum 4 GB (8 GB recommended)
- **Storage:** 2 GB free space

---

## 📝 Notes

- The executables are platform-specific (macOS app won't run on Windows and vice versa)
- First launch may take longer as the application unpacks
- Antivirus software may need to whitelist the executable
- The app creates local folders for data, logs, and reports on first run

---

## 🛠️ Build Configuration

The build process is controlled by:
- `forenstiq.spec` - PyInstaller specification file
- `build_macos.sh` - macOS build automation
- `build_windows.bat` - Windows build automation

To customize the build (e.g., add an icon), edit `forenstiq.spec`:
```python
# Add icon (line ~65)
icon='path/to/icon.icns',  # macOS
# or
icon='path/to/icon.ico',   # Windows
```

---

## 📧 Support

For build issues or questions:
- Check PyInstaller documentation: https://pyinstaller.org/
- Review the build logs in the terminal
- Ensure all dependencies are correctly installed

---

**© 2024 Forenstiq AI Technologies**
Advanced Digital Forensics Platform
