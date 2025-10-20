# 🚀 Quick Start Guide - Building Executables

## For macOS (Your Current System)

### Build the macOS Application
```bash
cd "/Users/rohithsaikandelli/Documents/Forenstiq AI Technologies/forenstiq-evidence-analyzer"
./build_macos.sh
```

**Output:** `dist/Forenstiq Evidence Analyzer.app`

### Create a DMG for Distribution
```bash
hdiutil create -volname "Forenstiq Evidence Analyzer" \
  -srcfolder "dist/Forenstiq Evidence Analyzer.app" \
  -ov -format UDZO Forenstiq-macOS.dmg
```

**Output:** `Forenstiq-macOS.dmg` (~800 MB compressed)

---

## For Windows (Build on Windows PC)

### 1. Transfer Files to Windows
Copy the entire project folder to a Windows computer.

### 2. Setup on Windows
```cmd
cd "path\to\forenstiq-evidence-analyzer"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller
```

### 3. Build the Windows Application
```cmd
build_windows.bat
```

**Output:** `dist\Forenstiq\Forenstiq.exe` (with dependencies)

---

## 📤 Distribution

### macOS
**Option 1:** Send the `.dmg` file
- Recipients double-click the DMG
- Drag app to Applications folder
- Done!

**Option 2:** Send the `.app` directly
- Zip the "Forenstiq Evidence Analyzer.app"
- Recipients unzip and double-click to run

### Windows
**Option 1:** Send the folder
- Zip the entire `dist\Forenstiq\` folder
- Recipients unzip and run `Forenstiq.exe`

**Option 2:** Create installer (recommended)
- Use Inno Setup or NSIS to create a proper installer
- Easier for end users

---

## ✅ What You Have Now

✓ **forenstiq.spec** - Build configuration
✓ **build_macos.sh** - Automated macOS build
✓ **build_windows.bat** - Automated Windows build
✓ **dist/Forenstiq Evidence Analyzer.app** - Ready to distribute!

---

## 🎯 Next Steps

1. **Test the macOS app** on your system
2. **Transfer project to Windows** if you need Windows executable
3. **Create DMG** for professional macOS distribution
4. **Share with testers** on both platforms

---

## 📊 File Sizes to Expect

- macOS .app: ~1.5-2 GB
- macOS DMG: ~800 MB
- Windows folder: ~1.5-2 GB
- Windows installer: ~800 MB

---

## 🆘 Quick Troubleshooting

**macOS "Can't be opened" error:**
```bash
xattr -cr "/path/to/Forenstiq Evidence Analyzer.app"
```

**Windows "Protected your PC":**
Click "More info" → "Run anyway"

**Build fails with recursion error:**
Already fixed in forenstiq.spec! ✓

---

**Ready to test! Your macOS executable is built and ready at:**
`dist/Forenstiq Evidence Analyzer.app`
