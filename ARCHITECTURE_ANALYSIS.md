# Forenstiq Evidence Analyzer - Architecture Analysis & Validation Plan

**Generated:** 2025-10-28
**Purpose:** Reverse-engineered architecture documentation and validation plan

---

## STEP 1: Component Architecture (The "What")

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  FORENSTIQ APPLICATION (main.py)                │
│                    ↓ AIService Singleton (loaded at startup)    │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ UI LAYER │───────▶│   CORE   │───────▶│    AI    │
    │          │        │ BUSINESS │        │  ENGINE  │
    └──────────┘        │  LOGIC   │        └──────────┘
          │             └──────────┘              │
          │                   │                   │
          │                   ▼                   │
          │             ┌──────────┐              │
          └────────────▶│ DATABASE │◀─────────────┘
                        │  LAYER   │
                        └──────────┘
```

### 1. UI Layer (`src/ui/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Main Window** | `main_window.py` | Application entry & splash screen |
| **Device Dashboard** | `device_selection_dashboard.py` | Device type selector (mobile, storage, CCTV, etc.) |
| **Evidence Analyzer** | `evidence_analyzer_window.py` (31KB) | **Main workbench** - Primary user interface |
| **Preview Widget** | `widgets/preview_widget.py` | File preview & metadata display |
| **File List Widget** | `widgets/file_list_widget.py` | Evidence file browser |
| **Case Info Widget** | `widgets/case_info_widget.py` | Case details panel |
| **Background Workers** | `workers/analysis_worker.py` | Keeps UI responsive during AI processing |

**Key Design:** UI uses **signals/slots** (Qt) to communicate. AIService singleton is passed from main.py:148-152.

---

### 2. Core Business Logic (`src/core/`)

| Component | File | Lines | Purpose |
|-----------|------|-------|---------|
| **High-Performance Loader** | `extraction_loader.py` | 16KB | Streaming ZIP parser with ThreadPoolExecutor |
| **AI Orchestrator** | `ai_analyzer.py` | 10KB | Coordinates face/object/OCR operations |
| **AI Service** | `ai_service.py` | 3.5KB | **Singleton** - Loads all AI models once at startup |
| **Case Manager** | `case_manager.py` | 3.4KB | Case CRUD operations |
| **File Scanner** | `file_scanner.py` | 5.4KB | Directory scanning & import |
| **Metadata Extractor** | `metadata_extractor.py` | 8KB | EXIF, GPS, camera data |
| **Report Generator** | `report_generator.py` | 21KB | PDF report creation |
| **Specialized Parsers** | `csv_parser.py`, `whatsapp_parser.py` | ~14KB each | Evidence-specific parsing |

**Critical Components:**

1. **`extraction_loader.py`** (Lines 88-131):
   - Uses `zipfile.ZipFile.infolist()` to build index WITHOUT loading file contents
   - `ThreadPoolExecutor` for parallel file processing
   - Supports `.ufdr`, `.zip`, `.ofb`, `.tar`, `.ab` formats
   - **Lazy hash calculation** (hash NOT computed during indexing)

2. **`ai_service.py`** (Lines 19-47):
   - **Singleton pattern** ensures models load only once
   - Config-driven: can disable face detection, OCR, or object detection
   - Models: ResNet50, YOLOv8n, dlib, Tesseract

3. **`ai_analyzer.py`** (Lines 209-260):
   - `analyze_case()`: Processes ALL unprocessed files (batch mode)
   - `analyze_file()`: Processes single file (routes by file type)
   - Updates `ai_processed` flag in database after analysis

---

### 3. AI Engine (`src/ai/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Face Detector** | `face_detector.py` | dlib/face_recognition |
| **Face Matcher** | `face_matcher.py` | Suspect face matching/clustering |
| **Object Detector** | `object_detector.py` | YOLOv8n (vehicles, weapons, electronics) |
| **OCR Engine** | `ocr_engine.py` | Tesseract/EasyOCR text extraction |
| **Image Classifier** | `image_classifier.py` | ResNet50 ImageNet classification |
| **Text Analyzer** | `text_analyzer.py` | Document text analysis |

