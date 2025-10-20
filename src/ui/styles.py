"""
Modern UI Stylesheet for Forenstiq Evidence Analyzer
"""

def get_application_stylesheet():
    """
    Get modern application-wide stylesheet

    Returns:
        String containing Qt StyleSheet
    """
    return """
    /* Main Application Styling */
    QMainWindow {
        background-color: #1E1E1E;
    }

    /* Menu Bar */
    QMenuBar {
        background-color: #2D2D30;
        border-bottom: 1px solid #3E3E42;
        padding: 4px;
        color: #CCCCCC;
    }

    QMenuBar::item {
        padding: 6px 12px;
        background-color: transparent;
        border-radius: 4px;
        color: #CCCCCC;
    }

    QMenuBar::item:selected {
        background-color: #094771;
        color: #FFFFFF;
    }

    QMenu {
        background-color: #2D2D30;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 4px;
        color: #CCCCCC;
    }

    QMenu::item {
        padding: 8px 24px 8px 12px;
        border-radius: 4px;
        color: #CCCCCC;
    }

    QMenu::item:selected {
        background-color: #094771;
        color: #FFFFFF;
    }

    QMenu::separator {
        height: 1px;
        background-color: #3E3E42;
        margin: 4px 8px;
    }

    /* Status Bar */
    QStatusBar {
        background-color: #2D2D30;
        border-top: 1px solid #3E3E42;
        color: #CCCCCC;
        padding: 4px 8px;
    }

    /* Buttons */
    QPushButton {
        background-color: #1967D2;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        min-height: 36px;
    }

    QPushButton:hover {
        background-color: #1557B0;
    }

    QPushButton:pressed {
        background-color: #104A94;
    }

    QPushButton:disabled {
        background-color: #E8EAED;
        color: #9AA0A6;
    }

    QPushButton#secondaryButton {
        background-color: #FFFFFF;
        color: #1967D2;
        border: 1px solid #DADCE0;
    }

    QPushButton#secondaryButton:hover {
        background-color: #F8F9FA;
        border-color: #1967D2;
    }

    QPushButton#dangerButton {
        background-color: #D93025;
    }

    QPushButton#dangerButton:hover {
        background-color: #C5221F;
    }

    /* Group Boxes */
    QGroupBox {
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 20px;
        font-weight: 600;
        color: #CCCCCC;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
        color: #CCCCCC;
    }

    /* Labels */
    QLabel {
        color: #CCCCCC;
        font-size: 13px;
    }

    QLabel#titleLabel {
        font-size: 16px;
        font-weight: 600;
        color: #FFFFFF;
    }

    QLabel#subtitleLabel {
        font-size: 12px;
        color: #9CDCFE;
    }

    QLabel#sectionHeader {
        font-size: 11px;
        font-weight: 600;
        color: #9CDCFE;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Line Edits */
    QLineEdit {
        background-color: #3C3C3C;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #CCCCCC;
    }

    QLineEdit:focus {
        border: 2px solid #007ACC;
        padding: 7px 11px;
    }

    QLineEdit:disabled {
        background-color: #2D2D30;
        color: #6A6A6A;
    }

    /* Text Edits */
    QTextEdit, QPlainTextEdit {
        background-color: #3C3C3C;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 8px;
        font-size: 13px;
        color: #CCCCCC;
        selection-background-color: #264F78;
        selection-color: #FFFFFF;
    }

    QTextEdit:focus, QPlainTextEdit:focus {
        border: 2px solid #007ACC;
    }

    /* Combo Boxes */
    QComboBox {
        background-color: #3C3C3C;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        min-height: 36px;
        color: #CCCCCC;
    }

    QComboBox:hover {
        border-color: #007ACC;
    }

    QComboBox::drop-down {
        border: none;
        width: 20px;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 6px solid #CCCCCC;
        margin-right: 8px;
    }

    QComboBox QAbstractItemView {
        background-color: #3C3C3C;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        selection-background-color: #094771;
        selection-color: #FFFFFF;
        color: #CCCCCC;
        padding: 4px;
    }

    /* List and Table Widgets */
    QListWidget, QTableWidget, QTreeWidget {
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 8px;
        alternate-background-color: #2D2D30;
        selection-background-color: #094771;
        selection-color: #FFFFFF;
        font-size: 13px;
        gridline-color: #3E3E42;
        color: #CCCCCC;
    }

    QListWidget::item, QTableWidget::item, QTreeWidget::item {
        padding: 8px;
        border-bottom: 1px solid #3E3E42;
        color: #CCCCCC;
    }

    QListWidget::item:hover, QTableWidget::item:hover, QTreeWidget::item:hover {
        background-color: #2A2D2E;
    }

    QListWidget::item:selected, QTableWidget::item:selected, QTreeWidget::item:selected {
        background-color: #094771;
        color: #FFFFFF;
    }

    QHeaderView::section {
        background-color: #2D2D30;
        color: #CCCCCC;
        padding: 8px;
        border: none;
        border-right: 1px solid #3E3E42;
        border-bottom: 2px solid #3E3E42;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }

    /* Scroll Bars */
    QScrollBar:vertical {
        background-color: #2D2D30;
        width: 12px;
        border-radius: 6px;
        margin: 0px;
    }

    QScrollBar::handle:vertical {
        background-color: #686868;
        border-radius: 6px;
        min-height: 30px;
        margin: 2px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #9E9E9E;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background-color: #2D2D30;
        height: 12px;
        border-radius: 6px;
        margin: 0px;
    }

    QScrollBar::handle:horizontal {
        background-color: #686868;
        border-radius: 6px;
        min-width: 30px;
        margin: 2px;
    }

    QScrollBar::handle:horizontal:hover {
        background-color: #9E9E9E;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Progress Bar */
    QProgressBar {
        background-color: #3E3E42;
        border: none;
        border-radius: 8px;
        height: 8px;
        text-align: center;
        color: #CCCCCC;
    }

    QProgressBar::chunk {
        background-color: #007ACC;
        border-radius: 8px;
    }

    /* Progress Dialog */
    QProgressDialog {
        background-color: #2D2D30;
        border: 1px solid #3E3E42;
        border-radius: 8px;
        color: #CCCCCC;
    }

    /* Tab Widget */
    QTabWidget::pane {
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 8px;
        top: -1px;
    }

    QTabBar::tab {
        background-color: #2D2D30;
        color: #969696;
        padding: 10px 20px;
        margin-right: 4px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: 500;
    }

    QTabBar::tab:selected {
        background-color: #252526;
        color: #FFFFFF;
        border-bottom: 2px solid #007ACC;
    }

    QTabBar::tab:hover:!selected {
        background-color: #383838;
    }

    /* Splitter */
    QSplitter::handle {
        background-color: #3E3E42;
        width: 1px;
        height: 1px;
    }

    QSplitter::handle:hover {
        background-color: #007ACC;
    }

    /* Tool Tip */
    QToolTip {
        background-color: #2D2D30;
        color: #CCCCCC;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 12px;
    }

    /* Check Box */
    QCheckBox {
        spacing: 8px;
        color: #CCCCCC;
        font-size: 13px;
    }

    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #3E3E42;
        border-radius: 4px;
        background-color: #3C3C3C;
    }

    QCheckBox::indicator:hover {
        border-color: #007ACC;
    }

    QCheckBox::indicator:checked {
        background-color: #007ACC;
        border-color: #007ACC;
        image: url(:/icons/check.png);
    }

    /* Radio Button */
    QRadioButton {
        spacing: 8px;
        color: #CCCCCC;
        font-size: 13px;
    }

    QRadioButton::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #3E3E42;
        border-radius: 9px;
        background-color: #3C3C3C;
    }

    QRadioButton::indicator:hover {
        border-color: #007ACC;
    }

    QRadioButton::indicator:checked {
        background-color: #007ACC;
        border-color: #007ACC;
    }

    QRadioButton::indicator:checked::after {
        width: 8px;
        height: 8px;
        border-radius: 4px;
        background-color: #FFFFFF;
    }

    /* Spin Box */
    QSpinBox, QDoubleSpinBox {
        background-color: #3C3C3C;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #CCCCCC;
    }

    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 2px solid #007ACC;
        padding: 7px 11px;
    }

    /* Dialog Boxes */
    QDialog {
        background-color: #2D2D30;
        color: #CCCCCC;
    }

    QMessageBox {
        background-color: #2D2D30;
        color: #CCCCCC;
    }

    QMessageBox QLabel {
        color: #CCCCCC;
        font-size: 13px;
    }

    /* Frame */
    QFrame#panel {
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 8px;
        padding: 16px;
    }

    QFrame#card {
        background-color: #252526;
        border-radius: 12px;
        padding: 20px;
    }
    """


