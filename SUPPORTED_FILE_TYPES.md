# Supported File Types - Forenstiq Evidence Analyzer

## Overview

Forenstiq Evidence Analyzer supports **100+ file types** across 10 major categories. The tool can process both individual files and entire forensic extraction archives.

---

## Input Methods

### 1. **Individual Files & Folders** (Current Implementation)
- Drag & drop folder containing evidence
- File scanner recursively processes all files
- All file types are imported and cataloged

### 2. **Forensic Extraction Archives** (NEW - High Performance)
- Cellebrite exports (.zip, .ufdr, .clbx)
- Oxygen Forensics exports (.ofb, .zip)
- Magnet AXIOM exports (.mfdb)
- Generic ZIP archives
- **30-100x faster loading** than competitors

---

## Supported File Categories

## 1. **Images** (Primary Focus - AI Analysis)

| Extension | Format | AI Analysis | Notes |
|-----------|--------|-------------|-------|
| .jpg, .jpeg | JPEG | ✅ Full | Face detection, object detection, OCR |
| .png | PNG | ✅ Full | Screenshots, graphics |
| .gif | GIF | ✅ Full | Animated images |
| .bmp | Bitmap | ✅ Full | Uncompressed images |
| .tiff, .tif | TIFF | ✅ Full | High-quality images |
| .webp | WebP | ✅ Full | Modern web format |
| .heic, .heif | HEIC/HEIF | ✅ Full | iPhone photos (iOS 11+) |

**AI Analysis Capabilities:**
- **Face Detection & Recognition** - Identify and cluster faces
- **Object Detection** - Weapons, drugs, vehicles, etc.
- **OCR (Text Extraction)** - Extract text from images
- **EXIF Metadata** - GPS, camera, timestamp
- **Perceptual Hashing** - Find similar/duplicate images

---

## 2. **Videos**

| Extension | Format | AI Analysis | Notes |
|-----------|--------|-------------|-------|
| .mp4 | MP4/MPEG-4 | 🔄 Planned | Most common format |
| .mov | QuickTime | 🔄 Planned | iPhone videos |
| .avi | AVI | 🔄 Planned | Legacy format |
| .mkv | Matroska | 🔄 Planned | High-quality container |
| .wmv | Windows Media | 🔄 Planned | Windows format |
| .flv | Flash Video | 🔄 Planned | Web videos |
| .webm | WebM | 🔄 Planned | YouTube format |
| .m4v | iTunes Video | 🔄 Planned | Apple format |
| .mpeg, .mpg | MPEG | 🔄 Planned | Standard format |

**Planned Video Analysis:**
- Frame-by-frame face detection
- Object tracking across frames
- Scene detection
- Audio transcription
- Metadata extraction

---

## 3. **Documents**

| Extension | Format | OCR Support | Notes |
|-----------|--------|-------------|-------|
| .pdf | PDF | ✅ Yes | Scanned & text PDFs |
| .doc, .docx | Microsoft Word | 📄 Text Extract | Office documents |
| .xls, .xlsx | Microsoft Excel | 📄 Text Extract | Spreadsheets |
| .ppt, .pptx | PowerPoint | 📄 Text Extract | Presentations |
| .txt | Plain Text | ✅ Yes | Text files |
| .rtf | Rich Text | 📄 Text Extract | Formatted text |
| .csv | CSV | ✅ Yes | Data files |
| .odt | OpenDocument | 📄 Text Extract | LibreOffice Writer |
| .ods | OpenDocument | 📄 Text Extract | LibreOffice Calc |
| .odp | OpenDocument | 📄 Text Extract | LibreOffice Impress |
| .pages | Apple Pages | ⚠️ Limited | macOS format |
| .numbers | Apple Numbers | ⚠️ Limited | macOS format |
| .keynote | Apple Keynote | ⚠️ Limited | macOS format |

**Document Analysis:**
- Full text extraction
- Keyword search
- Date/time metadata
- Author information