**Model Files:**
- `yolov8n.pt` (8MB) - Object detection model
- ResNet50 (downloaded from torchvision)
- dlib models (face landmarks)

---

### 4. Database Layer (`src/database/`)

**Schema:** `schema.sql` (138 lines)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **cases** | Case metadata | `case_id`, `case_number`, `case_name`, `status` |
| **evidence_files** | File records | `file_id`, `case_id`, `file_path`, `file_hash`, **`ai_processed`** |
| **face_detections** | Detected faces | `face_id`, `file_id`, `face_encoding`, `bounding_box` |
| **object_detections** | Detected objects | `detection_id`, `file_id`, `object_class`, `confidence` |
| **audit_log** | Chain of custody | `log_id`, `case_id`, `action`, `timestamp` |
| **tags** | Evidence tags | `tag_id`, `tag_name`, `tag_category` |

**Critical Fields:**
- `evidence_files.ai_processed` (Line 50): Boolean flag - **Controls caching logic**
- `evidence_files.ai_tags` (Line 51): JSON string of detected tags
- `evidence_files.file_hash` (Line 30): SHA-256 (calculated lazily)

**Repositories:**
- `file_repository.py`: `get_unprocessed_files()` returns files where `ai_processed = 0`
- `case_repository.py`: Case CRUD
- `audit_repository.py`: Forensic audit trail

---

### 5. Data Stores

| Store | Path | Purpose | Read-Only? | Integrity |
|-------|------|---------|------------|-----------|
| **Original Evidence** | `evidence.zip` (user-selected) | Source archive | ✅ YES | **NEVER modified** |
| **Case Database** | `data/case_XYZ.db` | Analysis results | ❌ NO | SQLite with transactions |
| **Temp Extraction** | `temp/` | Temporary file extraction | ❌ NO | Cleaned after use |
| **Reports** | `reports/` | Generated PDFs | ❌ NO | Write-only |
| **Logs** | `logs/` | Application logs | ❌ NO | Append-only |
| **Evidence Storage** | `evidence_storage/` | Case file copies | ❌ NO | Read/Write |

---

## STEP 2: Application Flow (The "How")

### Primary User Flow: Import → Analyze → Report

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. APPLICATION STARTUP                                          │
└─────────────────────────────────────────────────────────────────┘
   main.py:121-162
   ├─> setup_application() → Create dirs (data/, logs/, reports/, temp/)
   ├─> AIService() → Load ALL AI models (ResNet50, YOLOv8, Face, OCR)
   │   └─> ai_service.py:49-93 (SINGLETON - happens ONCE)
   └─> ForenstiqApplication.start()
       └─> SplashScreen → DeviceSelectionDashboard → EvidenceAnalyzerWindow

┌─────────────────────────────────────────────────────────────────┐
│ 2. CREATE NEW CASE                                              │
└─────────────────────────────────────────────────────────────────┘
   evidence_analyzer_window.py:231-272
   ├─> User: File → New Case
   ├─> NewCaseDialog.show()
   │   └─> User enters: case_number, case_name, investigator_name
   ├─> case_manager.create_case()
   │   └─> Creates SQLite DB: data/case_{case_number}.db
   │   └─> Inserts record into 'cases' table
   └─> UI: Updates case_info_widget

┌─────────────────────────────────────────────────────────────────┐
│ 3. IMPORT EVIDENCE FILES                                        │
└─────────────────────────────────────────────────────────────────┘
   evidence_analyzer_window.py:346-434
   ├─> User: Case → Import Files (or click "Import Files" button)
   ├─> QFileDialog: Select directory
   ├─> file_scanner.scan_and_import(directory, case_id)
   │   └─> file_scanner.py:
   │       ├─> Walk directory tree
   │       ├─> Detect file type by extension (extraction_loader.py:166-203)
   │       ├─> Extract EXIF metadata (metadata_extractor.py)
   │       ├─> For EACH file:
   │       │   └─> file_repository.add_file()
   │       │       └─> INSERT INTO evidence_files
   │       │           (file_path, file_type, file_size, date_modified, ...)
   │       │           ai_processed = 0  ← **NOT analyzed yet**
   │       └─> Return stats (images: X, videos: Y, documents: Z, ...)
   └─> UI: Show import summary dialog
       └─> Refresh file_list_widget (displays all imported files)

   **CRITICAL:** Files are imported but NOT analyzed. ai_processed = 0.