def get_card_style():
    """Get modern card-style widget background"""
    return """
        background-color: #252526;
        border: 1px solid #3E3E42;
        border-radius: 12px;
        padding: 16px;
        color: #CCCCCC;
    """


def get_primary_button_style():
    """Get primary button style"""
    return """
        QPushButton {
            background-color: #1967D2;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #1557B0;
        }
        QPushButton:pressed {
            background-color: #104A94;
        }
        QPushButton:disabled {
            background-color: #E8EAED;
            color: #9AA0A6;
        }
    """


def get_secondary_button_style():
    """Get secondary button style"""
    return """
        QPushButton {
            background-color: #3C3C3C;
            color: #FFFFFF;
            border: 2px solid #007ACC;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #094771;
        }
        QPushButton:pressed {
            background-color: #063759;
        }
        QPushButton:disabled {
            background-color: #2D2D30;
            color: #6A6A6A;
            border-color: #3E3E42;
        }
    """


def get_success_button_style():
    """Get success/positive button style"""
    return """
        QPushButton {
            background-color: #1E8E3E;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #137333;
        }
        QPushButton:pressed {
            background-color: #0D652D;
        }
        QPushButton:disabled {
            background-color: #E8EAED;
            color: #9AA0A6;
        }
    """


def get_danger_button_style():
    """Get danger/destructive button style"""
    return """
        QPushButton {
            background-color: #D93025;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #C5221F;
        }
        QPushButton:pressed {
            background-color: #A50E0E;
        }
        QPushButton:disabled {
            background-color: #E8EAED;
            color: #9AA0A6;
        }
    """
