"""
New Case Dialog - Create a new forensic case
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDateEdit, QPushButton,
    QLabel, QMessageBox
)
from PyQt5.QtCore import QDate, Qt
from datetime import datetime

class NewCaseDialog(QDialog):
    """Dialog for creating a new case"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.case_data = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Create New Case")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Case number (auto-generated, but can be edited)
        self.case_number_edit = QLineEdit()
        self.case_number_edit.setPlaceholderText("Auto-generated if left blank")
        form_layout.addRow("Case Number:", self.case_number_edit)
        
        # Case name (required)
        self.case_name_edit = QLineEdit()
        self.case_name_edit.setPlaceholderText("e.g., Phone Seizure - John Doe")
        form_layout.addRow("Case Name*:", self.case_name_edit)
        
        # Investigator name
        self.investigator_edit = QLineEdit()
        self.investigator_edit.setPlaceholderText("Your name")
        form_layout.addRow("Investigator:", self.investigator_edit)
        
        # Agency name
        self.agency_edit = QLineEdit()
        self.agency_edit.setPlaceholderText("e.g., State Forensic Laboratory")
        form_layout.addRow("Agency:", self.agency_edit)
        
        # Incident date
        self.incident_date_edit = QDateEdit()
        self.incident_date_edit.setDate(QDate.currentDate())
        self.incident_date_edit.setCalendarPopup(True)
        form_layout.addRow("Incident Date:", self.incident_date_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Case description, background information...")
        self.notes_edit.setMaximumHeight(100)
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # Required field note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        create_button = QPushButton("Create Case")
        create_button.setDefault(True)
        create_button.clicked.connect(self.validate_and_accept)
        create_button.setStyleSheet("""
            QPushButton {
                background-color: #0066FF;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052CC;
            }
        """)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        """Validate form and accept dialog"""
        # Check required fields
        if not self.case_name_edit.text().strip():
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a case name."
            )
            self.case_name_edit.setFocus()
            return
        
        # Collect data
        self.case_data = {
            'case_number': self.case_number_edit.text().strip(),
            'case_name': self.case_name_edit.text().strip(),
            'investigator_name': self.investigator_edit.text().strip(),
            'agency_name': self.agency_edit.text().strip(),
            'incident_date': self.incident_date_edit.date().toString('yyyy-MM-dd'),
            'notes': self.notes_edit.toPlainText().strip()
        }
        
        self.accept()
    
    def get_case_data(self):
        """Get collected case data"""
        return self.case_data