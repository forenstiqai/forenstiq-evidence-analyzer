# Forenstiq Evidence Analyzer - Bug Fix Implementation Plan

**Generated:** 2025-10-28
**Priority:** CRITICAL - Implements on-demand AI analysis and UX improvements

---

## Overview

This document provides step-by-step implementation instructions for fixing the identified issues in the Forenstiq Evidence Analyzer. All fixes are designed to be:
- **Non-breaking:** Existing functionality preserved
- **Testable:** Each fix has validation steps
- **Reversible:** Changes can be rolled back if needed

---

## 🔴 Fix #1: Implement On-Demand AI Analysis

### Problem Statement
When users click on a file, NO AI analysis happens. Users must manually run "Start Analysis" batch operation to see AI results (faces, objects, OCR).

### Impact
- **User Confusion:** "Why don't I see AI results?"
- **Poor UX:** Extra step required (not intuitive)
- **Expectation Mismatch:** Users expect immediate results on click

### Solution Design

**Hybrid Approach:**
- **On-demand:** When user clicks unprocessed file → Analyze immediately
- **Batch:** Keep existing "Start Analysis" button for processing all files
- **Cache:** If file already processed (ai_processed=1) → Show cached results

**Flow Diagram:**
```
User clicks on file
  ↓
Check: ai_processed flag?
  ├─ 0 (unprocessed) → Trigger on-demand analysis
  │                    └─ Show spinner: "Analyzing with AI..."
  │                    └─ Run AIAnalyzer.analyze_file()
  │                    └─ Update preview when done
  └─ 1 (processed) → Display cached results (instant)
```

### Implementation Steps

#### Step 1: Create On-Demand Analysis Worker
**File:** `src/ui/workers/single_file_analysis_worker.py` (NEW FILE)

```python
"""
Single File Analysis Worker - For on-demand AI analysis
"""
from PyQt5.QtCore import QThread, pyqtSignal
from ...core.ai_analyzer import AIAnalyzer
from ...core.ai_service import AIService

class SingleFileAnalysisWorker(QThread):
    """Worker thread for analyzing a single file on-demand"""

    # Signals
    finished = pyqtSignal(dict)  # file_data with AI results
    error = pyqtSignal(str)  # error message

    def __init__(self, file_id: int, ai_service: AIService):
        super().__init__()
        self.file_id = file_id
        self.ai_service = ai_service
        self.analyzer = None

    def run(self):
        """Run analysis in background"""
        try:
            # Initialize analyzer with shared AI service
            self.analyzer = AIAnalyzer(self.ai_service)

            # Analyze single file
            results = self.analyzer.analyze_file(self.file_id)

            # Get updated file data from database
            from ...database.file_repository import FileRepository
            file_repo = FileRepository()
            updated_file = file_repo.get_file(self.file_id)

            if updated_file:
                self.finished.emit(updated_file)
            else:
                self.error.emit(f"File {self.file_id} not found after analysis")

        except Exception as e:
            self.error.emit(str(e))
```

**Validation:**
- [ ] File created at correct path
- [ ] Imports work (no syntax errors)
- [ ] Worker can be instantiated

---

#### Step 2: Modify Evidence Analyzer Window
**File:** `src/ui/evidence_analyzer_window.py`

**Changes:**

**2.1: Add import at top of file (around line 9):**
```python
from .workers.analysis_worker import AnalysisWorker
from .workers.single_file_analysis_worker import SingleFileAnalysisWorker  # NEW
```

**2.2: Add instance variable in __init__ (around line 44):**
```python
self.current_case = None
self.current_case_id = None
self.device_type = device_type
self.single_file_worker = None  # NEW: Track on-demand analysis worker
```

**2.3: Replace on_file_selected() method (around line 745):**

**OLD CODE:**
```python
def on_file_selected(self, file_data: dict):
    """Handle file selection"""
    self.preview_widget.load_file(file_data)
```

