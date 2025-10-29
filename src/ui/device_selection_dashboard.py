"""
Device Selection Dashboard - Main menu for selecting device type
"""
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class DeviceCard(QFrame):
    """Card widget for each device type"""

    clicked = pyqtSignal(str)

    def __init__(self, device_type, icon, title, description, parent=None):
        super().__init__(parent)
        self.device_type = device_type
        self.setup_ui(icon, title, description)

    def setup_ui(self, icon, title, description):
        """Setup the card UI"""
        self.setObjectName("deviceCard")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Icon/Emoji
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont("Arial", 48)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_font = QFont("Arial", 11)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #9CDCFE;")
        layout.addWidget(desc_label)

        # Launch button
        launch_btn = QPushButton("Launch Module")
        launch_btn.setMinimumHeight(40)
        launch_btn.clicked.connect(lambda: self.clicked.emit(self.device_type))
        layout.addWidget(launch_btn)

        self.setLayout(layout)

        # Card styling
        self.setStyleSheet("""
            QFrame#deviceCard {
                background-color: #252526;
                border: 2px solid #3E3E42;
                border-radius: 12px;
                min-width: 280px;
                min-height: 320px;
            }
            QFrame#deviceCard:hover {
                background-color: #2D2D30;
                border: 2px solid #007ACC;
            }
        """)

    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.device_type)


class DeviceSelectionDashboard(QMainWindow):
    """Main dashboard for selecting device type"""

    device_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the dashboard UI"""
        self.setWindowTitle("Forenstiq AI Technologies - Forensic Platform")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(10)

        # Company name
        company_label = QLabel("FORENSTIQ AI TECHNOLOGIES")
        company_label.setAlignment(Qt.AlignCenter)
        company_font = QFont("Arial", 32, QFont.Bold)
        company_label.setFont(company_font)
        company_label.setStyleSheet("""
            color: #00BFFF;
            letter-spacing: 4px;
        """)
        header_layout.addWidget(company_label)

        # Tagline
        tagline_label = QLabel("Advanced Multi-Device Forensic Analysis Platform")
        tagline_label.setAlignment(Qt.AlignCenter)
        tagline_font = QFont("Arial", 14)
        tagline_label.setFont(tagline_font)
        tagline_label.setStyleSheet("color: #9CDCFE; font-style: italic;")
        header_layout.addWidget(tagline_label)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # Subtitle
        subtitle_label = QLabel("Select Evidence Type (Police Seizure Categories)")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 16, QFont.Bold)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: #FFFFFF;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(20)

        # Device cards grid
        cards_widget = QWidget()
        cards_layout = QGridLayout()
        cards_layout.setSpacing(25)

        # Create evidence category cards (based on actual police seizures)
        devices = [
            {
                'type': 'mobile',
                'icon': '📱',
                'title': 'Mobile Devices',
                'description': 'Smartphones, feature phones, tablets - WhatsApp, SMS, calls, photos, UPI transactions'
            },
            {
                'type': 'storage',
                'icon': '💾',
                'title': 'Storage Media',
                'description': 'USB drives, memory cards, external HDDs, SIM cards - bulk data extraction'
            },
            {
                'type': 'computer',
                'icon': '💻',
                'title': 'Computers',
                'description': 'Laptops, desktops, internal drives - documents, browser history, financial records'
            },
            {
                'type': 'cctv',
                'icon': '📹',
                'title': 'CCTV/DVR Systems',
                'description': 'Surveillance footage, DVR exports - face detection, movement tracking, timeline analysis'
            },
            {
                'type': 'network',
                'icon': '🌐',
                'title': 'Network Equipment',
                'description': 'Routers, modems - connection logs, DNS history, device tracking'
            },
            {
                'type': 'fraud_device',
                'icon': '⚠️',
                'title': 'Fraud Equipment',
                'description': 'SIM boxes, GSM gateways, skimmers - specialized cybercrime device analysis'
            }
        ]

        # Add cards to grid (2 columns)
        row, col = 0, 0
        for device in devices:
            card = DeviceCard(
                device['type'],
                device['icon'],
                device['title'],
                device['description']
            )
            card.clicked.connect(self.on_device_selected)
            cards_layout.addWidget(card, row, col)

            col += 1
            if col > 2:  # 3 cards per row
                col = 0
                row += 1

        cards_widget.setLayout(cards_layout)
        main_layout.addWidget(cards_widget)

        main_layout.addStretch()

        # Footer
        footer_label = QLabel("© 2024 Forenstiq AI Technologies • Advancing Digital Forensics")
        footer_label.setAlignment(Qt.AlignCenter)
        footer_font = QFont("Arial", 9)
        footer_label.setFont(footer_font)
        footer_label.setStyleSheet("color: #6A6A6A;")
        main_layout.addWidget(footer_label)

        central_widget.setLayout(main_layout)

    def on_device_selected(self, device_type):
        """Handle device selection"""
        self.device_selected.emit(device_type)
