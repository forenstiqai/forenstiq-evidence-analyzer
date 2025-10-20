"""
Case Information Widget - Display case details and actions
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ...database.case_repository import CaseRepository
from ..styles import get_primary_button_style

class CaseInfoWidget(QWidget):
    """Widget displaying case information"""
    
    import_requested = pyqtSignal()
    analyze_requested = pyqtSignal()
    report_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.case_repo = CaseRepository()
        self.current_case = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("CASE INFORMATION")
        title.setObjectName("sectionHeader")
        title.setStyleSheet("font-weight: 600; font-size: 11px; color: #5F6368; text-transform: uppercase; letter-spacing: 0.5px; padding-bottom: 8px;")
        layout.addWidget(title)
        
        # Case details group
        details_group = QGroupBox()
        details_layout = QVBoxLayout()
        
        # Case number
        self.case_number_label = QLabel("No case open")
        self.case_number_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        details_layout.addWidget(self.case_number_label)
        
        # Case name
        self.case_name_label = QLabel("")
        self.case_name_label.setWordWrap(True)
        self.case_name_label.setStyleSheet("font-size: 12px; color: #333;")
        details_layout.addWidget(self.case_name_label)
        
        details_layout.addSpacing(10)
        
        # Investigator
        self.investigator_label = QLabel("")
        self.investigator_label.setStyleSheet("font-size: 11px; color: #666;")
        details_layout.addWidget(self.investigator_label)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 11px; color: #666;")
        details_layout.addWidget(self.status_label)
        
        details_layout.addSpacing(10)
        
        # Statistics
        stats_layout = QVBoxLayout()
        
        self.total_files_label = QLabel("Total Files: 0")
        self.total_files_label.setStyleSheet("font-size: 11px;")
        stats_layout.addWidget(self.total_files_label)
        
        self.flagged_label = QLabel("Flagged: 0")
        self.flagged_label.setStyleSheet("font-size: 11px; color: #FF6B00;")
        stats_layout.addWidget(self.flagged_label)
        
        self.analyzed_label = QLabel("Analyzed: 0 / 0")
        self.analyzed_label.setStyleSheet("font-size: 11px;")
        stats_layout.addWidget(self.analyzed_label)
        
        details_layout.addLayout(stats_layout)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        layout.addSpacing(20)
        
        # Action buttons
        actions_label = QLabel("ACTIONS")
        actions_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #666;")
        layout.addWidget(actions_label)
        
        self.import_button = QPushButton("📁  Import Files")
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.import_requested.emit)
        self.import_button.setStyleSheet(get_primary_button_style())
        self.import_button.setMinimumHeight(44)
        layout.addWidget(self.import_button)

        self.analyze_button = QPushButton("🔬  Start Analysis")
        self.analyze_button.setEnabled(False)
        self.analyze_button.clicked.connect(self.analyze_requested.emit)
        self.analyze_button.setStyleSheet(get_primary_button_style())
        self.analyze_button.setMinimumHeight(44)
        layout.addWidget(self.analyze_button)

        self.report_button = QPushButton("📄  Generate Report")
        self.report_button.setEnabled(False)
        self.report_button.clicked.connect(self.report_requested.emit)
        self.report_button.setStyleSheet(get_primary_button_style())
        self.report_button.setMinimumHeight(44)
        layout.addWidget(self.report_button)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMaximumWidth(300)
    
    def get_button_style(self):
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #F0F0F0;
                border: 1px solid #CCC;
                padding: 10px;
                text-align: left;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
            QPushButton:disabled {
                background-color: #F5F5F5;
                color: #999;
            }
        """
    
    def load_case(self, case_data):
        """Load case information"""
        self.current_case = case_data
        
        # Update labels
        self.case_number_label.setText(f"Case #{case_data.get('case_number', 'N/A')}")
        self.case_name_label.setText(case_data.get('case_name', ''))
        self.investigator_label.setText(f"Investigator: {case_data.get('investigator_name', 'N/A')}")
        
        status = case_data.get('status', 'open').upper()
        status_color = '#28A745' if status == 'OPEN' else '#DC3545'
        self.status_label.setText(f"Status: <span style='color:{status_color};'>{status}</span>")
        
        self.total_files_label.setText(f"Total Files: {case_data.get('total_files', 0)}")
        self.flagged_label.setText(f"Flagged: {case_data.get('total_flagged', 0)}")
        
        # Enable buttons
        self.import_button.setEnabled(True)
        self.analyze_button.setEnabled(True)
        self.report_button.setEnabled(True)
        
        # Refresh statistics
        self.refresh_case_info(case_data['case_id'])
    
    def refresh_case_info(self, case_id):
        """Refresh case statistics"""
        try:
            stats = self.case_repo.get_case_statistics(case_id)
            
            total = stats.get('total_files', 0)
            processed = stats.get('processed_files', 0)
            flagged = stats.get('flagged_files', 0)
            
            self.total_files_label.setText(f"Total Files: {total}")
            self.flagged_label.setText(f"Flagged: {flagged}")
            self.analyzed_label.setText(f"Analyzed: {processed} / {total}")
            
        except Exception as e:
            print(f"Error refreshing case info: {e}")
    
    def clear(self):
        """Clear case information"""
        self.current_case = None
        self.case_number_label.setText("No case open")
        self.case_name_label.setText("")
        self.investigator_label.setText("")
        self.status_label.setText("")
        self.total_files_label.setText("Total Files: 0")
        self.flagged_label.setText("Flagged: 0")
        self.analyzed_label.setText("Analyzed: 0 / 0")
        
        self.import_button.setEnabled(False)
        self.analyze_button.setEnabled(False)
        self.report_button.setEnabled(False)