┌─────────────────────────────────────────────────────────────────┐
│ 4A. USER CLICKS ON FILE (Before Analysis)                      │
└─────────────────────────────────────────────────────────────────┘
   evidence_analyzer_window.py:745-747
   ├─> User: Clicks on file in file_list_widget
   ├─> SIGNAL: file_selected → on_file_selected(file_data)
   └─> preview_widget.load_file(file_data)
       └─> preview_widget.py:83-119
           ├─> Display image (if image file)
           ├─> Display metadata (basic info, dates, GPS, camera)
           ├─> Check: if file_data['ai_processed'] == 1:
           │       └─> Display AI tags, confidence, face count, OCR text
           │   else:
           │       └─> **NO AI RESULTS SHOWN** (not yet analyzed)
           └─> Enable flag/note buttons

   **KEY FINDING:** There is NO on-demand AI analysis when clicking a file!
   Files must be analyzed via the batch "Analyze Case" operation.

┌─────────────────────────────────────────────────────────────────┐
│ 4B. ANALYZE CASE (Batch AI Processing)                         │
└─────────────────────────────────────────────────────────────────┘
   evidence_analyzer_window.py:436-479
   ├─> User: Click "Start Analysis" button
   ├─> Confirmation dialog: "This will analyze all unprocessed files..."
   ├─> Create AnalysisWorker (background thread)
   │   └─> analysis_worker.py:23-38
   │       └─> analyzer = AIAnalyzer(ai_service)
   │           └─> analyzer.analyze_case(case_id)
   └─> ai_analyzer.py:209-260
       ├─> files = file_repo.get_unprocessed_files(case_id)
       │   └─> SELECT * WHERE case_id = ? AND ai_processed = 0
       ├─> FOR EACH file:
       │   ├─> results = analyze_file(file_id)
       │   │   └─> ai_analyzer.py:28-90
       │   │       ├─> Route by file_type:
       │   │       │   ├─> image → _analyze_image()
       │   │       │   │   └─> image_classifier.get_tags()
       │   │       │   │   └─> face_detector.detect_faces()
       │   │       │   │   └─> ocr_engine.extract_text()
       │   │       │   │   └─> object_detector.get_forensic_objects()
       │   │       │   ├─> video → _analyze_video() (stub)
       │   │       │   ├─> document → _analyze_document()
       │   │       │   └─> other → mark as analyzed
       │   │       └─> Return results dict
       │   ├─> file_repo.update_ai_analysis(file_id, analysis_data)
       │   │   └─> UPDATE evidence_files
       │   │       SET ai_processed = 1,
       │   │           ai_tags = ?,
       │   │           ai_confidence = ?,
       │   │           ocr_text = ?,
       │   │           face_count = ?,
       │   │           analyzed_date = NOW()
       │   │       WHERE file_id = ?
       │   └─> Emit progress signal → UI updates progress bar
       └─> Return stats (processed: X, faces: Y, text: Z, errors: W)

   **Result:** All files now have ai_processed = 1

┌─────────────────────────────────────────────────────────────────┐
│ 4C. USER CLICKS ON FILE (After Analysis)                       │
└─────────────────────────────────────────────────────────────────┘
   Same as 4A, but NOW ai_processed = 1:
   └─> preview_widget.display_metadata()
       └─> Shows: AI tags, confidence, face count, OCR text

   **Result:** User sees AI analysis results (cached in database)

┌─────────────────────────────────────────────────────────────────┐
│ 5. GENERATE REPORT                                              │
└─────────────────────────────────────────────────────────────────┘
   evidence_analyzer_window.py:525-629
   ├─> User: Click "Generate Report" button
   ├─> ReportOptionsDialog: Choose "Full Report" or "Flagged Only"
   ├─> QFileDialog: Save location
   ├─> report_generator.generate_report(case_id, file_path, flagged_only)
   │   └─> report_generator.py:
   │       ├─> Query database for case info & files
   │       ├─> Generate PDF with ReportLab
   │       │   ├─> Cover page (case details)
   │       │   ├─> Summary statistics
   │       │   ├─> File listing (with AI tags, metadata)
   │       │   ├─> Image thumbnails
   │       │   └─> Chain of custody (audit log)
   │       └─> Save to reports/
   └─> UI: Offer to open report (platform-specific: open/xdg-open/os.startfile)
