"""
Suspect Photo Upload Dialog
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QGroupBox, QSlider, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from pathlib import Path
from ...ai.face_matcher import FaceMatcher
from ..styles import get_primary_button_style, get_secondary_button_style


class SuspectPhotoDialog(QDialog):
    """Dialog for uploading suspect photo and configuring matching"""

    suspect_loaded = pyqtSignal(str, float)  # image_path, tolerance

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Suspect Photo")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.face_matcher = FaceMatcher()
        self.suspect_image_path = None

        self.init_ui()

    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = QLabel("Load Suspect Photo for Face Matching")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #202124;
            padding: 10px;
        """)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Upload a photo of the suspect. The system will search all evidence photos "
            "and identify images containing this person."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #5F6368; font-size: 13px; padding: 0 10px;")
        layout.addWidget(desc)

        # Image preview area
        preview_group = QGroupBox("Suspect Photo")
        preview_layout = QVBoxLayout()

        self.image_label = QLabel("No photo loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #F8F9FA;
                border: 2px dashed #DADCE0;
                border-radius: 8px;
                color: #9AA0A6;
                font-size: 14px;
            }
        """)
        preview_layout.addWidget(self.image_label)

        # Upload button
        upload_btn = QPushButton("📷  Select Suspect Photo")
        upload_btn.clicked.connect(self.select_photo)
        upload_btn.setStyleSheet(get_primary_button_style())
        upload_btn.setMinimumHeight(44)
        preview_layout.addWidget(upload_btn)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-size: 13px; padding: 10px;")
        layout.addWidget(self.info_label)

        # Matching sensitivity slider
        sensitivity_group = QGroupBox("Matching Sensitivity")
        sensitivity_layout = QVBoxLayout()

        sens_desc = QLabel(
            "Adjust how strictly faces are matched. "
            "Lower values = stricter matching (fewer false positives)"
        )
        sens_desc.setWordWrap(True)
        sens_desc.setStyleSheet("color: #5F6368; font-size: 12px; margin-bottom: 10px;")
        sensitivity_layout.addWidget(sens_desc)

        slider_layout = QHBoxLayout()

        # Labels
        strict_label = QLabel("Strict")
        strict_label.setStyleSheet("color: #5F6368; font-size: 11px;")
        slider_layout.addWidget(strict_label)

        # Slider
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setMinimum(40)  # 0.4 tolerance
        self.tolerance_slider.setMaximum(70)  # 0.7 tolerance
        self.tolerance_slider.setValue(60)    # 0.6 default
        self.tolerance_slider.setTickPosition(QSlider.TicksBelow)
        self.tolerance_slider.setTickInterval(5)
        self.tolerance_slider.valueChanged.connect(self.update_tolerance_label)
        slider_layout.addWidget(self.tolerance_slider, stretch=1)

        relaxed_label = QLabel("Relaxed")
        relaxed_label.setStyleSheet("color: #5F6368; font-size: 11px;")
        slider_layout.addWidget(relaxed_label)

        sensitivity_layout.addLayout(slider_layout)

        self.tolerance_label = QLabel("Tolerance: 0.60 (Recommended)")
        self.tolerance_label.setAlignment(Qt.AlignCenter)
        self.tolerance_label.setStyleSheet("color: #1967D2; font-weight: 600; margin-top: 8px;")
        sensitivity_layout.addWidget(self.tolerance_label)

        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(get_secondary_button_style())
        cancel_btn.setMinimumHeight(44)
        button_layout.addWidget(cancel_btn)

        self.start_btn = QPushButton("🔍  Start Face Matching")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_matching)
        self.start_btn.setStyleSheet(get_primary_button_style())
        self.start_btn.setMinimumHeight(44)
        button_layout.addWidget(self.start_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_photo(self):
        """Open file dialog to select suspect photo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Suspect Photo",
            "",
            "Images (*.jpg *.jpeg *.png *.bmp *.gif)"
        )

        if file_path:
            self.load_photo(Path(file_path))

    def load_photo(self, image_path: Path):
        """Load and validate suspect photo"""
        # Load with face matcher
        result = self.face_matcher.load_suspect_photo(image_path)

        if result['success']:
            # Display image
            pixmap = QPixmap(str(image_path))
            scaled_pixmap = pixmap.scaled(
                self.image_label.width() - 20,
                self.image_label.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

            # Update info
            face_count = result['face_count']
            if face_count == 1:
                self.info_label.setText("✓ 1 face detected - ready to match")
                self.info_label.setStyleSheet("color: #1E8E3E; font-size: 13px; font-weight: 600;")
            else:
                self.info_label.setText(f"⚠ {face_count} faces detected - will match all")
                self.info_label.setStyleSheet("color: #F9AB00; font-size: 13px; font-weight: 600;")

            self.suspect_image_path = image_path
            self.start_btn.setEnabled(True)

        else:
            # Show error
            QMessageBox.warning(
                self,
                "Error Loading Photo",
                result.get('error', 'Unknown error occurred')
            )
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("No photo loaded")
            self.info_label.setText("")
            self.start_btn.setEnabled(False)

    def update_tolerance_label(self, value):
        """Update tolerance label when slider changes"""
        tolerance = value / 100.0
        self.tolerance_label.setText(f"Tolerance: {tolerance:.2f}")

        if tolerance < 0.55:
            self.tolerance_label.setStyleSheet("color: #D93025; font-weight: 600; margin-top: 8px;")
        elif tolerance > 0.65:
            self.tolerance_label.setStyleSheet("color: #F9AB00; font-weight: 600; margin-top: 8px;")
        else:
            self.tolerance_label.setStyleSheet("color: #1E8E3E; font-weight: 600; margin-top: 8px;")

    def start_matching(self):
        """Start face matching process"""
        if self.suspect_image_path:
            tolerance = self.tolerance_slider.value() / 100.0
            self.face_matcher.set_tolerance(tolerance)
            self.suspect_loaded.emit(str(self.suspect_image_path), tolerance)
            self.accept()

    def get_face_matcher(self) -> FaceMatcher:
        """Get configured face matcher instance"""
        return self.face_matcher