**NEW CODE:**
```python
def on_file_selected(self, file_data: dict):
    """Handle file selection with on-demand AI analysis"""
    # Check if file needs AI analysis
    if file_data.get('ai_processed') == 0:
        # Show loading state in preview
        self.preview_widget.show_loading_state(file_data)

        # Start on-demand analysis
        self.start_single_file_analysis(file_data)
    else:
        # File already analyzed - show cached results
        self.preview_widget.load_file(file_data)

def start_single_file_analysis(self, file_data: dict):
    """Start on-demand analysis for a single file"""
    file_id = file_data['file_id']

    # Create worker thread
    self.single_file_worker = SingleFileAnalysisWorker(file_id, self.ai_service)

    # Connect signals
    self.single_file_worker.finished.connect(self.on_single_file_analysis_finished)
    self.single_file_worker.error.connect(self.on_single_file_analysis_error)

    # Start analysis
    self.single_file_worker.start()
    self.logger.info(f"Started on-demand analysis for file_id={file_id}")

def on_single_file_analysis_finished(self, updated_file_data: dict):
    """Handle completion of single file analysis"""
    # Update preview with AI results
    self.preview_widget.load_file(updated_file_data)

    # Refresh file list to show updated status
    self.file_list_widget.refresh_file(updated_file_data)

    # Update status bar
    self.status_bar.showMessage(f"Analysis complete: {updated_file_data['file_name']}")

    self.logger.info(f"On-demand analysis complete for {updated_file_data['file_name']}")

def on_single_file_analysis_error(self, error_msg: str):
    """Handle single file analysis error"""
    self.logger.error(f"On-demand analysis error: {error_msg}")

    # Show error in preview panel
    self.preview_widget.show_error_state(error_msg)

    # Show error dialog
    QMessageBox.warning(
        self,
        "Analysis Error",
        f"Failed to analyze file:\n\n{error_msg}"
    )
```

**Validation:**
- [ ] Code compiles (no syntax errors)
- [ ] Methods properly indented
- [ ] Signals connected correctly

---

#### Step 3: Modify Preview Widget
**File:** `src/ui/widgets/preview_widget.py`

**Add these new methods (after line 237):**

```python
def show_loading_state(self, file_data: dict):
    """Show loading state while AI analysis is running"""
    # Display image if available
    if file_data.get('file_type') == 'image':
        file_path = Path(file_data.get('file_path'))
        if file_path.exists():
            try:
                pil_image = load_image_pil(file_path)
                if pil_image:
                    display_size = (600, 600)
                    pil_image.thumbnail(display_size)
                    pixmap = pil_to_pixmap(pil_image)
                    self.image_label.setPixmap(pixmap)
                    self.image_label.setAlignment(Qt.AlignCenter)
            except:
                pass

    # Show loading message in metadata
    loading_text = f"Filename: {file_data.get('file_name', 'N/A')}\n\n"
    loading_text += "=== AI ANALYSIS IN PROGRESS ===\n\n"
    loading_text += "🔄 Analyzing with AI...\n\n"
    loading_text += "• Detecting faces\n"
    loading_text += "• Identifying objects\n"
    loading_text += "• Extracting text (OCR)\n"
    loading_text += "• Classifying image\n\n"
    loading_text += "This may take 5-10 seconds...\n"

    self.metadata_text.setPlainText(loading_text)

    # Disable buttons during analysis
    self.flag_button.setEnabled(False)
    self.note_button.setEnabled(False)

def show_error_state(self, error_msg: str):
    """Show error state when analysis fails"""
    error_text = "=== ANALYSIS ERROR ===\n\n"
    error_text += f"❌ {error_msg}\n\n"
    error_text += "The file could not be analyzed. Please check:\n"
    error_text += "• File is not corrupted\n"
    error_text += "• AI models are loaded correctly\n"
    error_text += "• Sufficient disk space available\n\n"
    error_text += "Check logs for more details."

    self.metadata_text.setPlainText(error_text)
```

**Validation:**
- [ ] Methods added after line 237
- [ ] Indentation correct
- [ ] Loading UI displays properly

---

#### Step 4: Modify File List Widget
**File:** `src/ui/widgets/file_list_widget.py`

**Add refresh method (need to check current structure first):**

```python
def refresh_file(self, updated_file_data: dict):
    """Refresh a single file in the list after analysis"""
    file_id = updated_file_data['file_id']

    # Find the file in the list and update it
    for row in range(self.file_list.rowCount()):
        item = self.file_list.item(row, 0)
        if item and item.data(Qt.UserRole) == file_id:
            # Update the stored data
            item.setData(Qt.UserRole + 1, updated_file_data)

            # Update visual indicator (if showing processing status)
            # Could add icon or color change here
            break
```

---

### Testing Steps

**Test 1: On-Demand Analysis (Unprocessed File)**
1. Import 5 image files (do NOT run batch analysis)
2. Click on first image
3. **Expected:**
   - Preview shows image immediately
   - Metadata shows: "🔄 Analyzing with AI..."
   - After 5-10 seconds: AI results appear
   - Shows: Tags, confidence, face count, OCR text
4. Click on different file, then back to first file
5. **Expected:**
   - First file now shows results INSTANTLY (cached)