---

## 4. **Audio Files**

| Extension | Format | Analysis | Notes |
|-----------|--------|----------|-------|
| .mp3 | MP3 | 🔄 Planned | Most common |
| .wav | WAV | 🔄 Planned | Uncompressed |
| .m4a | M4A/AAC | 🔄 Planned | iPhone recordings |
| .aac | AAC | 🔄 Planned | Advanced Audio Coding |
| .flac | FLAC | 🔄 Planned | Lossless |
| .wma | Windows Media | 🔄 Planned | Windows format |
| .ogg | Ogg Vorbis | 🔄 Planned | Open format |
| .opus | Opus | 🔄 Planned | VoIP quality |
| .aiff | AIFF | 🔄 Planned | Apple format |
| .ape | APE | 🔄 Planned | Lossless |
| .alac | ALAC | 🔄 Planned | Apple Lossless |

**Planned Audio Analysis:**
- Speech-to-text transcription
- Speaker identification
- Audio fingerprinting
- Metadata extraction

---

## 5. **Archives** (Forensic Extraction Files)

| Extension | Format | Fast Load | Notes |
|-----------|--------|-----------|-------|
| .zip | ZIP | ✅ Yes | **21.6x faster** than extraction |
| .rar | RAR | 🔄 Planned | Common compression |
| .7z | 7-Zip | 🔄 Planned | High compression |
| .tar | TAR | 🔄 Planned | Unix archive |
| .gz, .gzip | GZIP | 🔄 Planned | Compression |
| .bz2 | BZIP2 | 🔄 Planned | Compression |
| .tar.gz, .tgz | Tarball | 🔄 Planned | Combined archive |
| .tar.bz2, .tbz2 | Tarball | 🔄 Planned | Combined archive |

**Special Forensic Formats:**
| Extension | Tool | Status | Performance |
|-----------|------|--------|-------------|
| .ufdr | Cellebrite UFED | ✅ Supported | 30-100x faster |
| .ofb | Oxygen Forensics | ✅ Supported | 30-100x faster |
| .clbx | Cellebrite | ✅ Supported | 30-100x faster |
| .mfdb | Magnet AXIOM | ✅ Supported | 30-100x faster |
| .ab | Android Backup | 🔄 Planned | - |
| .bin, .dd, .raw | Raw Images | 🔄 Planned | - |

---

## 6. **Databases** (Critical for Mobile Forensics)

| Extension | Type | Analysis | Common Source |
|-----------|------|----------|---------------|
| .db | SQLite | ✅ Yes | Android apps, iOS apps |
| .sqlite, .sqlite3 | SQLite | ✅ Yes | WhatsApp, Messages |
| .sql | SQL Dump | 📄 Text | Database exports |
| .mdb | MS Access | ⚠️ Limited | Windows databases |
| .accdb | MS Access | ⚠️ Limited | Modern Access |
| .dbf | dBASE | ⚠️ Limited | Legacy databases |

**Important Mobile Databases:**
- **WhatsApp:** `msgstore.db`, `wa.db`
- **iMessage:** `sms.db`, `chat.db`
- **Contacts:** `contacts.db`, `contacts2.db`
- **Call Logs:** `callhistory.db`, `calls.db`
- **Browser History:** `browser.db`, `history.db`

---

## 7. **Email Files**

| Extension | Format | Analysis | Notes |
|-----------|--------|----------|-------|
| .eml | Email Message | 📧 Parse | Individual emails |
| .msg | Outlook Message | 📧 Parse | Microsoft format |
| .pst | Outlook Archive | 📧 Parse | Full mailbox |
| .ost | Outlook Offline | 📧 Parse | Cached mailbox |
| .mbox | MBOX | 📧 Parse | Unix mail format |
| .emlx | Apple Mail | 📧 Parse | macOS mail |

**Email Analysis:**
- Sender/recipient extraction
- Attachment processing
- Header analysis
- Timeline construction

