"""
Advanced Search Dialog - Search evidence by person, date, keywords
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QDateEdit, QCheckBox, QTextEdit,
    QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from pathlib import Path


class AdvancedSearchDialog(QDialog):
    """Advanced forensic search with multiple filters"""

    search_requested = pyqtSignal(dict)  # Emit search parameters

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Advanced Forensic Search")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header
        header = QLabel("Advanced Evidence Search")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #007ACC; padding: 10px;")
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "Search across all evidence files including contacts, messages, "
            "emails, documents, images, and databases."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 5px 10px;")
        layout.addWidget(desc)

        # Search by Person
        person_group = QGroupBox("👤 Search by Person/Contact")
        person_layout = QVBoxLayout()

        person_label = QLabel("Person Name (e.g., 'Rohith'):")
        self.person_input = QLineEdit()
        self.person_input.setPlaceholderText("Enter name to search for...")
        self.person_enabled = QCheckBox("Enable person search")
        self.person_enabled.setChecked(True)

        person_layout.addWidget(self.person_enabled)
        person_layout.addWidget(person_label)
        person_layout.addWidget(self.person_input)
        person_group.setLayout(person_layout)
        layout.addWidget(person_group)

        # Search by Date
        date_group = QGroupBox("📅 Search by Date/Time")
        date_layout = QVBoxLayout()

        self.date_enabled = QCheckBox("Enable date filtering")
        self.date_enabled.setChecked(False)
        date_layout.addWidget(self.date_enabled)

        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setCalendarPopup(True)
        date_range_layout.addWidget(self.date_from)

        date_range_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        date_range_layout.addWidget(self.date_to)

        date_layout.addLayout(date_range_layout)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # Search by Keywords
        keyword_group = QGroupBox("🔑 Search by Keywords")
        keyword_layout = QVBoxLayout()

        self.keyword_enabled = QCheckBox("Enable keyword search")
        self.keyword_enabled.setChecked(False)
        keyword_layout.addWidget(self.keyword_enabled)

        keyword_label = QLabel("Keywords (comma-separated):")
        self.keyword_input = QTextEdit()
        self.keyword_input.setPlaceholderText("e.g., money, transfer, payment, bank, account")
        self.keyword_input.setMaximumHeight(80)

        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        keyword_group.setLayout(keyword_layout)
        layout.addWidget(keyword_group)

        # Search Scope
        scope_group = QGroupBox("📁 Search Scope")
        scope_layout = QVBoxLayout()

        self.search_all = QCheckBox("Search in all file types")
        self.search_all.setChecked(True)
        self.search_all.toggled.connect(self.toggle_file_types)
        scope_layout.addWidget(self.search_all)

        # File type checkboxes
        file_types_layout = QVBoxLayout()
        self.file_type_checks = {}
        file_types = [
            ('Images', 'image'),
            ('Videos', 'video'),
            ('Documents', 'document'),
            ('Text Files', 'code'),
            ('Databases', 'database'),
            ('Emails', 'email'),
            ('Audio', 'audio'),
        ]

        for label, ftype in file_types:
            cb = QCheckBox(label)
            cb.setChecked(False)
            cb.setEnabled(False)
            self.file_type_checks[ftype] = cb
            file_types_layout.addWidget(cb)

        scope_layout.addLayout(file_types_layout)
        scope_group.setLayout(scope_layout)
        layout.addWidget(scope_group)

        # Upload Suspect Photo
        photo_group = QGroupBox("📸 Upload Suspect Photo (Optional)")
        photo_layout = QVBoxLayout()

        photo_desc = QLabel("Upload a photo to search for this person in images:")
        photo_desc.setWordWrap(True)
        photo_layout.addWidget(photo_desc)

        photo_btn_layout = QHBoxLayout()
        self.upload_photo_btn = QPushButton("📁 Upload Photo")
        self.upload_photo_btn.clicked.connect(self.upload_photo)
        photo_btn_layout.addWidget(self.upload_photo_btn)

        self.photo_label = QLabel("No photo uploaded")
        self.photo_label.setStyleSheet("color: #666; font-style: italic;")
        photo_btn_layout.addWidget(self.photo_label)
        photo_btn_layout.addStretch()

        photo_layout.addLayout(photo_btn_layout)
        photo_group.setLayout(photo_layout)
        layout.addWidget(photo_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.search_btn = QPushButton("🔍 Search Evidence")
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.search_btn.clicked.connect(self.perform_search)
        button_layout.addWidget(self.search_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.suspect_photo_path = None

    def toggle_file_types(self, checked):
        """Enable/disable file type checkboxes"""
        for cb in self.file_type_checks.values():
            cb.setEnabled(not checked)
            if checked:
                cb.setChecked(False)

    def upload_photo(self):
        """Upload suspect photo for face matching"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Suspect Photo",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp)"
        )

        if file_path:
            self.suspect_photo_path = file_path
            self.photo_label.setText(f"✓ {Path(file_path).name}")
            self.photo_label.setStyleSheet("color: #00AA00; font-weight: bold;")

    def perform_search(self):
        """Validate and emit search parameters"""
        search_params = {
            'person': None,
            'date_from': None,
            'date_to': None,
            'keywords': [],
            'file_types': [],
            'suspect_photo': None
        }

        # Person search
        if self.person_enabled.isChecked() and self.person_input.text().strip():
            search_params['person'] = self.person_input.text().strip()

        # Date search
        if self.date_enabled.isChecked():
            search_params['date_from'] = self.date_from.date().toString("yyyy-MM-dd")
            search_params['date_to'] = self.date_to.date().toString("yyyy-MM-dd")

        # Keywords
        if self.keyword_enabled.isChecked() and self.keyword_input.toPlainText().strip():
            keywords_text = self.keyword_input.toPlainText().strip()
            search_params['keywords'] = [k.strip() for k in keywords_text.split(',') if k.strip()]

        # File types
        if self.search_all.isChecked():
            search_params['file_types'] = 'all'
        else:
            search_params['file_types'] = [
                ftype for ftype, cb in self.file_type_checks.items() if cb.isChecked()
            ]

        # Suspect photo
        if self.suspect_photo_path:
            search_params['suspect_photo'] = self.suspect_photo_path

        # Validate at least one search criteria
        if not any([
            search_params['person'],
            search_params['date_from'],
            search_params['keywords'],
            search_params['suspect_photo']
        ]):
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Search Criteria",
                "Please enter at least one search criterion:\n"
                "- Person name\n"
                "- Date range\n"
                "- Keywords\n"
                "- Suspect photo"
            )
            return

        # Emit search signal
        self.search_requested.emit(search_params)
        self.accept()
