"""
Splash Screen - Loading screen with company logo
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient


class SplashScreen(QWidget):
    """Splash screen with Forenstiq logo and loading animation"""

    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.progress_value = 0
        self.init_ui()
        self.start_loading()

    def init_ui(self):
        """Initialize splash screen UI"""
        # Remove window frame and make it stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set size and center on screen
        self.setFixedSize(600, 400)
        self.center_on_screen()

        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Add spacing at top
        layout.addStretch(1)

        # Company Logo Text (since we don't have an image file)
        logo_label = QLabel("FORENSTIQ")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_font = QFont("Arial", 48, QFont.Bold)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet("""
            color: #00BFFF;
            letter-spacing: 8px;
            padding: 20px;
        """)
        layout.addWidget(logo_label)

        # Subtitle
        subtitle_label = QLabel("AI TECHNOLOGIES")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont("Arial", 16, QFont.Bold)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("""
            color: #FFFFFF;
            letter-spacing: 12px;
            padding-bottom: 10px;
        """)
        layout.addWidget(subtitle_label)

        # Tagline
        tagline = QLabel("Advanced Digital Forensics Platform")
        tagline.setAlignment(Qt.AlignCenter)
        tagline_font = QFont("Arial", 12, QFont.Normal)
        tagline.setFont(tagline_font)
        tagline.setStyleSheet("""
            color: #9CDCFE;
            font-style: italic;
            padding: 5px;
        """)
        layout.addWidget(tagline)

        layout.addSpacing(30)

        # Loading label
        self.loading_label = QLabel("Initializing...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        loading_font = QFont("Arial", 11)
        self.loading_label.setFont(loading_font)
        self.loading_label.setStyleSheet("color: #CCCCCC;")
        layout.addWidget(self.loading_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3E3E42;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #007ACC,
                    stop: 1 #00BFFF
                );
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Version info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_font = QFont("Arial", 9)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #6A6A6A; padding-top: 10px;")
        layout.addWidget(version_label)

        layout.addStretch(1)

        self.setLayout(layout)

    def paintEvent(self, event):
        """Custom paint event for gradient background"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#1E1E1E"))
        gradient.setColorAt(1, QColor("#2D2D30"))

        # Draw rounded rectangle
        painter.setBrush(gradient)
        painter.setPen(QColor("#3E3E42"))
        painter.drawRoundedRect(self.rect(), 15, 15)

    def center_on_screen(self):
        """Center the splash screen on the screen"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def start_loading(self):
        """Start the loading animation"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # Update every 30ms

    def update_progress(self):
        """Update loading progress"""
        self.progress_value += 1
        self.progress_bar.setValue(self.progress_value)

        # Update loading text based on progress
        if self.progress_value < 20:
            self.loading_label.setText("Initializing system...")
        elif self.progress_value < 40:
            self.loading_label.setText("Loading AI modules...")
        elif self.progress_value < 60:
            self.loading_label.setText("Preparing forensic tools...")
        elif self.progress_value < 80:
            self.loading_label.setText("Setting up database...")
        elif self.progress_value < 100:
            self.loading_label.setText("Almost ready...")

        # When complete, close splash and show main window
        if self.progress_value >= 100:
            self.timer.stop()
            self.loading_label.setText("Ready!")
            QTimer.singleShot(500, self.close_splash)

    def close_splash(self):
        """Close splash screen and emit finished signal"""
        self.finished.emit()
        self.close()
