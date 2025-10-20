"""
Mobile Forensics Window - For analyzing mobile phone data
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class MobileForensicsWindow(QMainWindow):
    """Mobile Phone Forensics Module"""

    def __init__(self, device_type='mobile'):
        super().__init__()
        self.device_type = device_type
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Forenstiq - Mobile Phone Forensics")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)

        # Icon
        icon_label = QLabel("📱")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Arial", 72)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title = QLabel("Mobile Phone Forensics")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)

        # Description
        desc = QLabel("Advanced forensic analysis for smartphones")
        desc.setAlignment(Qt.AlignCenter)
        desc_font = QFont("Arial", 14)
        desc.setFont(desc_font)
        desc.setStyleSheet("color: #9CDCFE;")
        layout.addWidget(desc)

        # Coming soon message
        coming_soon = QLabel("🚧 Module Under Development 🚧")
        coming_soon.setAlignment(Qt.AlignCenter)
        coming_soon_font = QFont("Arial", 16, QFont.Bold)
        coming_soon.setFont(coming_soon_font)
        coming_soon.setStyleSheet("color: #FFA500; padding: 20px;")
        layout.addWidget(coming_soon)

        # Info
        info = QLabel(
            "This module will support:\n\n"
            "• iOS and Android device extraction\n"
            "• Call logs and SMS analysis\n"
            "• App data recovery\n"
            "• Location history mapping\n"
            "• Deleted data recovery"
        )
        info.setAlignment(Qt.AlignLeft)
        info_font = QFont("Arial", 12)
        info.setFont(info_font)
        info.setStyleSheet("color: #CCCCCC; padding: 20px;")
        layout.addWidget(info)

        # Back button
        back_btn = QPushButton("← Back to Dashboard")
        back_btn.setMinimumHeight(45)
        back_btn.setMinimumWidth(200)
        back_btn.clicked.connect(self.close)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        central_widget.setLayout(layout)
