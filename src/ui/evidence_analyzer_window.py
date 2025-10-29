"""
Main application window
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QAction, QStatusBar, QMessageBox, QFileDialog,
    QProgressDialog, QApplication
)
from .workers.analysis_worker import AnalysisWorker
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from datetime import datetime
from PyQt5.QtGui import QIcon
from pathlib import Path

from .dialogs.new_case_dialog import NewCaseDialog
from .dialogs.open_case_dialog import OpenCaseDialog
from .dialogs.suspect_photo_dialog import SuspectPhotoDialog
from .dialogs.report_options_dialog import ReportOptionsDialog
from .widgets.case_info_widget import CaseInfoWidget
from .widgets.file_list_widget import FileListWidget
from .widgets.preview_widget import PreviewWidget

from ..core.case_manager import CaseManager
from ..core.file_scanner import FileScanner
from ..utils.logger import get_logger
from ..ai.face_matcher import FaceMatcher

class EvidenceAnalyzerWindow(QMainWindow):
    """Evidence Analyzer Module - Image/Video Analysis Window"""

    # Signal to notify when returning to dashboard
    return_to_dashboard_signal = pyqtSignal()

    def __init__(self, device_type='computer'):
        super().__init__()

        self.logger = get_logger()
        self.case_manager = CaseManager()
        self.file_scanner = FileScanner()
        self.face_matcher = None  # Will be set when suspect photo is loaded

        self.current_case = None
        self.current_case_id = None
        self.device_type = device_type  # Store the device type

        # Map device types to display names (Police Seizure Categories)
        self.device_names = {
            'mobile': '📱 Mobile Devices',
            'storage': '💾 Storage Media',
            'computer': '💻 Computers',
            'cctv': '📹 CCTV/DVR Systems',
            'network': '🌐 Network Equipment',
            'fraud_device': '⚠️ Fraud Equipment'
        }

        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface"""
        # Set window title with device type
        device_display_name = self.device_names.get(self.device_type, '💻 Computer Tool')
        self.setWindowTitle(f"Forenstiq Evidence Analyzer v1.0 - {device_display_name}")
        self.setGeometry(100, 100, 1400, 900)

        # Create menu bar
        self.create_menu_bar()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Add module indicator header at the top
        self.create_module_header(main_layout)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Case info
        self.case_info_widget = CaseInfoWidget()
        self.case_info_widget.import_requested.connect(self.import_files)
        self.case_info_widget.analyze_requested.connect(self.analyze_case)
        self.case_info_widget.report_requested.connect(self.generate_report)
        splitter.addWidget(self.case_info_widget)
        
        # Middle panel - File list
        self.file_list_widget = FileListWidget()
        self.file_list_widget.file_selected.connect(self.on_file_selected)
        splitter.addWidget(self.file_list_widget)
        
        # Right panel - Preview
        self.preview_widget = PreviewWidget()
        splitter.addWidget(self.preview_widget)
        
        # Set splitter sizes (20% - 40% - 40%)
        splitter.setSizes([280, 560, 560])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.logger.info("Main window initialized")

    def create_module_header(self, layout):
        """Create module indicator header at the top"""
        from PyQt5.QtWidgets import QLabel, QFrame, QPushButton
        from PyQt5.QtGui import QFont

        # Header frame
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a5f, stop:1 #2c5282);
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)

        # Back button with arrow
        back_button = QPushButton("← Back to Dashboard")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
        """)
        back_button.clicked.connect(self.return_to_dashboard)
        header_layout.addWidget(back_button)

        header_layout.addSpacing(20)

        # Module name label
        device_display_name = self.device_names.get(self.device_type, '💻 Computer Tool')
        module_label = QLabel(f"Active Module: {device_display_name}")
        module_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)

        header_layout.addWidget(module_label)
        header_layout.addStretch()

        # Company badge
        company_label = QLabel("FORENSTIQ AI TECHNOLOGIES")
        company_label.setStyleSheet("""
            color: #60a5fa;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 2px;
            background: transparent;
        """)
        header_layout.addWidget(company_label)

        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_case_action = QAction("&New Case...", self)
        new_case_action.setShortcut("Ctrl+N")
        new_case_action.triggered.connect(self.new_case)
        file_menu.addAction(new_case_action)
        
        open_case_action = QAction("&Open Case...", self)
        open_case_action.setShortcut("Ctrl+O")
        open_case_action.triggered.connect(self.open_case)
        file_menu.addAction(open_case_action)
        
        file_menu.addSeparator()
        
        close_case_action = QAction("&Close Case", self)
        close_case_action.triggered.connect(self.close_case)
        file_menu.addAction(close_case_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Case menu
        case_menu = menubar.addMenu("&Case")
        
        import_action = QAction("&Import Files...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_files)
        case_menu.addAction(import_action)
        
        analyze_action = QAction("&Analyze All", self)
        analyze_action.setShortcut("Ctrl+A")
        analyze_action.triggered.connect(self.analyze_case)
        case_menu.addAction(analyze_action)
        
        case_menu.addSeparator()
        
        report_action = QAction("Generate &Report...", self)
        report_action.setShortcut("Ctrl+R")
        report_action.triggered.connect(self.generate_report)
        case_menu.addAction(report_action)

        case_menu.addSeparator()

        # Suspect face matching
        suspect_action = QAction("🔍 Find Suspect in Photos...", self)
        suspect_action.setShortcut("Ctrl+F")
        suspect_action.triggered.connect(self.load_suspect_photo)
        case_menu.addAction(suspect_action)

        case_menu.addSeparator()

        # Advanced search
        search_action = QAction("🔎 Advanced Search...", self)
        search_action.setShortcut("Ctrl+Shift+F")
        search_action.triggered.connect(self.show_advanced_search)
        case_menu.addAction(search_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_case(self):
        """Create new case"""
        dialog = NewCaseDialog(self)
        
        if dialog.exec_():
            case_data = dialog.get_case_data()
            
            try:
                case_id = self.case_manager.create_case(case_data)
                self.logger.info(f"Created new case: {case_id}")
                
                # Load the new case
                self.load_case(case_id)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Case '{case_data['case_name']}' created successfully!"
                )
                
            except Exception as e:
                self.logger.error(f"Error creating case: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create case: {str(e)}"
                )
    
    def open_case(self):
        """Open existing case"""
        dialog = OpenCaseDialog(self)
        
        if dialog.exec_():
            case_id = dialog.get_selected_case_id()
            if case_id:
                self.load_case(case_id)
    
    def load_case(self, case_id: int):
        """Load case into interface"""
        try:
            case = self.case_manager.open_case(case_id)
            
            if case:
                self.current_case = case
                self.current_case_id = case_id
                
                # Update UI
                self.case_info_widget.load_case(case)
                self.file_list_widget.load_case_files(case_id)
                
                self.status_bar.showMessage(f"Opened case: {case['case_name']}")
                self.logger.info(f"Loaded case: {case_id}")
            else:
                raise Exception("Case not found")
                
        except Exception as e:
            self.logger.error(f"Error loading case: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open case: {str(e)}"
            )
    
    def close_case(self):
        """Close current case"""
        if self.current_case:
            reply = QMessageBox.question(
                self,
                "Close Case",
                f"Close case '{self.current_case['case_name']}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.current_case = None
                self.current_case_id = None
                
                # Clear UI
                self.case_info_widget.clear()
                self.file_list_widget.clear()
                self.preview_widget.clear()
                
                self.status_bar.showMessage("Ready")
                self.logger.info("Case closed")
    
    def import_files(self):
        """Import evidence files"""
        if not self.current_case_id:
            QMessageBox.warning(
                self,
                "No Case Open",
                "Please open or create a case first."
            )
            return
        
        # Select directory
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Evidence Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.logger.info(f"Importing files from: {directory}")
            self.import_from_directory(Path(directory))
    
    def import_from_directory(self, directory: Path):
        """Import files from directory with progress dialog"""
        # Create progress dialog
        progress = QProgressDialog(
            "Scanning and importing files...",
            "Cancel",
            0,
            100,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Importing Evidence")
        
        def update_progress(current, total, filename):
            progress.setMaximum(total)
            progress.setValue(current)
            progress.setLabelText(f"Importing: {filename}")
            QApplication.processEvents()
        
        try:
            # Scan and import
            stats = self.file_scanner.scan_and_import(
                directory,
                self.current_case_id,
                progress_callback=update_progress
            )
            
            progress.close()
            
            # Show results with all file types
            message = f"Import completed successfully!\n\n"
            message += f"Total files scanned: {stats['total_files']}\n"
            message += f"Total imported: {stats['imported']}\n\n"
            message += f"File Types:\n"
            message += f"• Images: {stats['images']}\n"
            message += f"• Videos: {stats['videos']}\n"
            message += f"• Documents: {stats['documents']}\n"
            message += f"• Audio: {stats['audio']}\n"
            message += f"• Databases: {stats['databases']}\n"
            message += f"• Archives: {stats['archives']}\n"
            message += f"• Emails: {stats['emails']}\n"
            message += f"• Code files: {stats['code']}\n"
            message += f"• Executables: {stats['executables']}\n"
            message += f"• System files: {stats['system']}\n"
            message += f"• Other: {stats['other']}\n\n"
            message += f"Errors: {stats['errors']}"

            QMessageBox.information(
                self,
                "Import Complete",
                message
            )
            
            # Refresh file list
            self.file_list_widget.load_case_files(self.current_case_id)
            self.case_info_widget.refresh_case_info(self.current_case_id)
            
            self.logger.info(f"Imported {stats['imported']} files")
            
        except Exception as e:
            progress.close()
            self.logger.error(f"Error importing files: {e}")
            QMessageBox.critical(
                self,
                "Import Error",
                f"Failed to import files: {str(e)}"
            )
    
    def analyze_case(self):
        """Analyze all files in case"""
        if not self.current_case_id:
            QMessageBox.warning(
                self,
                "No Case Open",
                "Please open a case first."
            )
            return
        
        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Analyze Case",
            "This will analyze all unprocessed files using AI.\n"
            "This may take several minutes depending on the number of files.\n\n"
            "Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Create progress dialog
            self.progress_dialog = QProgressDialog(
                "Initializing AI modules...",
                "Cancel",
                0, 100,
                self
            )
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setWindowTitle("AI Analysis")
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.show()
            
            # Create and start worker
            self.analysis_worker = AnalysisWorker(self.current_case_id)
            self.analysis_worker.progress.connect(self.on_analysis_progress)
            self.analysis_worker.finished.connect(self.on_analysis_finished)
            self.analysis_worker.error.connect(self.on_analysis_error)
            
            # Handle cancel
            self.progress_dialog.canceled.connect(self.on_analysis_cancelled)
            
            self.analysis_worker.start()
            self.logger.info("Analysis worker started")
    
    def on_analysis_progress(self, current, total, filename):
        """Handle analysis progress update"""
        self.progress_dialog.setMaximum(total)
        self.progress_dialog.setValue(current)
        self.progress_dialog.setLabelText(f"Analyzing ({current}/{total}):\n{filename}")
        
    def on_analysis_finished(self, stats):
        """Handle analysis completion"""
        self.progress_dialog.close()
        
        QMessageBox.information(
            self,
            "Analysis Complete",
            f"AI analysis completed successfully!\n\n"
            f"Files processed: {stats['processed']}\n"
            f"Faces detected: {stats['faces_found']}\n"
            f"Files with text: {stats['text_found']}\n"
            f"Objects found: {stats['objects_found']}\n"
            f"Errors: {stats['errors']}"
        )
        
        # Refresh UI
        self.file_list_widget.load_case_files(self.current_case_id)
        self.case_info_widget.refresh_case_info(self.current_case_id)
        
        self.logger.info("Analysis completed successfully")
    
    def on_analysis_error(self, error_msg):
        """Handle analysis error"""
        self.progress_dialog.close()
        self.logger.error(f"Analysis error: {error_msg}")
        
        QMessageBox.critical(
            self,
            "Analysis Error",
            f"An error occurred during analysis:\n\n{error_msg}"
        )
    
    def on_analysis_cancelled(self):
        """Handle analysis cancellation"""
        if hasattr(self, 'analysis_worker'):
            self.analysis_worker.cancel()
            self.logger.info("Analysis cancelled by user")
    
    def generate_report(self):
        """Generate case report"""
        if not self.current_case_id:
            QMessageBox.warning(
                self,
                "No Case Open",
                "Please open a case first."
            )
            return

        # Get case statistics for the dialog
        from ..database.file_repository import FileRepository
        file_repo = FileRepository()
        all_files = file_repo.get_files_by_case(self.current_case_id)
        flagged_files = file_repo.get_files_by_case(self.current_case_id, flagged_only=True)

        # Show report options dialog
        options_dialog = ReportOptionsDialog(
            flagged_count=len(flagged_files),
            total_files=len(all_files),
            parent=self
        )

        if not options_dialog.exec_():
            return  # User cancelled

        flagged_only = options_dialog.is_flagged_only()
        report_type_str = "Flagged" if flagged_only else "Full"

        # Ask for save location
        from PyQt5.QtWidgets import QFileDialog

        default_filename = f"Report_{report_type_str}_{self.current_case['case_number']}_{datetime.now().strftime('%Y%m%d')}.pdf"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report",
            default_filename,
            "PDF Files (*.pdf)"
        )

        if file_path:
            try:
                from ..core.report_generator import ReportGenerator

                # Show progress
                progress = QProgressDialog(
                    f"Generating {report_type_str.lower()} report...",
                    None,
                    0, 0,
                    self
                )
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle("Report Generation")
                progress.show()

                # Generate report
                generator = ReportGenerator()
                success = generator.generate_report(
                    self.current_case_id,
                    Path(file_path),
                    flagged_only=flagged_only
                )
                
                progress.close()
                
                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Report generated successfully!\n\nSaved to:\n{file_path}"
                    )
                    
                    # Ask to open
                    reply = QMessageBox.question(
                        self,
                        "Open Report",
                        "Would you like to open the report now?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        import os
                        import platform
                        
                        if platform.system() == 'Darwin':  # macOS
                            os.system(f'open "{file_path}"')
                        elif platform.system() == 'Windows':
                            os.startfile(file_path)
                        else:  # Linux
                            os.system(f'xdg-open "{file_path}"')
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to generate report. Check logs for details."
                    )
                    
            except Exception as e:
                self.logger.error(f"Report generation error: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error generating report:\n{str(e)}"
                )
    
    def load_suspect_photo(self):
        """Load suspect photo for face matching"""
        if not self.current_case_id:
            QMessageBox.warning(
                self,
                "No Case Open",
                "Please open a case first."
            )
            return

        # Open suspect photo dialog
        dialog = SuspectPhotoDialog(self)
        dialog.suspect_loaded.connect(self.start_face_matching)

        if dialog.exec_():
            self.face_matcher = dialog.get_face_matcher()

    def start_face_matching(self, image_path: str, tolerance: float):
        """Start face matching process across all case images"""
        self.logger.info(f"Starting face matching with tolerance: {tolerance}")

        try:
            # Get all image files from current case
            from ..database.file_repository import FileRepository
            file_repo = FileRepository()
            all_files = file_repo.get_files_by_case(self.current_case_id)

            # Filter only images
            image_files = [f for f in all_files if f['file_type'] == 'image']

            if not image_files:
                QMessageBox.information(
                    self,
                    "No Images",
                    "No images found in the current case."
                )
                return

            self.logger.info(f"Found {len(image_files)} images to check")

            # Create progress dialog
            progress = QProgressDialog(
                "Searching for suspect in photos...",
                "Cancel",
                0,
                len(image_files),
                self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Face Matching")
            progress.show()

            # Perform face matching
            matched_files = []
            for idx, file_data in enumerate(image_files):
                if progress.wasCanceled():
                    break

                progress.setValue(idx + 1)
                progress.setLabelText(f"Checking: {file_data['file_name']}")
                QApplication.processEvents()

                # Match faces
                file_path = Path(file_data['file_path'])
                match_result = self.face_matcher.match_faces_in_image(file_path)

                if match_result['has_match']:
                    file_data['match_confidence'] = match_result['confidence']
                    file_data['match_count'] = match_result['match_count']
                    matched_files.append(file_data)
                    self.logger.info(
                        f"Match found in {file_data['file_name']}: "
                        f"{match_result['confidence']:.1f}% confidence"
                    )

            progress.close()

            # Show results
            if matched_files:
                # Sort by confidence
                matched_files.sort(key=lambda x: x['match_confidence'], reverse=True)

                # Show results message
                QMessageBox.information(
                    self,
                    "Face Matching Complete",
                    f"Found {len(matched_files)} photo(s) containing the suspect!\n\n"
                    f"The file list has been filtered to show only matches.\n"
                    f"Matches are sorted by confidence (highest first)."
                )

                # Filter file list to show only matches
                self.file_list_widget.show_suspect_matches(matched_files)

                self.status_bar.showMessage(
                    f"Showing {len(matched_files)} suspect matches"
                )

            else:
                QMessageBox.information(
                    self,
                    "No Matches Found",
                    f"No photos containing the suspect were found in this case.\n\n"
                    f"Checked {len(image_files)} images."
                )

        except Exception as e:
            self.logger.error(f"Error during face matching: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during face matching:\n\n{str(e)}"
            )

    def on_file_selected(self, file_data: dict):
        """Handle file selection"""
        self.preview_widget.load_file(file_data)

    def return_to_dashboard(self):
        """Return to the device selection dashboard"""
        # Check if there's an active case
        if self.current_case:
            reply = QMessageBox.question(
                self,
                "Return to Dashboard",
                f"A case is currently open: '{self.current_case['case_name']}'\n\n"
                f"Return to dashboard anyway?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Emit signal and close this window
        self.return_to_dashboard_signal.emit()
        self.close()

    def show_advanced_search(self):
        """Show advanced forensic search dialog"""
        if not self.current_case_id:
            QMessageBox.warning(
                self,
                "No Case Open",
                "Please open a case first."
            )
            return

        from .dialogs.advanced_search_dialog import AdvancedSearchDialog
        from ..core.forensic_search import ForensicSearchEngine

        dialog = AdvancedSearchDialog(self)
        dialog.search_requested.connect(self.perform_search)

        dialog.exec_()

    def perform_search(self, search_params: dict):
        """Perform forensic search with given parameters"""
        self.logger.info(f"Performing search with params: {search_params}")

        from ..core.forensic_search import ForensicSearchEngine
        from PyQt5.QtWidgets import QProgressDialog

        # Show progress
        progress = QProgressDialog(
            "Searching evidence files...",
            "Cancel",
            0, 0,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Searching...")
        progress.show()
        QApplication.processEvents()

        try:
            search_engine = ForensicSearchEngine()

            # Check if suspect photo provided
            if search_params.get('suspect_photo'):
                # Load suspect photo for face matching
                from ..ai.face_matcher import FaceMatcher
                face_matcher = FaceMatcher()
                face_matcher.load_suspect_face(Path(search_params['suspect_photo']))

                results = search_engine.search_with_face_match(
                    self.current_case_id,
                    search_params,
                    face_matcher
                )
            else:
                results = search_engine.search(self.current_case_id, search_params)

            progress.close()

            # Display results
            if results:
                QMessageBox.information(
                    self,
                    "Search Results",
                    f"Found {len(results)} matching files!\n\n"
                    f"The file list has been filtered to show search results.\n"
                    f"Files are sorted by relevance."
                )

                # Filter file list to show results
                self.file_list_widget.show_search_results(results)

                self.status_bar.showMessage(
                    f"Showing {len(results)} search results"
                )

                self.logger.info(f"Search complete: {len(results)} results")
            else:
                QMessageBox.information(
                    self,
                    "No Results",
                    "No files matched your search criteria.\n\n"
                    "Try:\n"
                    "• Broadening your search terms\n"
                    "• Checking different file types\n"
                    "• Adjusting the date range"
                )

        except Exception as e:
            progress.close()
            self.logger.error(f"Search error: {e}")
            QMessageBox.critical(
                self,
                "Search Error",
                f"An error occurred during search:\n\n{str(e)}"
            )

    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog will be implemented in the next phase."
        )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Forenstiq Evidence Analyzer",
            "<h2>Forenstiq Evidence Analyzer v1.0</h2>"
            "<p>AI-Powered Digital Forensic Analysis Tool</p>"
            "<p>Copyright © 2024 Forenstiq AI Technologies</p>"
            "<p><br>This software uses AI and machine learning to automatically<br>"
            "analyze digital evidence, detecting faces, objects, and text<br>"
            "to accelerate forensic investigations.</p>"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.current_case:
            reply = QMessageBox.question(
                self,
                "Exit",
                "A case is currently open. Exit anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()