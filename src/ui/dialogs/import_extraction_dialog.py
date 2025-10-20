"""
Import Extraction File Dialog
High-performance dialog for loading forensic extraction files
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QLabel, QFileDialog, QProgressBar, QTextEdit,
                              QComboBox, QGroupBox, QCheckBox, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from datetime import datetime

from ...core.extraction_loader import ExtractionLoader, ExtractionFormat
from ...utils.logger import get_logger


class ImportWorker(QThread):
    """Background worker thread for importing extraction files"""

    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(dict)  # stats
    error = pyqtSignal(str)  # error message

    def __init__(self, extraction_path: Path, case_id: int, num_workers: int, fast_mode: bool):
        super().__init__()
        self.extraction_path = extraction_path
        self.case_id = case_id
        self.num_workers = num_workers
        self.fast_mode = fast_mode
        self.loader = ExtractionLoader()
        self.logger = get_logger()

    def run(self):
        """Run import in background thread"""
        try:
            def progress_callback(current, total, message):
                self.progress.emit(current, total, message)

            if self.fast_mode:
                # Fast mode: Index only, lazy loading
                stats = self.loader.load_extraction_fast(
                    extraction_path=self.extraction_path,
                    case_id=self.case_id,
                    progress_callback=progress_callback,
                    num_workers=self.num_workers
                )
            else:
                # Full extraction mode: Extract all files to disk
                stats = self.loader.load_extraction_with_full_extraction(
                    extraction_path=self.extraction_path,
                    case_id=self.case_id,
                    progress_callback=progress_callback
                )

            self.finished.emit(stats)

        except Exception as e:
            self.logger.error(f"Import error: {e}")
            self.error.emit(str(e))


class ImportExtractionDialog(QDialog):
    """
    Dialog for importing forensic extraction files

    Features:
    - Format auto-detection
    - Fast mode vs Full extraction mode
    - Parallel processing with configurable workers
    - Real-time progress updates
    - Performance statistics
    """

    def __init__(self, case_id: int, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.extraction_path = None
        self.worker = None
        self.logger = get_logger()

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Import Forensic Extraction File")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # File selection
        file_group = QGroupBox("Extraction File")
        file_layout = QVBoxLayout()

        file_select_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_file)
        file_select_layout.addWidget(self.file_label, 1)
        file_select_layout.addWidget(browse_btn)

        self.format_label = QLabel("Format: Unknown")
        self.format_label.setStyleSheet("color: #666; font-style: italic;")

        file_layout.addLayout(file_select_layout)
        file_layout.addWidget(self.format_label)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()

        # Fast mode checkbox
        self.fast_mode_checkbox = QCheckBox("Fast Mode (Recommended)")
        self.fast_mode_checkbox.setChecked(True)
        self.fast_mode_checkbox.setToolTip(
            "Fast Mode: Index files without extracting (10-100x faster)\n"
            "Files are accessed on-demand from the archive.\n\n"
            "Disable for full extraction to disk (slower but more compatible)."
        )
        options_layout.addWidget(self.fast_mode_checkbox)

        # Worker threads
        worker_layout = QHBoxLayout()
        worker_layout.addWidget(QLabel("Parallel Workers:"))
        self.workers_spin = QSpinBox()
        self.workers_spin.setMinimum(1)
        self.workers_spin.setMaximum(16)
        self.workers_spin.setValue(4)
        self.workers_spin.setToolTip("Number of parallel processing threads (4-8 recommended)")
        worker_layout.addWidget(self.workers_spin)
        worker_layout.addStretch()
        options_layout.addLayout(worker_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.status_label = QLabel("Ready to import")

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(QLabel("Log:"))
        progress_layout.addWidget(self.log_text)

        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.import_btn = QPushButton("Start Import")
        self.import_btn.clicked.connect(self.start_import)
        self.import_btn.setEnabled(False)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_file(self):
        """Open file browser"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Forensic Extraction File",
            "",
            "All Supported (*.zip *.ufdr *.ofb *.bin *.tar *.tar.gz *.ab *.clbx *.mfdb);;"
            "ZIP Archives (*.zip *.clbx);;"
            "Cellebrite Files (*.ufdr);;"
            "Oxygen Files (*.ofb);;"
            "AXIOM Files (*.mfdb);;"
            "Raw Images (*.bin *.dd *.raw);;"
            "Android Backups (*.ab);;"
            "TAR Archives (*.tar *.tar.gz);;"
            "All Files (*.*)"
        )

        if file_path:
            self.extraction_path = Path(file_path)
            self.file_label.setText(file_path)

            # Detect format
            format_type = ExtractionFormat.detect_format(self.extraction_path)
            self.format_label.setText(f"Format: {format_type}")

            # Enable import button
            self.import_btn.setEnabled(True)

            self.log(f"Selected file: {self.extraction_path.name}")
            self.log(f"Detected format: {format_type}")

    def start_import(self):
        """Start import process"""
        if not self.extraction_path:
            return

        # Disable controls
        self.import_btn.setEnabled(False)
        self.cancel_btn.setText("Close")

        self.log(f"Starting import at {datetime.now().strftime('%H:%M:%S')}")
        self.log(f"Fast Mode: {'Enabled' if self.fast_mode_checkbox.isChecked() else 'Disabled'}")
        self.log(f"Workers: {self.workers_spin.value()}")
        self.log("")

        # Start worker thread
        self.worker = ImportWorker(
            extraction_path=self.extraction_path,
            case_id=self.case_id,
            num_workers=self.workers_spin.value(),
            fast_mode=self.fast_mode_checkbox.isChecked()
        )

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.import_finished)
        self.worker.error.connect(self.import_error)

        self.worker.start()

    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status"""
        self.progress_bar.setValue(current)
        self.status_label.setText(message)

    def import_finished(self, stats: dict):
        """Import completed successfully"""
        elapsed = stats.get('elapsed_seconds', 0)
        total_files = stats.get('total', 0)
        processed = stats.get('processed', 0)
        errors = stats.get('errors', 0)
        files_per_sec = stats.get('files_per_second', 0)

        self.log("")
        self.log("=" * 50)
        self.log("IMPORT COMPLETE!")
        self.log("=" * 50)
        self.log(f"Total Files: {total_files}")
        self.log(f"Processed: {processed}")
        self.log(f"Errors: {errors}")
        self.log(f"Time Elapsed: {elapsed:.2f} seconds")
        self.log(f"Performance: {files_per_sec:.1f} files/second")
        self.log("")

        # File type breakdown
        self.log("File Types:")
        for key in ['images', 'videos', 'documents', 'databases']:
            if key in stats and stats[key] > 0:
                self.log(f"  {key.capitalize()}: {stats[key]}")

        self.status_label.setText(f"Complete! Imported {processed} files in {elapsed:.1f}s")
        self.progress_bar.setValue(100)

        # Show accept button
        self.cancel_btn.setText("Close")

    def import_error(self, error_msg: str):
        """Import failed"""
        self.log("")
        self.log("ERROR: Import failed!")
        self.log(f"  {error_msg}")

        self.status_label.setText(f"Error: {error_msg}")
        self.import_btn.setEnabled(True)
        self.import_btn.setText("Retry Import")

    def log(self, message: str):
        """Add message to log"""
        self.log_text.append(message)