```

---

### Critical Sequences

#### A. File Import Flow
```
User selects directory
  → FileScanner.scan_and_import()
    → Walk file tree
      → For each file:
        → Detect type by extension
        → Extract EXIF (if image)
        → INSERT INTO evidence_files (ai_processed = 0)
  → Show import stats dialog
  → Refresh file list widget
```

#### B. AI Analysis Flow (Batch)
```
User clicks "Analyze Case"
  → Confirm dialog
  → Create AnalysisWorker thread
    → AIAnalyzer.analyze_case()
      → Query: SELECT * WHERE ai_processed = 0
      → For each file:
        → AIAnalyzer.analyze_file()
          → Route by file_type
            → Face detection
            → Object detection (YOLO)
            → OCR (Tesseract)
            → Image classification (ResNet50)
          → UPDATE evidence_files SET ai_processed = 1
  → Show completion dialog
  → Refresh UI
```

#### C. File Preview Flow
```
User clicks file in list
  → on_file_selected(file_data)
    → PreviewWidget.load_file()
      → Display image/video/document
      → Display metadata (dates, GPS, camera)
      → if ai_processed == 1:
          → Display AI results
        else:
          → Skip AI section
```

---

## STEP 3: Data Flow (The "Where")

### Data Lifecycle

```
┌───────────────────────────────────────────────────────────────┐
│ ORIGINAL EVIDENCE (Read-Only)                                 │
│ evidence.zip / directory                                      │
│ ✅ NEVER MODIFIED - Forensic Integrity                        │
└───────────────────────────────────────────────────────────────┘
                          │
                          │ File Scanner
                          ▼
┌───────────────────────────────────────────────────────────────┐
│ CASE DATABASE (Read/Write)                                    │
│ data/case_{number}.db                                         │
│                                                               │
│ Tables:                                                       │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ evidence_files                                          │  │
│ │ ├─ file_path (reference to original)                   │  │
│ │ ├─ file_hash (SHA-256, lazy calculated)                │  │
│ │ ├─ ai_processed (0 or 1) ← CACHING FLAG                │  │
│ │ ├─ ai_tags (JSON string)                               │  │
│ │ ├─ ai_confidence (0.0-1.0)                             │  │
│ │ ├─ ocr_text (extracted text)                           │  │
│ │ ├─ face_count (integer)                                │  │
│ │ └─ is_flagged (boolean)                                │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ face_detections                                         │  │
│ │ ├─ file_id (FK)                                        │  │
│ │ ├─ face_encoding (BLOB - 128-dim vector)              │  │
│ │ └─ bounding_box (JSON)                                 │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ object_detections                                       │  │
│ │ ├─ file_id (FK)                                        │  │
│ │ ├─ object_class (string: "car", "weapon", etc.)       │  │
│ │ └─ confidence (0.0-1.0)                                │  │
│ └─────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌─────────────────────────────────────────────────────────┐  │
│ │ audit_log                                              │  │
│ │ ├─ action (import, analyze, flag, report)             │  │
│ │ └─ timestamp                                           │  │
│ └─────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
                          │
                          │ Report Generator
                          ▼
┌───────────────────────────────────────────────────────────────┐
│ REPORTS (Write-Only)                                          │
│ reports/Report_{case_number}_{date}.pdf                      │
└───────────────────────────────────────────────────────────────┘
```

### Data Modification Matrix

| Operation | Original Evidence | Case DB | Temp Dir | Reports |
|-----------|-------------------|---------|----------|---------|
| **Import Files** | ❌ NO | ✅ INSERT | ❌ NO | ❌ NO |
| **Analyze Case** | ❌ NO | ✅ UPDATE | ⚠️ MAYBE | ❌ NO |
| **View File** | ✅ READ | ✅ READ | ❌ NO | ❌ NO |
| **Flag File** | ❌ NO | ✅ UPDATE | ❌ NO | ❌ NO |
| **Generate Report** | ❌ NO | ✅ READ | ❌ NO | ✅ WRITE |

**Forensic Integrity Guarantee:**
- Original evidence files are **NEVER** modified (read-only access via `zipfile.ZipFile(..., 'r')`)
- All analysis results stored in separate SQLite database
- File hashes verify integrity
- Audit log tracks ALL operations (chain of custody)

---

### Critical Data Points

#### 1. The `ai_processed` Flag (schema.sql:50)
```sql
ai_processed BOOLEAN DEFAULT 0
```
**Purpose:** Cache control - prevents re-running AI on analyzed files

**State Machine:**
```
File Import → ai_processed = 0 (unprocessed)
    ↓