---

## 8. **Code & Scripts** (For Digital Evidence)

| Extension | Language | Analysis | Notes |
|-----------|----------|----------|-------|
| .py | Python | 📄 Text | Scripts |
| .java | Java | 📄 Text | Android apps |
| .js, .ts | JavaScript | 📄 Text | Web apps |
| .jsx, .tsx | React | 📄 Text | Web apps |
| .cpp, .c, .h | C/C++ | 📄 Text | Native apps |
| .php | PHP | 📄 Text | Web scripts |
| .rb | Ruby | 📄 Text | Scripts |
| .go | Go | 📄 Text | Modern apps |
| .rs | Rust | 📄 Text | Systems |
| .swift | Swift | 📄 Text | iOS apps |
| .kt | Kotlin | 📄 Text | Android apps |
| .html, .css | Web | 📄 Text | Web pages |
| .xml, .json | Data | 📄 Text | Config files |
| .yaml, .yml | YAML | 📄 Text | Config files |
| .sh, .bat, .ps1 | Shell | 📄 Text | Scripts |

---

## 9. **Executables & Applications**

| Extension | Platform | Analysis | Notes |
|-----------|----------|----------|-------|
| .exe | Windows | 🔍 Hash | Executables |
| .dll | Windows | 🔍 Hash | Libraries |
| .app | macOS | 🔍 Hash | Applications |
| .apk | Android | 🔍 Hash | Android apps |
| .ipa | iOS | 🔍 Hash | iOS apps |
| .deb | Linux | 🔍 Hash | Debian packages |
| .rpm | Linux | 🔍 Hash | RedHat packages |
| .dmg | macOS | 🔍 Hash | Disk images |
| .pkg | macOS | 🔍 Hash | Installers |
| .msi | Windows | 🔍 Hash | Installers |
| .so | Linux | 🔍 Hash | Shared libraries |
| .dylib | macOS | 🔍 Hash | Dynamic libraries |

**Security Analysis:**
- File hash calculation (MD5, SHA256)
- Malware detection (planned)
- Code signing verification (planned)

---

## 10. **System & Log Files**

| Extension | Type | Analysis | Notes |
|-----------|------|----------|-------|
| .log | Log File | 📄 Parse | System logs |
| .ini | Config | 📄 Parse | Windows config |
| .cfg, .conf | Config | 📄 Parse | Settings |
| .reg | Registry | 📄 Parse | Windows registry |
| .plist | Property List | 📄 Parse | macOS/iOS config |
| .dat | Data | 🔍 Hex | Binary data |
| .tmp | Temporary | 🔍 Hex | Temp files |
| .bak | Backup | 🔍 Hex | Backup files |
| .sys | System | 🔍 Hex | System files |

---

## Analysis Capabilities by File Type

### ✅ **Full AI Analysis** (Images)
- Face detection & recognition
- Object detection (weapons, drugs, vehicles)
- OCR (text extraction)
- EXIF metadata (GPS, camera, timestamp)
- Perceptual hashing (duplicate detection)
- Image classification

### 📄 **Text Extraction** (Documents)
- Full text extraction
- Metadata extraction
- Keyword search
- Timeline analysis

### 📧 **Email Parsing** (Email Files)
- Sender/recipient extraction
- Attachment processing
- Header analysis
- Thread reconstruction

### 🔍 **Hash & Metadata** (All Files)
- SHA256/MD5 hash calculation
- File size and timestamps
- File type detection
- Duplicate detection

### 🔄 **Planned Features**
- Video analysis (frame extraction, object tracking)
- Audio transcription (speech-to-text)
- Advanced malware analysis
- Network packet analysis

---

## File Size Limits