**Test 2: Cached Results (Processed File)**
1. Run batch "Start Analysis"
2. Click on any file
3. **Expected:**
   - Results appear instantly (< 100ms)
   - No "Analyzing..." message

**Test 3: Error Handling**
1. Delete `yolov8n.pt` model file
2. Restart app
3. Click on unprocessed file
4. **Expected:**
   - Analysis runs but object detection skips
   - No crash
   - Shows partial results

---

## 🟡 Fix #2: Add UI Indicators for Unprocessed Files

### Problem Statement
Users don't know files need analysis. No visual indicator showing "X unprocessed files".

### Solution Design

**Add 3 indicators:**
1. **Badge on "Start Analysis" button:** "Start Analysis (10 pending)"
2. **Banner after import:** "⚠️ Files imported. Click 'Start Analysis' to detect faces and objects."
3. **Status bar counter:** "Loaded: 100 files | Analyzed: 45 | Pending: 55"

### Implementation Steps

#### Step 1: Add Pending Count Method
**File:** `src/database/file_repository.py`

**Add method after line 178:**
```python
def get_unprocessed_count(self, case_id: int) -> int:
    """Get count of files that haven't been processed by AI yet"""
    query = '''
        SELECT COUNT(*)
        FROM evidence_files
        WHERE case_id = ? AND ai_processed = 0
    '''
    results = self.db.execute_query(query, (case_id,))

    if results:
        return results[0][0]
    return 0
```

---

#### Step 2: Update Case Info Widget
**File:** `src/ui/widgets/case_info_widget.py`

**Find the "Start Analysis" button creation and modify:**

```python
# OLD
self.analyze_button = QPushButton("Start Analysis")

# NEW
self.analyze_button = QPushButton("Start Analysis")
# Will be updated dynamically with pending count
```

**Add method to update button text:**
```python
def update_analysis_button(self, pending_count: int):
    """Update analysis button text with pending count"""
    if pending_count > 0:
        self.analyze_button.setText(f"⚡ Start Analysis ({pending_count} pending)")
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
    else:
        self.analyze_button.setText("✓ All Files Analyzed")
        self.analyze_button.setEnabled(False)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
        """)
```

---

#### Step 3: Add Import Success Banner
**File:** `src/ui/evidence_analyzer_window.py`

**Modify import_from_directory() method (around line 395):**

**After showing import complete dialog, add:**
```python
# Show results
QMessageBox.information(
    self,
    "Import Complete",
    message
)

# NEW: Check if files need analysis
from ..database.file_repository import FileRepository
file_repo = FileRepository()
pending_count = file_repo.get_unprocessed_count(self.current_case_id)

if pending_count > 0:
    # Show analysis prompt banner
    reply = QMessageBox.question(
        self,
        "AI Analysis Available",
        f"📊 {stats['imported']} files imported successfully!\n\n"
        f"⚡ {pending_count} files are ready for AI analysis.\n\n"
        f"Would you like to start AI analysis now?\n"
        f"(This will detect faces, objects, and extract text)",
        QMessageBox.Yes | QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        # Auto-start analysis
        self.analyze_case()

# Refresh file list
self.file_list_widget.load_case_files(self.current_case_id)
self.case_info_widget.refresh_case_info(self.current_case_id)

# NEW: Update analysis button with pending count
self.case_info_widget.update_analysis_button(pending_count)
```

---

#### Step 4: Add Status Bar Counter
**File:** `src/ui/evidence_analyzer_window.py`

**Add new method:**
```python
def update_status_bar_stats(self):
    """Update status bar with file statistics"""
    if not self.current_case_id:
        return

    from ..database.file_repository import FileRepository
    file_repo = FileRepository()

    all_files = file_repo.get_files_by_case(self.current_case_id)
    total = len(all_files)

    processed_count = sum(1 for f in all_files if f['ai_processed'] == 1)
    pending_count = total - processed_count

    status_text = f"📁 Files: {total} | ✓ Analyzed: {processed_count} | ⏳ Pending: {pending_count}"
    self.status_bar.showMessage(status_text)
```

**Call this method:**
- After import completes
- After analysis completes
- After on-demand analysis completes
- When case opens

---

### Testing Steps

**Test 1: Import Banner**
1. Import files
2. **Expected:** Dialog asks "Would you like to start AI analysis now?"
3. Click No
4. **Expected:** Button shows "⚡ Start Analysis (10 pending)" in orange

**Test 2: Status Bar**
1. Open case with mixed files (some analyzed, some not)
2. **Expected:** Status bar shows "📁 Files: 100 | ✓ Analyzed: 45 | ⏳ Pending: 55"