Analyze Case → ai_processed = 1 (processed)
    ↓
View File → Check flag:
    if 1: Display cached results
    if 0: Show "Not yet analyzed"
```

**Risk:** If flag is set to 1 WITHOUT saving results, user sees no AI data (data loss).

#### 2. Hash Calculation (Lazy)
```python
# extraction_loader.py:107-119
file_hash = None  # Not calculated during indexing!
```
**When calculated:** Only when explicitly requested (e.g., for report generation)
**Why:** Performance - hashing is expensive (100-500ms per file)

#### 3. Temp File Extraction
```python
# extraction_loader.py:132-164
def extract_file_stream(file_path: str) -> bytes
```
**When used:** For AI analysis (model needs file path, not bytes)
**Where stored:** `temp/` directory
**Cleanup:** Should be cleaned after analysis (verify this!)

---

## STEP 4: Validation Plan (The "Test")

### Test Case Matrix

| Test ID | Feature | Action Steps | Expected Result | Actual Result | Pass/Fail |
|---------|---------|--------------|-----------------|---------------|-----------|
| **TC-01** | **Case Creation** | 1. Launch app<br>2. File → New Case<br>3. Enter: case_number="TEST-001", case_name="Validation Test"<br>4. Click Create | 1. Folder `data/` created<br>2. SQLite DB `data/case_TEST-001.db` exists<br>3. UI shows case info panel<br>4. Status bar: "Case opened: Validation Test" | | |
| **TC-02** | **Evidence Import** | 1. Open case TEST-001<br>2. Case → Import Files<br>3. Select `sample_data/` directory<br>4. Wait for completion | 1. Progress dialog shows file count<br>2. Import completes in < 30sec (for 100 files)<br>3. Summary dialog shows breakdown by type<br>4. File list populates with all files | | |
| **TC-03** | **UI Responsiveness (During Import)** | 1. While TC-02 import is running<br>2. Click menu File → About<br>3. Move window | 1. About dialog opens immediately<br>2. Window moves smoothly<br>3. **UI never freezes** (background thread working) | | |
| **TC-04** | **File Preview (Before Analysis)** | 1. After TC-02 completes<br>2. Click on first image file<br>3. Observe preview panel | 1. Image displays within 1 sec<br>2. Metadata shows: filename, size, dates, GPS (if available)<br>3. **AI Analysis section is EMPTY** (ai_processed = 0)<br>4. Flag button is enabled | | |
| **TC-05** | **Batch AI Analysis** | 1. Click "Start Analysis" button<br>2. Confirm dialog → Yes<br>3. Wait for completion | 1. Progress dialog shows "Analyzing (1/100): filename.jpg"<br>2. Progress bar updates in real-time<br>3. Analysis completes (time depends on file count)<br>4. Summary dialog shows:<br>   - Files processed: 100<br>   - Faces detected: X<br>   - Files with text: Y<br>   - Objects found: Z | | |
| **TC-06** | **File Preview (After Analysis)** | 1. After TC-05 completes<br>2. Click on same image from TC-04<br>3. Observe preview panel | 1. Image displays within 1 sec<br>2. **AI Analysis section NOW shows:**<br>   - Tags: ["person", "vehicle", ...]<br>   - Confidence: 85.3%<br>   - Faces Detected: 2<br>   - OCR Text: (if text present)<br>3. Data loads **instantly** (cached in DB) | | |
| **TC-07** | **AI Result Caching** | 1. Click on different file (analyzed)<br>2. Click back to file from TC-06<br>3. Repeat 10 times | 1. Every click shows results **instantly** (< 100ms)<br>2. **No re-computation** (ai_processed = 1 prevents re-run)<br>3. Network/CPU usage stays low | | |
| **TC-08** | **Forensic Integrity (File Hash)** | 1. Before import: Get MD5 of `evidence.zip`<br>2. Run TC-02 (import)<br>3. Run TC-05 (analysis)<br>4. Run TC-12 (report generation)<br>5. After all: Get MD5 of `evidence.zip` | 1. MD5 hashes are **IDENTICAL**<br>2. Original evidence is **NEVER modified**<br>3. Audit log shows all operations | | |
| **TC-09** | **Face Matching** | 1. Tools → Load Suspect Photo<br>2. Select suspect photo<br>3. Set tolerance: 0.6<br>4. Start matching | 1. Progress dialog: "Checking: photo_001.jpg"<br>2. Matching completes<br>3. Dialog shows: "Found 5 photos containing suspect"<br>4. File list filters to show only matches<br>5. Matches sorted by confidence (highest first) | | |
| **TC-10** | **Flag Evidence** | 1. Select file with weapon detected<br>2. Click "Flag as Evidence" button<br>3. Refresh file list | 1. Flag button changes to "Unflag"<br>2. File metadata shows "=== FLAGGED ==="<br>3. File list shows flag icon next to file<br>4. Database: is_flagged = 1 | | |
| **TC-11** | **Report Generation (Full)** | 1. File → Generate Report<br>2. Select "Full Report"<br>3. Save as `TEST-001_full.pdf` | 1. Progress dialog: "Generating report..."<br>2. Report generates in < 60 sec<br>3. PDF opens, contains:<br>   - Cover page (case details)<br>   - Summary stats (total files, AI results)<br>   - File listing with thumbnails<br>   - AI tags for each file<br>   - Chain of custody (audit log) | | |
| **TC-12** | **Report Generation (Flagged Only)** | 1. File → Generate Report<br>2. Select "Flagged Items Only"<br>3. Save as `TEST-001_flagged.pdf` | 1. Report generates<br>2. PDF contains ONLY flagged files from TC-10<br>3. Summary shows: "Flagged items: 1 of 100" | | |
| **TC-13** | **Advanced Search (Text)** | 1. Tools → Advanced Search<br>2. Search type: "OCR Text"<br>3. Enter: "invoice"<br>4. Click Search | 1. Search completes<br>2. File list filters to show only files with "invoice" in OCR text<br>3. Preview shows highlighted OCR section | | |
| **TC-14** | **Advanced Search (Date Range)** | 1. Tools → Advanced Search<br>2. Date Range: 2024-01-01 to 2024-12-31<br>3. Click Search | 1. File list filters to show only files taken in 2024<br>2. Results sorted by date (newest first) | | |
| **TC-15** | **Error Handling (Missing File)** | 1. Manually delete a file from evidence_storage/<br>2. Click on that file in list | 1. Error dialog: "File not found: /path/to/file.jpg"<br>2. App does NOT crash<br>3. Log entry created | | |
| **TC-16** | **Error Handling (Corrupt AI Model)** | 1. Delete `yolov8n.pt`<br>2. Restart app<br>3. Run Analyze Case | 1. Startup log: "Object detector failed to load"<br>2. Analysis runs but skips object detection<br>3. App does NOT crash<br>4. Results show: "Objects: Not available" | | |
| **TC-17** | **Performance (Large Case)** | 1. Import 1,000 image files<br>2. Run Analyze Case<br>3. Measure time | 1. Import: < 2 minutes<br>2. Analysis: ~10-20 minutes (depends on hardware)<br>3. UI remains responsive throughout<br>4. Memory usage < 2 GB | | |
| **TC-18** | **Multi-Device Support** | 1. Launch app<br>2. Dashboard: Select "Mobile Devices"<br>3. Create case<br>4. Import files | 1. Window title: "Mobile Devices"<br>2. All features work identically<br>3. Report shows device type | | |

---

### Critical Test Scenarios

#### A. The "First Click" Bug Test
**Purpose:** Verify user expectations for on-demand analysis

**Steps:**
1. Import 10 image files (do NOT run Analyze Case)
2. Click on first image
3. **Expected:** User sees image + metadata
4. **Actual:** User sees image + metadata, but NO AI results
5. **Issue:** User may expect AI analysis to happen on-demand

**Validation:**
- Is this a bug or intended behavior?
- If intended: Add UI hint "Click 'Start Analysis' to analyze files"
- If bug: Implement on-demand analysis on first click

#### B. The "Cache Invalidation" Test
**Purpose:** Ensure ai_processed flag is set correctly

**Steps:**
1. Import 1 file
2. Run Analyze Case → ai_processed = 1
3. Check database: `SELECT ai_processed, ai_tags FROM evidence_files`
4. Verify: ai_processed = 1 AND ai_tags is NOT empty

**Risk:** If ai_processed = 1 but ai_tags = NULL → Data loss bug

#### C. The "Threading Race Condition" Test
**Purpose:** Verify extraction_loader ThreadPoolExecutor safety

**Steps:**
1. Import ZIP with 1,000 files
2. Monitor `extraction_loader.py:213-249` (ParallelFileProcessor)
3. Verify: All files inserted to DB without duplicates or missing entries
4. Check logs for threading errors

**Risk:** Race condition in database INSERTs

---

## CRITICAL FINDINGS & BUGS

### 🔴 Issue #1: No On-Demand AI Analysis
**Location:** `evidence_analyzer_window.py:745-747`

**Problem:**
```python
def on_file_selected(self, file_data: dict):
    """Handle file selection"""
    self.preview_widget.load_file(file_data)  # Just displays file
    # NO AI analysis triggered here!
