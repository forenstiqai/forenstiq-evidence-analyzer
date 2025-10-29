"""
File List Widget - Display evidence files categorized by type
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QPushButton, QLabel, QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ...database.file_repository import FileRepository

class FileListWidget(QWidget):
    """Widget displaying list of evidence files grouped by category"""

    file_selected = pyqtSignal(dict)

    # Category definitions - Comprehensive Forensic Evidence Types (Police Seizure Priority)
    # Updated based on 2024-2025 digital forensics research - 27 categories
    CATEGORIES = {
        # Priority 1: Communication Evidence (99% of fraud cases)
        'messaging': {'icon': '💬', 'name': 'Messaging Apps', 'color': '#25D366'},  # WhatsApp, Telegram, Signal
        'messages': {'icon': '💬', 'name': 'SMS/Messages', 'color': '#34B7F1'},
        'calls': {'icon': '📞', 'name': 'Call Logs (CDR)', 'color': '#FF6B6B'},
        'social_media': {'icon': '📱', 'name': 'Social Media', 'color': '#1DA1F2'},  # Facebook, Instagram, Twitter

        # Priority 2: Financial Evidence (UPI fraud, banking, crypto)
        'banking': {'icon': '💰', 'name': 'Banking/UPI Data', 'color': '#F59E0B'},
        'cryptocurrency': {'icon': '₿', 'name': 'Cryptocurrency', 'color': '#F7931A'},  # Bitcoin, wallets, blockchain

        # Priority 3: Media Evidence (Photos, Videos, Surveillance)
        'image': {'icon': '📷', 'name': 'Photos/Images', 'color': '#4CAF50'},
        'video': {'icon': '🎬', 'name': 'Videos', 'color': '#2196F3'},  # Personal videos, phone recordings
        'cctv': {'icon': '📹', 'name': 'CCTV/Surveillance', 'color': '#1976D2'},  # DVR exports, surveillance footage

        # Priority 4: Documents (Fake certificates, PDFs)
        'document': {'icon': '📄', 'name': 'Documents', 'color': '#FF9800'},

        # Priority 5: Phone/Device Data
        'contacts': {'icon': '👤', 'name': 'Contacts', 'color': '#9C27B0'},
        'location': {'icon': '📍', 'name': 'Location/GPS Data', 'color': '#E91E63'},

        # Priority 6: Digital Activity (Browser, Cloud)
        'browser': {'icon': '🌐', 'name': 'Browser Data', 'color': '#4285F4'},  # History, cookies, cache, passwords
        'cloud': {'icon': '☁️', 'name': 'Cloud Storage', 'color': '#34A853'},  # Google Drive, Dropbox, iCloud

        # Priority 7: Storage & System
        'database': {'icon': '🗄️', 'name': 'Databases', 'color': '#607D8B'},
        'archive': {'icon': '📦', 'name': 'Archives/Backups', 'color': '#795548'},
        'memory': {'icon': '💾', 'name': 'Memory/Volatile Data', 'color': '#9E9D24'},  # RAM dumps, live forensics

        # Priority 8: Network Evidence
        'network': {'icon': '🌐', 'name': 'Router/Network Logs', 'color': '#00BCD4'},

        # Priority 9: Specialized Fraud Equipment
        'sim_data': {'icon': '📱', 'name': 'SIM Card Data', 'color': '#FF5722'},
        'fraud_device': {'icon': '⚠️', 'name': 'Fraud Device Data', 'color': '#F44336'},

        # Priority 10: Emerging Evidence (IoT, Smart Devices)
        'iot': {'icon': '⌚', 'name': 'Smart Devices/IoT', 'color': '#00897B'},  # Smartwatch, fitness tracker, vehicle
        'encrypted': {'icon': '🔐', 'name': 'Encrypted/Protected Files', 'color': '#D32F2F'},  # Encrypted containers

        # Priority 11: Other Evidence
        'audio': {'icon': '🎵', 'name': 'Audio/Voice', 'color': '#9C27B0'},
        'email': {'icon': '📧', 'name': 'Email Evidence', 'color': '#3F51B5'},
        'executable': {'icon': '⚙️', 'name': 'Apps/Executables', 'color': '#F44336'},
        'system': {'icon': '🔧', 'name': 'System Files', 'color': '#9E9E9E'},
        'other': {'icon': '📋', 'name': 'Other Evidence', 'color': '#757575'}
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.file_repo = FileRepository()
        self.current_case_id = None
        self.all_files = []
        self.matched_files = []  # For suspect matches
        self.search_results = []  # For search results
        self.category_items = {}  # Store category tree items

        self.init_ui()

    def init_ui(self):
        """Initialize professional forensic UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Professional toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("""
            QWidget {
                background: #2c3e50;
                border-bottom: 1px solid #1a252f;
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        toolbar_layout.setSpacing(8)

        # Title
        title = QLabel("Evidence Files")
        title.setStyleSheet("""
            font-weight: 600;
            font-size: 13px;
            color: #ecf0f1;
            background: transparent;
        """)
        toolbar_layout.addWidget(title)

        toolbar_layout.addStretch()

        # View toggle
        view_label = QLabel("View:")
        view_label.setStyleSheet("color: #95a5a6; background: transparent; font-size: 11px;")
        toolbar_layout.addWidget(view_label)

        self.view_toggle = QComboBox()
        self.view_toggle.addItems(["Grouped by Type", "Flat List"])
        self.view_toggle.setStyleSheet("""
            QComboBox {
                background: #34495e;
                color: #ecf0f1;
                border: 1px solid #1a252f;
                padding: 4px 8px;
                font-size: 11px;
                min-width: 120px;
            }
            QComboBox:hover {
                background: #3d566e;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                border: 1px solid #1a252f;
            }
        """)
        self.view_toggle.currentTextChanged.connect(self.toggle_view_mode)
        toolbar_layout.addWidget(self.view_toggle)

        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "Flagged Only", "Images Only", "Videos Only"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background: #34495e;
                color: #ecf0f1;
                border: 1px solid #1a252f;
                padding: 4px 8px;
                font-size: 11px;
                min-width: 100px;
            }
            QComboBox:hover {
                background: #3d566e;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #34495e;
                color: #ecf0f1;
                selection-background-color: #3498db;
                border: 1px solid #1a252f;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.filter_combo)

        layout.addWidget(toolbar)

        # Search bar
        search_container = QWidget()
        search_container.setStyleSheet("background: #ffffff; border-bottom: 1px solid #dfe6e9;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(12, 8, 12, 8)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search files...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dfe6e9;
                background: #ffffff;
                padding: 6px 10px;
                font-size: 12px;
                color: #2d3436;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QLineEdit::placeholder {
                color: #b2bec3;
            }
        """)
        self.search_edit.textChanged.connect(self.search_files)
        search_layout.addWidget(self.search_edit)

        layout.addWidget(search_container)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Name", "Date", "Type", "Status"])

        # Professional tree styling
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #ffffff;
                border: none;
                font-size: 12px;
                color: #2d3436;
                outline: 0;
            }
            QTreeWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #f7f9fa;
            }
            QTreeWidget::item:hover {
                background: #f1f3f5;
            }
            QTreeWidget::item:selected {
                background: #3498db;
                color: white;
            }
            QTreeWidget::branch {
                background: transparent;
            }
            QHeaderView::section {
                background: #f8f9fa;
                color: #636e72;
                padding: 8px 4px;
                border: none;
                border-bottom: 2px solid #dfe6e9;
                border-right: 1px solid #dfe6e9;
                font-weight: 600;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

        self.tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.tree.setAlternatingRowColors(False)
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(20)
        self.tree.setAnimated(False)

        # Column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # Selection handling
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)

        layout.addWidget(self.tree)

        # Status bar
        status_bar = QWidget()
        status_bar.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border-top: 1px solid #dfe6e9;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 6, 12, 6)

        self.status_label = QLabel("Total: 0 files")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #636e72;
            background: transparent;
        """)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        layout.addWidget(status_bar)

        self.setLayout(layout)
    
    def load_case_files(self, case_id):
        """Load files for case"""
        self.current_case_id = case_id

        try:
            files = self.file_repo.get_files_by_case(case_id)
            self.all_files = files
            self.display_files(files)
        except Exception as e:
            print(f"Error loading files: {e}")

    def toggle_view_mode(self):
        """Toggle between grouped and flat view"""
        self.display_files(self.all_files)

    def display_files(self, files):
        """Display files in tree (grouped by category or flat)"""
        self.tree.clear()
        self.category_items = {}

        view_mode = self.view_toggle.currentText()

        # Check for both with and without emoji prefix
        if "Grouped by Type" in view_mode:
            # ALWAYS show grouped view with all categories (even if 0 files)
            self._display_grouped(files)
        else:
            # Flat list - only show if there are files
            if not files:
                self.status_label.setText("Total: 0 files")
                return
            self._display_flat(files)

        self.status_label.setText(f"Total: {len(files)} files")

    def _display_grouped(self, files):
        """Display files grouped by category with icons (Google Files style - always show all categories)"""
        # Group files by category
        files_by_category = {}
        for file_data in files:
            file_type = file_data.get('file_type', 'other')
            if file_type not in files_by_category:
                files_by_category[file_type] = []
            files_by_category[file_type].append(file_data)

        # Create ALL category groups (even if empty - like Google Files)
        for category_key in self.CATEGORIES.keys():
            category_info = self.CATEGORIES[category_key]
            category_files = files_by_category.get(category_key, [])
            count = len(category_files)

            # Create category item (ALWAYS, even if 0 files)
            category_item = QTreeWidgetItem(self.tree)
            category_item.setText(0, f"{category_info['icon']} {category_info['name']} ({count})")
            category_item.setForeground(0, Qt.black)

            # Bold font for category
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)

            # Expand only if has files (collapse if empty)
            if count > 0:
                category_item.setExpanded(True)

                # Add files to category
                for file_data in category_files:
                    self._add_file_item(category_item, file_data)
            else:
                category_item.setExpanded(False)
                # Add "No files" placeholder for empty categories
                empty_item = QTreeWidgetItem(category_item)
                empty_item.setText(0, "No files in this category")
                empty_item.setForeground(0, Qt.gray)
                empty_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable

            # Store category item
            self.category_items[category_key] = category_item

    def _display_flat(self, files):
        """Display all files in flat list"""
        for file_data in files:
            self._add_file_item(self.tree, file_data)

    def _add_file_item(self, parent, file_data):
        """Add a file item to the tree"""
        file_item = QTreeWidgetItem(parent)

        # Filename with flag
        filename = file_data.get('file_name', '')
        if file_data.get('is_flagged'):
            filename = f"⚠️ {filename}"

        file_item.setText(0, filename)
        file_item.setData(0, Qt.UserRole, file_data)  # Store full data

        # Date taken
        date_taken = file_data.get('date_taken', '')
        if date_taken:
            date_taken = date_taken.split('T')[0]  # Just date part
        file_item.setText(1, date_taken)

        # Type
        file_type = file_data.get('file_type', '').upper()
        file_item.setText(2, file_type)

        # Status
        if file_data.get('ai_processed'):
            status = "✓ Analyzed"
            file_item.setForeground(3, Qt.darkGreen)
        else:
            status = "Pending"
            file_item.setForeground(3, Qt.darkGray)

        file_item.setText(3, status)

        return file_item
    
    def apply_filter(self):
        """Apply selected filter"""
        filter_text = self.filter_combo.currentText()

        if filter_text == "All Files":
            filtered = self.all_files
            self.status_label.setStyleSheet("font-size: 10px; color: #999;")
        elif filter_text == "Suspect Matches":
            if hasattr(self, 'matched_files') and self.matched_files:
                self.show_suspect_matches(self.matched_files)
                return
            else:
                filtered = []
        elif filter_text == "Flagged Only":
            filtered = [f for f in self.all_files if f.get('is_flagged')]
        elif filter_text == "Images Only":
            filtered = [f for f in self.all_files if f.get('file_type') == 'image']
        elif filter_text == "Videos Only":
            filtered = [f for f in self.all_files if f.get('file_type') == 'video']
        else:
            filtered = self.all_files

        self.display_files(filtered)

    def search_files(self, text):
        """Search files by filename"""
        if not text:
            self.display_files(self.all_files)
            return

        text = text.lower()
        filtered = [f for f in self.all_files if text in f.get('file_name', '').lower()]
        self.display_files(filtered)

    def on_selection_changed(self):
        """Handle file selection"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            file_data = item.data(0, Qt.UserRole)

            # Only emit if this is a file item (not a category)
            if file_data:
                self.file_selected.emit(file_data)
    
    def show_suspect_matches(self, matched_files):
        """Display only files matching the suspect"""
        self.tree.clear()

        for file_data in matched_files:
            file_item = QTreeWidgetItem(self.tree)

            # Filename with match indicators
            match_conf = file_data.get('match_confidence', 0)
            match_count = file_data.get('match_count', 1)
            flag_icon = "⚠️" if file_data.get('is_flagged') else ""
            filename = file_data.get('file_name', '')

            filename_display = f"{flag_icon}🎯 {filename} ({match_conf:.1f}% - {match_count} face(s))"
            file_item.setText(0, filename_display)
            file_item.setForeground(0, Qt.darkGreen)
            file_item.setData(0, Qt.UserRole, file_data)
            file_item.setToolTip(0, f"Match confidence: {match_conf:.1f}%\nFaces found: {match_count}")

            # Date taken
            date_taken = file_data.get('date_taken', '')
            if date_taken:
                date_taken = date_taken.split('T')[0]
            file_item.setText(1, date_taken)

            # Type
            file_type = file_data.get('file_type', '').upper()
            file_item.setText(2, file_type)

            # Status
            file_item.setText(3, "🎯 SUSPECT MATCH")
            file_item.setForeground(3, Qt.darkGreen)

        self.status_label.setText(
            f"Showing {len(matched_files)} suspect match(es) | "
            "Click 'All Files' filter to reset"
        )
        self.status_label.setStyleSheet("font-size: 10px; color: #1E8E3E; font-weight: 600;")

        # Add "Suspect Matches" to filter if not already there
        if self.filter_combo.findText("Suspect Matches") == -1:
            self.filter_combo.insertItem(1, "Suspect Matches")
        self.filter_combo.setCurrentText("Suspect Matches")

        # Store matched files for filter
        self.matched_files = matched_files

    def show_search_results(self, search_results):
        """Display search results with match details"""
        self.tree.clear()

        for file_data in search_results:
            file_item = QTreeWidgetItem(self.tree)

            # Filename with search match indicators
            flag_icon = "⚠️" if file_data.get('is_flagged') else ""
            filename = file_data.get('file_name', '')
            match_details = file_data.get('match_details', {})
            match_count = match_details.get('match_count', 0)
            matches_text = ', '.join(match_details.get('matches', []))

            filename_display = f"{flag_icon}🔎 {filename} ({match_count} match(es))"
            file_item.setText(0, filename_display)
            file_item.setForeground(0, Qt.blue)
            file_item.setData(0, Qt.UserRole, file_data)
            file_item.setToolTip(0, f"Matches:\n{matches_text}")

            # Date taken
            date_taken = file_data.get('date_taken', '')
            if date_taken:
                date_taken = date_taken.split('T')[0]
            file_item.setText(1, date_taken)

            # Type
            file_type = file_data.get('file_type', '').upper()
            file_item.setText(2, file_type)

            # Status
            file_item.setText(3, "🔎 SEARCH MATCH")
            file_item.setForeground(3, Qt.blue)

        self.status_label.setText(
            f"Showing {len(search_results)} search result(s) | "
            "Click 'All Files' filter to reset"
        )
        self.status_label.setStyleSheet("font-size: 10px; color: #007ACC; font-weight: 600;")

        # Store search results
        self.search_results = search_results

    def clear(self):
        """Clear file list - but still show all categories with (0)"""
        self.current_case_id = None
        self.all_files = []
        self.matched_files = []
        self.search_results = []
        self.category_items = {}

        # Show all categories with 0 counts (Google Files style)
        if "Grouped by Type" in self.view_toggle.currentText():
            self._display_grouped([])  # Empty list - shows all categories with (0)
        else:
            self.tree.clear()

        self.status_label.setText("Total: 0 files")
        self.status_label.setStyleSheet("""
            font-size: 11px;
            color: #636e72;
            background: transparent;
        """)