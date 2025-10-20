# Changelog - Forenstiq Evidence Analyzer

All notable changes to this project are documented in this file.

---

## [1.0.0] - 2025-10-14

### 🎉 Major Improvements

#### ✨ UI/UX Enhancements
- **NEW**: Modern Material Design-inspired stylesheet
- **NEW**: Improved button styling with hover effects
- **NEW**: Better color scheme (Google Material colors)
- **NEW**: Enhanced visual feedback for all interactive elements
- **NEW**: Smooth transitions and modern card-style widgets
- **NEW**: Professional typography and spacing

#### 🐛 Critical Bug Fixes
1. **FIXED**: `QApplication` not imported error during file import
   - Added missing import in `src/ui/main_window.py:7`
   - File imports now work correctly

2. **FIXED**: Qt High DPI scaling warning
   - Moved `QApplication.setAttribute()` calls before QApplication instantiation
   - Fixed in `src/main.py:52-54`

3. **FIXED**: Tesseract OCR path error on macOS
   - Added auto-detection for Tesseract installation path
   - Supports macOS, Windows, and Linux
   - Modified `src/ai/ocr_engine.py`

4. **FIXED**: Deprecated torchvision warning
   - Updated from `pretrained=True` to `weights=ResNet50_Weights.IMAGENET1K_V1`
   - Fixed in `src/ai/image_classifier.py:27-28`

#### 🔧 Code Quality Improvements
- **IMPROVED**: Error handling throughout the application
- **IMPROVED**: Logging instead of print statements
- **IMPROVED**: Consistent error messages
- **IMPROVED**: Better exception handling in AI modules

#### 📝 Documentation
- **NEW**: Comprehensive README.md with:
  - Installation instructions
  - User guide
  - Technology stack overview
  - Project structure
  - Troubleshooting guide
  - Performance metrics
- **NEW**: CHANGELOG.md (this file)

---

## Technical Changes

### Files Modified

1. **src/main.py**
   - Moved High DPI attributes before QApplication creation
   - Added modern stylesheet import and application
   - Fixed initialization order

2. **src/ui/main_window.py**
   - Added `QApplication` to imports
   - Fixed missing import error

3. **src/ui/styles.py** (NEW)
   - Created comprehensive modern stylesheet
   - Added helper functions for button styles
   - Material Design color palette

4. **src/ui/widgets/case_info_widget.py**
   - Updated to use new button styles
   - Improved section headers
   - Better visual hierarchy

5. **src/ai/ocr_engine.py**
   - Added auto-detection for Tesseract path
   - Cross-platform support
   - Better error handling

6. **src/ai/image_classifier.py**
   - Fixed deprecated `pretrained` parameter
   - Updated to use `weights` parameter
   - Modernized model loading

7. **src/core/file_scanner.py**
   - Improved error logging
   - Better exception messages

8. **README.md** (NEW)
   - Complete project documentation
   - User guide and installation instructions

9. **CHANGELOG.md** (NEW)
   - This file documenting all changes

---

## Warnings Resolved

### Before:
```
Attribute Qt::AA_EnableHighDpiScaling must be set before QCoreApplication is created.
Error importing <file>: name 'QApplication' is not defined
Error extracting text: C:\Program Files\Tesseract-OCR\tesseract.exe is not installed
UserWarning: The parameter 'pretrained' is deprecated
```

### After:
```
✅ All warnings resolved
✅ Clean application startup
✅ Proper error handling
```

---

## Performance

No performance regressions. All improvements are cosmetic or bug fixes.

---

## Breaking Changes

None. This is the initial stable release.

---

## Known Issues

1. **Font Warning**: Qt warns about missing "Monospace" font (cosmetic only, no impact)
   - This is a Qt framework warning on macOS
   - Does not affect functionality

2. **pkg_resources Warning**: External dependency warning from face_recognition_models
   - This is from a third-party library
   - Will be resolved when the library updates

---

## Upgrade Notes

This is the initial 1.0.0 release. No upgrade steps needed.

---

## Credits

**Development**: Forenstiq AI Technologies
**Testing**: Comprehensive manual testing completed
**Date**: October 14, 2025

---

## Next Steps

See ROADMAP in README.md for upcoming features.

Priority items:
- Video analysis
- Face clustering
- Timeline visualization
- Advanced search

---

*For support or questions, check README.md or contact Forenstiq AI Technologies*