```

**Impact:**
- User imports files
- User clicks on file expecting AI results
- User sees only basic metadata (dates, GPS, camera)
- **No AI tags, face count, or OCR text until batch analysis runs**

**Expected Behavior (User Perspective):**
- Click on file → AI analyzes it immediately (on-demand)
- Show loading spinner: "Analyzing with AI..."
- Display results when ready

**Actual Behavior:**
- Click on file → Display only basic metadata
- AI results only appear after running "Start Analysis" (batch mode)

**Fix Options:**
1. **Add on-demand analysis:** Modify `on_file_selected()` to check `ai_processed` flag
   - If 0: Trigger `analyzer.analyze_file(file_id)` in background thread
   - Show loading indicator in preview panel
   - Update preview when analysis completes
2. **Add UI indicator:** Change preview panel to show:
   - "⚠️ Not yet analyzed. Click 'Start Analysis' to process all files."
3. **Hybrid approach:** On-demand for clicked file, batch for all others

**Recommendation:** **Option 3 (Hybrid)** - Best user experience

---

### 🟡 Issue #2: Unclear User Flow
**Location:** General UX issue

**Problem:**
- No visual cue indicating files need analysis
- "Start Analysis" button not prominent enough
- User may not realize analysis is a separate step

**Impact:**
- Confusion: "Why don't I see AI results?"
- Poor discoverability of batch analysis feature

**Fix:**
- Add badge to file list: "10 unprocessed files"
- Change button text: "Start AI Analysis (10 files pending)"
- Show banner after import: "Files imported. Click 'Start Analysis' to detect faces and objects."

---

### 🟡 Issue #3: Temp File Cleanup
**Location:** `extraction_loader.py:132-164`

**Problem:**
```python
def extract_file_stream(self, file_path: str) -> bytes:
    with zipfile.ZipFile(self.zip_path, 'r') as zf:
        return zf.read(file_path)  # Returns bytes