**Test 3: All Analyzed State**
1. Run analysis until all files processed
2. **Expected:** Button shows "✓ All Files Analyzed" (green, disabled)

---

## 🟡 Fix #3: Add Temp File Cleanup Mechanism

### Problem Statement
AI models need file paths (not bytes). Files may be extracted to `temp/` during analysis, potentially filling disk space.

### Solution Design

**Two-part fix:**
1. **Explicit cleanup after analysis:** Delete temp files after each file analyzed
2. **Startup cleanup:** Clear temp folder on app start (in case of crash)
3. **Context manager:** Use try/finally to ensure cleanup happens

### Implementation Steps

#### Step 1: Add Cleanup Utilities
**File:** `src/utils/file_utils.py`

**Add these functions:**
```python
import shutil
from pathlib import Path

def cleanup_temp_directory():
    """Clean up temporary extraction directory"""
    temp_dir = Path('temp')

    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            return True
        except Exception as e:
            from .logger import get_logger
            logger = get_logger()
            logger.error(f"Failed to clean temp directory: {e}")
            return False
    return True

def get_temp_file_path(filename: str) -> Path:
    """Get a temporary file path for extraction"""
    temp_dir = Path('temp')
    temp_dir.mkdir(exist_ok=True)

    # Create unique subdirectory using timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    extract_dir = temp_dir / timestamp
    extract_dir.mkdir(exist_ok=True)

    return extract_dir / filename
```

---

#### Step 2: Modify AI Analyzer for Cleanup
**File:** `src/core/ai_analyzer.py`

**Modify analyze_file() method (around line 28):**

```python
def analyze_file(self, file_id: int) -> Dict:
    """Analyze single file with all AI modules"""
    temp_files_created = []  # Track temp files for cleanup

    try:
        # Get file info
        file_data = self.file_repo.get_file(file_id)
        if not file_data:
            raise ValueError(f"File {file_id} not found")

        file_path = Path(file_data['file_path'])
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = file_data['file_type']
        self.logger.info(f"Analyzing {file_type} file: {file_path.name}")

        results = {
            'file_id': file_id,
            'ai_tags': [],
            'ai_confidence': 0.0,
            'ocr_text': '',
            'face_count': 0,
            'objects_detected': []
        }

        # Route to appropriate analyzer based on file type
        if file_type == 'image':
            self._analyze_image(file_path, results)
        elif file_type == 'video':
            self._analyze_video(file_path, results)
        elif file_type == 'document':
            self._analyze_document(file_path, results)
        # ... rest of routing logic

        # Update database
        analysis_data = {
            'ai_tags': json.dumps(results['ai_tags']),
            'ai_confidence': results['ai_confidence'],
            'ocr_text': results['ocr_text'],
            'face_count': results['face_count']
        }

        self.file_repo.update_ai_analysis(file_id, analysis_data)

        self.logger.info(f"✓ Analysis complete for {file_path.name}")

        return results

    finally:
        # CLEANUP: Remove any temporary files created during analysis
        for temp_file in temp_files_created:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    self.logger.debug(f"Cleaned up temp file: {temp_file}")
            except Exception as e:
                self.logger.warning(f"Failed to clean temp file {temp_file}: {e}")
```

---

#### Step 3: Add Startup Cleanup
**File:** `src/main.py`

**Modify setup_application() function (around line 90):**

```python
def setup_application():
    """Setup application directories and configuration"""

    # Create necessary directories
    directories = [
        'data',
        'logs',
        'reports',
        'evidence_storage',
        'temp'
    ]

    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

    # NEW: Clean up temp directory from previous session
    from src.utils.file_utils import cleanup_temp_directory
    cleanup_temp_directory()

    # Initialize logging
    logger = ForenstiqLogger.get_logger()
    logger.info("=" * 60)
    logger.info("Forenstiq Evidence Analyzer Starting")
    logger.info("Temp directory cleaned")
    logger.info("=" * 60)

    # ... rest of setup
```

---

### Testing Steps

**Test 1: Temp Cleanup After Analysis**
1. Import 10 files
2. Monitor `temp/` directory size: `du -sh temp/`
3. Run analysis
4. **Expected:** Temp dir size stays < 50 MB during analysis
5. After analysis: Temp dir is empty or minimal

**Test 2: Startup Cleanup**
1. Kill app during analysis (force quit)
2. Check `temp/` has files
3. Restart app
4. **Expected:** Startup log shows "Temp directory cleaned"
5. `temp/` directory is empty

**Test 3: Large File Handling**
1. Import 1,000 files
2. Run analysis
3. Monitor disk space: `df -h`
4. **Expected:** No disk space errors

