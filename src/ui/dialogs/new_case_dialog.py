"""
New Case Dialog for Forenstiq Lab Intelligence
Allows creation of new forensic investigation cases
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QLabel, QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime


class NewCaseDialog(QDialog):
    """
    Dialog for creating a new forensic investigation case

    Signals:
        case_created: Emitted when a case is successfully created
    """

    case_created = pyqtSignal(dict)  # Emits case data

    def __init__(self, db_manager, parent=None):
        """
        Initialize New Case Dialog

        Args:
            db_manager: DatabaseManager instance
            parent: Parent widget
        """
        super().__init__(parent)

        self.db_manager = db_manager
        self.case_data = None

        self.setWindowTitle("Create New Case - Forenstiq Lab Intelligence")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Create New Forensic Investigation Case")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Enter case details to begin investigation")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #9CA3AF; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Case Information Group
        case_group = QGroupBox("Case Information")
        case_layout = QFormLayout()

        # Case Name
        self.case_name_input = QLineEdit()
        self.case_name_input.setPlaceholderText("e.g., WhatsApp Fraud Investigation")
        case_layout.addRow("Case Name: *", self.case_name_input)

        # Case Number
        self.case_number_input = QLineEdit()
        self.case_number_input.setPlaceholderText("e.g., FIR-2025/CYB/12345")
        case_layout.addRow("Case Number: *", self.case_number_input)

        # Investigator Name
        self.investigator_input = QLineEdit()
        self.investigator_input.setPlaceholderText("e.g., Inspector Rajesh Kumar")
        case_layout.addRow("Investigator Name: *", self.investigator_input)

        # Agency/Lab Name
        self.agency_input = QLineEdit()
        self.agency_input.setPlaceholderText("e.g., Mumbai Cyber Crime Cell")
        self.agency_input.setText("Forenstiq Lab Intelligence")
        case_layout.addRow("Agency/Lab Name:", self.agency_input)

        # Case Type
        self.case_type_combo = QComboBox()
        self.case_type_combo.addItems([
            "Cybercrime Investigation",
            "Financial Fraud",
            "Digital Evidence Analysis",
            "Mobile Forensics",
            "Social Media Investigation",
            "Data Recovery",
            "Malware Analysis",
            "Other"
        ])
        case_layout.addRow("Case Type:", self.case_type_combo)

        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High", "Critical"])
        self.priority_combo.setCurrentText("Medium")
        case_layout.addRow("Priority:", self.priority_combo)

        case_group.setLayout(case_layout)
        layout.addWidget(case_group)

        # Description Group
        desc_group = QGroupBox("Case Description")
        desc_layout = QVBoxLayout()

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Enter case description, background, and objectives...\n\n"
            "Example:\n"
            "Investigation into alleged financial fraud involving UPI transactions. "
            "Suspect's mobile device seized for forensic analysis. "
            "Objective: Extract evidence of fraudulent transactions and communications."
        )
        self.description_input.setMinimumHeight(120)
        desc_layout.addWidget(self.description_input)

        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Required fields note
        required_note = QLabel("* Required fields")
        required_note.setStyleSheet("color: #EF4444; font-size: 10px; font-style: italic;")
        layout.addWidget(required_note)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)

        self.create_btn = QPushButton("Create Case")
        self.create_btn.setMinimumWidth(120)
        self.create_btn.setDefault(True)
        self.create_btn.clicked.connect(self.create_case)
        button_layout.addWidget(self.create_btn)

        layout.addLayout(button_layout)

    def apply_styles(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2D30;
                color: #E5E7EB;
            }
            QLabel {
                color: #E5E7EB;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3C3F41;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                color: #3B82F6;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3C3F41;
                color: #E5E7EB;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 2px solid #3B82F6;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #6B7280;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #E5E7EB;
                margin-right: 5px;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton#cancel_btn {
                background-color: #4B5563;
            }
            QPushButton#cancel_btn:hover {
                background-color: #6B7280;
            }
        """)

        self.cancel_btn.setObjectName("cancel_btn")

    def validate_input(self):
        """
        Validate user input

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check case name
        case_name = self.case_name_input.text().strip()
        if not case_name:
            return False, "Case name is required."

        # Check case number
        case_number = self.case_number_input.text().strip()
        if not case_number:
            return False, "Case number is required."

        # Check investigator name
        investigator = self.investigator_input.text().strip()
        if not investigator:
            return False, "Investigator name is required."

        # Check if case number already exists
        # Note: Duplicate check is handled by database UNIQUE constraint
        # If needed, can be added via case_repository.get_case_by_number()

        return True, ""

    def create_case(self):
        """Create the new case"""
        # Validate input
        is_valid, error_msg = self.validate_input()

        if not is_valid:
            QMessageBox.warning(
                self,
                "Validation Error",
                error_msg
            )
            return

        try:
            # Gather case data
            case_name = self.case_name_input.text().strip()
            case_number = self.case_number_input.text().strip()
            investigator = self.investigator_input.text().strip()
            agency = self.agency_input.text().strip() or "Forenstiq Lab Intelligence"
            case_type = self.case_type_combo.currentText()
            priority = self.priority_combo.currentText()
            description = self.description_input.toPlainText().strip()

            # Create case in database using CaseManager
            from ...core.case_manager import CaseManager

            case_manager = CaseManager()

            # Prepare case data
            case_data = {
                'case_name': case_name,
                'case_number': case_number,
                'investigator_name': investigator,
                'agency_name': agency,
                'status': 'open',
                'notes': f"Case Type: {case_type}\nPriority: {priority}\nDescription: {description}"
            }

            # Create case
            case_id = case_manager.create_case(case_data)

            if case_id:
                # Store case data
                self.case_data = {
                    'id': case_id,
                    'case_name': case_name,
                    'case_number': case_number,
                        'investigator_name': investigator,
                        'agency': agency,
                        'case_type': case_type,
                        'priority': priority,
                        'description': description,
                        'status': 'new'
                    }

                # Emit signal
                self.case_created.emit(self.case_data)

                # Show success message
                QMessageBox.information(
                    self,
                    "Case Created",
                    f"Case '{case_name}' has been created successfully!\n\n"
                    f"Case Number: {case_number}\n"
                    f"Investigator: {investigator}\n"
                    f"Type: {case_type}\n"
                    f"Priority: {priority}\n\n"
                    "You can now import evidence for this case."
                )

                # Accept dialog
                self.accept()
            else:
                QMessageBox.critical(
                    self,
                    "Database Error",
                    "Database manager not initialized.\nCannot create case."
                )

        except Exception as e:
            error_msg = str(e)

            # Check for duplicate case number
            if "UNIQUE constraint failed: cases.case_number" in error_msg:
                QMessageBox.warning(
                    self,
                    "Duplicate Case Number",
                    f"A case with the number '{case_number}' already exists.\n\n"
                    "Please use a different case number.\n\n"
                    "Tip: Each case must have a unique case number for forensic integrity."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error Creating Case",
                    f"An error occurred while creating the case:\n\n{error_msg}"
                )

            import traceback
            traceback.print_exc()

    def get_case_data(self):
        """
        Get the created case data

        Returns:
            dict: Case data dictionary or None
        """
        return self.case_data