```
**BUT** AI models need file paths, not bytes:
```python
# ai_analyzer.py:40-42
file_path = Path(file_data['file_path'])
# Models expect: image_classifier.classify_image(file_path)
```

**Risk:**
- Are files extracted to `temp/` during analysis?
- Are they cleaned up afterward?
- Could fill disk with temp files (1,000 images = ~5 GB)

**Validation Needed:**
- Test TC-17 (1,000 files) and monitor `temp/` directory size
- Check if cleanup happens after analysis

**Fix (if needed):**
- Add explicit cleanup in `ai_analyzer.py:260`:
  ```python
  finally:
      shutil.rmtree('temp/', ignore_errors=True)
  ```

---

### 🟢 Issue #4: High-Performance Loader Not Used
**Location:** `extraction_loader.py` vs. `file_scanner.py`

**Finding:**
- `extraction_loader.py` has sophisticated ZIP streaming logic
- `file_scanner.py` does basic directory scanning
- **Evidence Analyzer primarily imports from directories, not ZIPs**

**Question:**
- Is the high-performance loader ever used in production?
- Should it be integrated into the import flow for `.ufdr`, `.zip` archives?

**Recommendation:**
- If supporting forensic archives (UFED, Cellebrite), integrate extraction_loader into import flow
- If only supporting directory import, mark extraction_loader as "Future feature"

---

### 🟢 Issue #5: Error Handling for Missing AI Models
**Location:** `ai_service.py:49-93`

**Current Behavior:**
```python
try:
    self.face_detector = FaceDetector()
    self.logger.info("✓ Face detector loaded")