| File Type | Recommended Max | Hard Limit | Notes |
|-----------|----------------|------------|-------|
| Images | 50 MB | 500 MB | For AI processing |
| Videos | 5 GB | No limit | Processed in chunks |
| Documents | 100 MB | 1 GB | For text extraction |
| Databases | 500 MB | No limit | SQLite optimization |
| Archives | No limit | No limit | Streaming parser |
| Other | No limit | No limit | Basic metadata only |

---

## Special Cases

### **Mobile Device Extractions**
When you import a Cellebrite/Oxygen/UFED extraction, you typically get:

**Android:**
- Images: `DCIM/`, `Pictures/`, `Screenshots/`
- Databases: `data/data/com.whatsapp/databases/msgstore.db`
- Contacts: `data/data/com.android.providers.contacts/databases/contacts2.db`
- Call logs: `data/data/com.android.providers.contacts/databases/calllog.db`
- Browser: `data/data/com.android.browser/databases/browser.db`

**iOS:**
- Images: `Media/DCIM/`, `PhotoData/`
- Databases: `HomeDomain/Library/SMS/sms.db`
- Contacts: `HomeDomain/Library/AddressBook/AddressBook.sqlitedb`
- Call logs: Part of `sms.db`
- Safari: `HomeDomain/Library/Safari/`

**All these files are automatically detected and imported!**

---

## Performance by File Type

| File Type | Import Speed | AI Processing | Notes |
|-----------|-------------|---------------|-------|
| Images | ~1000/sec | ~10/sec | Fast import, slower AI |
| Videos | ~100/sec | N/A | Metadata only |
| Documents | ~500/sec | ~50/sec | Fast OCR |
| Databases | ~200/sec | N/A | SQLite parsing |
| Archives | **293,136/sec** | N/A | **Streaming index!** |
| Other | ~1000/sec | N/A | Metadata only |

**Archive Processing Speed:**
- Traditional tools: Extract all → 3+ hours
- Forenstiq: Stream index → **1-3 minutes**
- **Speedup: 30-100x faster!**

---

## Not Supported (Yet)

| Type | Extensions | Status | ETA |
|------|-----------|--------|-----|
| 3D Models | .obj, .fbx, .blend | Planned | Q2 2025 |
| CAD Files | .dwg, .dxf | Planned | Q3 2025 |
| Encrypted | .encrypted, .gpg | Planned | Q2 2025 |
| Virtual Machines | .vmdk, .vdi | Planned | Q4 2025 |
| Container Images | .docker, .iso | Planned | Q4 2025 |

---

## Summary

**Total Supported Extensions: 100+**

- **Images:** 7 formats ✅ Full AI support
- **Videos:** 9 formats 🔄 Metadata only (AI planned)
- **Documents:** 13 formats ✅ Text extraction
- **Audio:** 11 formats 🔄 Metadata only (transcription planned)
- **Archives:** 8+ formats ✅ **High-speed streaming**
- **Databases:** 6+ formats ✅ SQLite parsing
- **Email:** 6 formats ✅ Full parsing
- **Code:** 25+ formats ✅ Text extraction
- **Executables:** 12 formats ✅ Hash & metadata
- **System:** 10+ formats ✅ Log parsing

**Key Differentiator:**
Forensic extraction archives (.zip, .ufdr, .ofb) load **30-100x faster** than competitor tools!

---

## Usage Example

```python
# Import any supported file type
from src.core.file_scanner import FileScanner

scanner = FileScanner()

# Option 1: Import folder with mixed files
stats = scanner.scan_and_import(
    directory=Path("/evidence/phone_extraction"),
    case_id=123
)

# Option 2: Import forensic archive (FAST!)
from src.core.extraction_loader import ExtractionLoader

loader = ExtractionLoader()
stats = loader.load_extraction_fast(
    extraction_path=Path("cellebrite_export.zip"),
    case_id=123
)
# Loads 10,000 files in ~45 seconds!
```

---

## Questions?

- For file type support questions, check this document
- For extraction performance, see `EXTRACTION_PERFORMANCE.md`
- For quick start, see `EXTRACTION_QUICK_START.md`