---

## 🟢 Fix #4: Integration Testing

### Complete End-to-End Test

**Scenario:** Full workflow with all fixes enabled

1. **Launch App**
   - ✓ Temp directory cleaned
   - ✓ AI models loaded
   - ✓ Status bar shows "Ready"

2. **Create Case**
   - ✓ Case created in database
   - ✓ Folders created

3. **Import 20 Files**
   - ✓ Import completes
   - ✓ Dialog asks: "Would you like to start AI analysis now?"
   - ✓ Click "No"
   - ✓ Button shows: "⚡ Start Analysis (20 pending)"
   - ✓ Status bar: "📁 Files: 20 | ✓ Analyzed: 0 | ⏳ Pending: 20"

4. **Click on File #1 (On-Demand Analysis)**
   - ✓ Image displays immediately
   - ✓ Metadata shows: "🔄 Analyzing with AI..."
   - ✓ After 5-10 sec: AI results appear
   - ✓ Status bar updates: "📁 Files: 20 | ✓ Analyzed: 1 | ⏳ Pending: 19"
   - ✓ Button updates: "⚡ Start Analysis (19 pending)"

5. **Click on File #2**
   - ✓ Same on-demand analysis behavior
   - ✓ Status: "Analyzed: 2 | Pending: 18"

6. **Click Back on File #1**
   - ✓ Results appear INSTANTLY (< 100ms)
   - ✓ No "Analyzing..." message

7. **Run Batch "Start Analysis"**
   - ✓ Progress dialog: "Analyzing (1/18): file003.jpg"
   - ✓ All remaining files processed
   - ✓ Button changes to: "✓ All Files Analyzed" (green, disabled)
   - ✓ Status: "📁 Files: 20 | ✓ Analyzed: 20 | ⏳ Pending: 0"

8. **Generate Report**
   - ✓ Report includes all 20 files with AI results
   - ✓ PDF opens correctly

9. **Check Disk Usage**
   - ✓ `temp/` directory is empty
   - ✓ No temp file leaks

---

## Implementation Order

### Phase 1: Core Functionality (Do First)
1. ✅ Create SingleFileAnalysisWorker
2. ✅ Modify evidence_analyzer_window.py (on_file_selected)
3. ✅ Modify preview_widget.py (loading states)
4. ✅ Test on-demand analysis (TC-04, TC-06)

### Phase 2: UI Improvements
5. ✅ Add get_unprocessed_count() to file_repository.py
6. ✅ Add update_analysis_button() to case_info_widget.py
7. ✅ Add import banner prompt
8. ✅ Add status bar counter
9. ✅ Test UI indicators

### Phase 3: Cleanup & Polish
10. ✅ Add cleanup_temp_directory() to file_utils.py
11. ✅ Modify ai_analyzer.py for cleanup
12. ✅ Add startup cleanup to main.py
13. ✅ Test temp file cleanup

### Phase 4: Integration Testing
14. ✅ Run complete end-to-end test
15. ✅ Run TC-01 through TC-18
16. ✅ Document results

---

## Rollback Plan

If any fix causes issues:

### Rollback Fix #1 (On-Demand Analysis)
```bash
# Restore original on_file_selected method
git diff src/ui/evidence_analyzer_window.py
# Manually revert to original 3-line version
# Delete SingleFileAnalysisWorker file
```

### Rollback Fix #2 (UI Indicators)
- Remove new methods from case_info_widget.py
- Remove banner prompt from import flow
- Restore original status bar messages

### Rollback Fix #3 (Cleanup)
- Remove cleanup calls
- Temp files will accumulate but won't break functionality

---

## Success Criteria

### Fix #1 Success:
- [ ] User clicks unprocessed file → AI analysis starts automatically
- [ ] Loading indicator shows during analysis
- [ ] Results display when analysis completes
- [ ] Clicking analyzed file shows instant cached results
- [ ] No crashes or hangs

### Fix #2 Success:
- [ ] Button shows pending count: "⚡ Start Analysis (X pending)"
- [ ] Status bar shows file statistics
- [ ] Import prompts user to start analysis
- [ ] All indicators update in real-time

### Fix #3 Success:
- [ ] Temp directory stays small during analysis (< 50 MB)
- [ ] Temp cleaned on startup
- [ ] No disk space errors with 1,000+ files

---

## Post-Implementation Checklist

- [ ] All code changes committed to version control
- [ ] Test results documented
- [ ] User documentation updated
- [ ] CHANGELOG.md updated
- [ ] Performance benchmarks recorded
- [ ] Known issues documented

---

**END OF BUG FIX PLAN**