except Exception as e:
    self.logger.error(f"✗ Face detector failed to load: {e}")
    # Continues with self.face_detector = None
```

**Good:** App doesn't crash if model fails to load
**Risk:** Analysis runs but silently skips failed modules

**Validation:**
- TC-16: Verify app handles missing models gracefully
- Verify user is notified (not just logged)

**Improvement:**
- Show warning dialog on startup: "⚠️ Face detection unavailable. Install dlib to enable."

---

## VALIDATION CHECKLIST

### Pre-Validation Setup
- [ ] Create clean test environment
- [ ] Prepare sample data:
  - [ ] 10 images (various types: portraits, landscapes, documents)
  - [ ] 5 documents (PDFs, Word docs)
  - [ ] 3 videos
  - [ ] 1 ZIP archive with nested structure
- [ ] Install all dependencies (`pip install -r requirements.txt`)
- [ ] Verify AI models downloaded:
  - [ ] `yolov8n.pt` exists in project root
  - [ ] Tesseract installed (`tesseract --version`)
  - [ ] dlib installed (`python -c "import dlib"`)

### Execute Test Cases
- [ ] Run TC-01 through TC-18 in sequence
- [ ] Document results in "Actual Result" column
- [ ] Mark Pass/Fail
- [ ] For each failure:
  - [ ] Capture screenshot
  - [ ] Copy error message from logs
  - [ ] Note steps to reproduce

### Post-Validation
- [ ] Review logs (`logs/forenstiq_*.log`)
- [ ] Check database integrity:
  ```bash
  sqlite3 data/case_TEST-001.db "PRAGMA integrity_check;"
  ```
- [ ] Verify forensic integrity (TC-08)
- [ ] Generate final validation report

---

## NEXT STEPS

1. **Run Validation Tests** (Use test matrix above)
2. **Fix Critical Issues:**
   - Issue #1: Implement on-demand AI analysis
   - Issue #2: Improve UX/UI indicators
3. **Document Results:** Create `VALIDATION_REPORT.md`
4. **Performance Tuning:** Optimize AI analysis for large cases
5. **User Documentation:** Write user guide with clear workflow

---

## APPENDIX: Code References

### Key Files to Monitor
| File | Lines | What to Watch |
|------|-------|---------------|
| `evidence_analyzer_window.py` | 745-747 | File selection handler |
| `ai_analyzer.py` | 209-260 | Batch analysis loop |
| `file_repository.py` | 170-178 | `get_unprocessed_files()` query |
| `schema.sql` | 50 | `ai_processed` flag definition |
| `extraction_loader.py` | 88-131 | ZIP indexing performance |

### Database Queries for Debugging
```sql
-- Check analysis status
SELECT file_name, ai_processed, ai_tags, face_count
FROM evidence_files
WHERE case_id = 1;

-- Find unprocessed files
SELECT COUNT(*)
FROM evidence_files
WHERE ai_processed = 0;

-- Verify flagged files
SELECT file_name, flag_reason
FROM evidence_files
WHERE is_flagged = 1;

-- Audit trail
SELECT action, timestamp, details
FROM audit_log
WHERE case_id = 1
ORDER BY timestamp DESC;
```

---

**END OF ARCHITECTURE ANALYSIS**
