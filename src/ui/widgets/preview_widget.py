"""
Preview Widget - Display file preview and metadata
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QPushButton, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from pathlib import Path
from ...utils.image_utils import load_image_pil, pil_to_pixmap

class PreviewWidget(QWidget):
    """Widget for previewing selected file"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.current_file = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("PREVIEW")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #666;")
        layout.addWidget(title)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Image preview
        self.image_label = QLabel("Select a file to preview")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setStyleSheet("background-color: #F5F5F5; border: 1px solid #DDD;")
        self.image_label.setScaledContents(False)
        content_layout.addWidget(self.image_label)
        
        # Metadata group
        metadata_group = QGroupBox("Metadata")
        metadata_layout = QVBoxLayout()
        
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setMaximumHeight(200)
        self.metadata_text.setStyleSheet("background-color: #FFFFFF; color: #202124; font-size: 10px; font-family: monospace;")
        metadata_layout.addWidget(self.metadata_text)
        
        metadata_group.setLayout(metadata_layout)
        content_layout.addWidget(metadata_group)
        
        # Actions
        actions_layout = QHBoxLayout()
        
        self.flag_button = QPushButton("🚩 Flag as Evidence")
        self.flag_button.setEnabled(False)
        self.flag_button.clicked.connect(self.toggle_flag)
        actions_layout.addWidget(self.flag_button)
        
        self.note_button = QPushButton("📝 Add Note")
        self.note_button.setEnabled(False)
        actions_layout.addWidget(self.note_button)
        
        content_layout.addLayout(actions_layout)
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
    
    def load_file(self, file_data):
        """Load and display file"""
        self.current_file = file_data
        
        # Load image if it's an image file
        if file_data.get('file_type') == 'image':
            file_path = Path(file_data.get('file_path'))
            if file_path.exists():
                try:
                    pil_image = load_image_pil(file_path)
                    if pil_image:
                        # Resize for display
                        display_size = (600, 600)
                        pil_image.thumbnail(display_size)
                        
                        pixmap = pil_to_pixmap(pil_image)
                        self.image_label.setPixmap(pixmap)
                        self.image_label.setAlignment(Qt.AlignCenter)
                except Exception as e:
                    self.image_label.setText(f"Error loading image:\n{str(e)}")
            else:
                self.image_label.setText("Image file not found")
        else:
            self.image_label.setText(f"Preview not available for {file_data.get('file_type')} files")
        
        # Display metadata
        self.display_metadata(file_data)
        
        # Enable buttons
        self.flag_button.setEnabled(True)
        self.note_button.setEnabled(True)
        
        # Update flag button text
        if file_data.get('is_flagged'):
            self.flag_button.setText("🏳️ Unflag")
        else:
            self.flag_button.setText("🚩 Flag as Evidence")
    
    def display_metadata(self, file_data):
        """Display file metadata"""
        metadata_lines = []

        # Basic info
        metadata_lines.append(f"Filename: {file_data.get('file_name', 'N/A')}")
        metadata_lines.append(f"Type: {file_data.get('file_type', 'N/A').upper()}")

        # File size
        size_bytes = file_data.get('file_size', 0)
        size_mb = size_bytes / (1024 * 1024)
        metadata_lines.append(f"Size: {size_mb:.2f} MB")

        # File paths
        metadata_lines.append("")
        metadata_lines.append("=== File Location ===")
        if file_data.get('file_relative_path'):
            metadata_lines.append(f"Relative Path: {file_data['file_relative_path']}")
        metadata_lines.append(f"Full Path: {file_data.get('file_path', 'N/A')}")

        # Hash value
        if file_data.get('file_hash'):
            metadata_lines.append("")
            metadata_lines.append("=== File Integrity ===")
            metadata_lines.append(f"SHA-256 Hash: {file_data['file_hash']}")
        
        # Dates
        metadata_lines.append("")
        metadata_lines.append("=== Dates ===")
        if file_data.get('date_taken'):
            metadata_lines.append(f"Date Taken: {file_data['date_taken']}")
        if file_data.get('date_created'):
            metadata_lines.append(f"Date Created: {file_data['date_created']}")
        if file_data.get('date_modified'):
            metadata_lines.append(f"Date Modified: {file_data['date_modified']}")
        if file_data.get('date_accessed'):
            metadata_lines.append(f"Date Accessed: {file_data['date_accessed']}")
        
        # GPS
        if file_data.get('gps_latitude') or file_data.get('gps_longitude'):
            metadata_lines.append("")
            metadata_lines.append("=== Location ===")
            if file_data.get('gps_latitude'):
                metadata_lines.append(f"Latitude: {file_data['gps_latitude']:.6f}")
            if file_data.get('gps_longitude'):
                metadata_lines.append(f"Longitude: {file_data['gps_longitude']:.6f}")
            if file_data.get('gps_altitude'):
                metadata_lines.append(f"Altitude: {file_data['gps_altitude']:.2f}m")
        
        # Camera
        if file_data.get('camera_make') or file_data.get('camera_model'):
            metadata_lines.append("")
            metadata_lines.append("=== Camera ===")
            if file_data.get('camera_make'):
                metadata_lines.append(f"Make: {file_data['camera_make']}")
            if file_data.get('camera_model'):
                metadata_lines.append(f"Model: {file_data['camera_model']}")
        
        # AI Analysis
        if file_data.get('ai_processed'):
            metadata_lines.append("")
            metadata_lines.append("=== AI Analysis ===")
            if file_data.get('ai_tags'):
                metadata_lines.append(f"Tags: {file_data['ai_tags']}")
            if file_data.get('ai_confidence'):
                metadata_lines.append(f"Confidence: {file_data['ai_confidence']:.2%}")
            if file_data.get('face_count'):
                metadata_lines.append(f"Faces Detected: {file_data['face_count']}")
            if file_data.get('ocr_text'):
                metadata_lines.append(f"\nOCR Text:\n{file_data['ocr_text'][:200]}...")
        
        # Flagged status
        if file_data.get('is_flagged'):
            metadata_lines.append("")
            metadata_lines.append("=== FLAGGED ===")
            if file_data.get('flag_reason'):
                metadata_lines.append(f"Reason: {file_data['flag_reason']}")
        
        # Notes
        if file_data.get('analyst_notes'):
            metadata_lines.append("")
            metadata_lines.append("=== Analyst Notes ===")
            metadata_lines.append(file_data['analyst_notes'])
        
        self.metadata_text.setPlainText("\n".join(metadata_lines))
    
    def toggle_flag(self):
        """Toggle flag status"""
        if not self.current_file:
            return
        
        # TODO: Implement flag toggling with database
        from ...database.file_repository import FileRepository
        file_repo = FileRepository()
        
        file_id = self.current_file['file_id']
        
        if self.current_file.get('is_flagged'):
            file_repo.unflag_file(file_id)
            self.flag_button.setText("🚩 Flag as Evidence")
        else:
            file_repo.flag_file(file_id, "Manually flagged by analyst")
            self.flag_button.setText("🏳️ Unflag")
        
        # Reload file data
        updated_file = file_repo.get_file(file_id)
        if updated_file:
            self.load_file(updated_file)
    
    def clear(self):
        """Clear preview"""
        self.current_file = None
        self.image_label.clear()
        self.image_label.setText("Select a file to preview")
        self.metadata_text.clear()
        self.flag_button.setEnabled(False)
        self.note_button.setEnabled(False)