"""
Forenstiq AI Technologies - Multi-Device Forensic Analysis Platform
Main Application Entry Point
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# Add src directory to path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir.parent))

from src.ui.splash_screen import SplashScreen
from src.ui.device_selection_dashboard import DeviceSelectionDashboard
from src.ui.evidence_analyzer_window import EvidenceAnalyzerWindow
from src.ui.mobile_forensics_window import MobileForensicsWindow
from src.ui.styles import get_application_stylesheet
from src.utils.logger import ForenstiqLogger
from src.utils.config_loader import get_config


class ForenstiqApplication:
    """Main application controller"""

    def __init__(self, app):
        self.app = app
        self.splash = None
        self.dashboard = None
        self.active_module = None

    def start(self):
        """Start the application with splash screen"""
        # Show splash screen
        self.splash = SplashScreen()
        self.splash.finished.connect(self.show_dashboard)
        self.splash.show()

    def show_dashboard(self):
        """Show device selection dashboard after splash"""
        self.dashboard = DeviceSelectionDashboard()
        self.dashboard.device_selected.connect(self.launch_module)
        self.dashboard.show()

    def launch_module(self, device_type):
        """Launch the selected device module"""
        logger = ForenstiqLogger.get_logger()
        logger.info(f"Launching {device_type} module")

        # Close dashboard
        if self.dashboard:
            self.dashboard.hide()

        # Launch appropriate module with device_type
        # All modules now use the Evidence Analyzer with their specific device type
        if device_type in ['laptop', 'mobile', 'cctv', 'cloud', 'network', 'iot']:
            self.active_module = EvidenceAnalyzerWindow(device_type=device_type)
            # Connect the return signal to show dashboard again
            self.active_module.return_to_dashboard_signal.connect(self.show_dashboard)
            self.active_module.show()
        else:
            # Coming soon for other modules
            QMessageBox.information(
                self.dashboard,
                "Module Coming Soon",
                f"The {device_type.title()} forensics module is currently under development.\n\n"
                f"Available modules:\n"
                f"• Laptop/Computer Analysis (Full functionality)\n"
                f"• CCTV Camera Analysis (Full functionality)\n"
                f"• Mobile Phone Analysis (In Development)"
            )
            # Show dashboard again
            if self.dashboard:
                self.dashboard.show()

def setup_application():
    """Setup application directories and configuration"""
    
    # Create necessary directories
    directories = [
        'data',
        'logs',
        'reports',
        'evidence_storage',
        'temp'
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    
    # Initialize logging
    logger = ForenstiqLogger.get_logger()
    logger.info("=" * 60)
    logger.info("Forenstiq Evidence Analyzer Starting")
    logger.info("=" * 60)
    
    # Load configuration
    try:
        config = get_config()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return False
    
    return True

def main():
    """Main application entry point"""

    # High DPI support - MUST be set before creating QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Setup
    if not setup_application():
        print("Error: Failed to setup application")
        sys.exit(1)

    # Create Qt Application
    app = QApplication(sys.argv)
    app.setApplicationName("Forenstiq Evidence Analyzer")
    app.setOrganizationName("Forenstiq AI Technologies")

    # Set application style
    app.setStyle('Fusion')

    # Apply modern stylesheet
    app.setStyleSheet(get_application_stylesheet())

    # Create and start application with new flow
    forenstiq_app = ForenstiqApplication(app)
    forenstiq_app.start()

    # Start event loop
    exit_code = app.exec_()
    
    # Cleanup
    logger = ForenstiqLogger.get_logger()
    logger.info("Application shutdown")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()