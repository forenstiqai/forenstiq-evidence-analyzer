"""
Report Options Dialog - Select report type and options
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QGroupBox,
    QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt


class ReportOptionsDialog(QDialog):
    """Dialog for selecting report generation options"""

    def __init__(self, flagged_count: int = 0, total_files: int = 0, parent=None):
        super().__init__(parent)

        self.flagged_count = flagged_count
        self.total_files = total_files
        self.report_type = "full"  # Default to full report

        self.init_ui()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Generate Report")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Select Report Type")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        layout.addWidget(title)

        layout.addSpacing(10)

        # Description
        desc = QLabel(
            "Choose the type of report you want to generate for this case."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(desc)

        layout.addSpacing(20)

        # Report type selection
        report_group = QGroupBox("Report Type")
        report_layout = QVBoxLayout()

        self.button_group = QButtonGroup()

        # Full report option
        self.full_report_radio = QRadioButton(
            f"📄 Full Case Report ({self.total_files} files)"
        )
        self.full_report_radio.setChecked(True)
        self.full_report_radio.setStyleSheet("color: #CCCCCC; font-size: 13px;")
        self.button_group.addButton(self.full_report_radio, 0)
        report_layout.addWidget(self.full_report_radio)

        full_desc = QLabel("    Includes all evidence files in the case")
        full_desc.setStyleSheet("color: #9CDCFE; font-size: 11px; margin-left: 20px;")
        report_layout.addWidget(full_desc)

        report_layout.addSpacing(15)

        # Flagged only option
        self.flagged_report_radio = QRadioButton(
            f"⚠️  Flagged Evidence Only ({self.flagged_count} files)"
        )
        self.flagged_report_radio.setStyleSheet("color: #CCCCCC; font-size: 13px;")
        self.button_group.addButton(self.flagged_report_radio, 1)
        report_layout.addWidget(self.flagged_report_radio)

        flagged_desc = QLabel("    Only includes files marked as flagged evidence")
        flagged_desc.setStyleSheet("color: #9CDCFE; font-size: 11px; margin-left: 20px;")
        report_layout.addWidget(flagged_desc)

        # Disable flagged option if no flagged files
        if self.flagged_count == 0:
            self.flagged_report_radio.setEnabled(False)
            no_flagged_label = QLabel("    ⓘ No flagged items in this case")
            no_flagged_label.setStyleSheet("color: #888888; font-size: 11px; margin-left: 20px; font-style: italic;")
            report_layout.addWidget(no_flagged_label)

        report_group.setLayout(report_layout)
        layout.addWidget(report_group)

        layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        generate_btn = QPushButton("Generate Report")
        generate_btn.setMinimumWidth(150)
        generate_btn.clicked.connect(self.accept)
        generate_btn.setDefault(True)
        button_layout.addWidget(generate_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_report_type(self) -> str:
        """
        Get selected report type

        Returns:
            "full" or "flagged"
        """
        if self.flagged_report_radio.isChecked():
            return "flagged"
        return "full"

    def is_flagged_only(self) -> bool:
        """
        Check if flagged-only report is selected

        Returns:
            True if flagged-only report
        """
        return self.get_report_type() == "flagged"
