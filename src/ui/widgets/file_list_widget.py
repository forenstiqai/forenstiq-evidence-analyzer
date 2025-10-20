"""
File List Widget - Display evidence files in a table
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QPushButton, QLabel,
    QHeaderView, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from ...database.file_repository import FileRepository

class FileListWidget(QWidget):
    """Widget displaying list of evidence files"""
    
    file_selected = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.file_repo = FileRepository()
        self.current_case_id = None
        self.all_files = []
        self.matched_files = []  # For suspect matches

        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title and search
        header_layout = QHBoxLayout()
        
        title = QLabel("EVIDENCE FILES")
        title.setStyleSheet("font-weight: bold; font-size: 12px; color: #666;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter combo
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Files", "Flagged Only", "Images Only", "Videos Only"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        header_layout.addWidget(self.filter_combo)
        
        layout.addLayout(header_layout)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Search files...")
        self.search_edit.textChanged.connect(self.search_files)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "📷", "Filename", "Date Taken", "Type", "Status"
        ])
        
        # Table styling
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Icon
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Filename
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Status
        
        # Selection handling
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        
        # Status bar
        self.status_label = QLabel("No files")
        self.status_label.setStyleSheet("font-size: 10px; color: #999;")
        layout.addWidget(self.status_label)
        
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
    
    def display_files(self, files):
        """Display files in table"""
        self.table.setRowCount(len(files))
        
        for row, file_data in enumerate(files):
            # Flag icon
            flag_item = QTableWidgetItem("⚠️" if file_data.get('is_flagged') else "")
            flag_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, flag_item)
            
            # Filename
            filename_item = QTableWidgetItem(file_data.get('file_name', ''))
            filename_item.setData(Qt.UserRole, file_data)  # Store full data
            self.table.setItem(row, 1, filename_item)
            
            # Date taken
            date_taken = file_data.get('date_taken', '')
            if date_taken:
                date_taken = date_taken.split('T')[0]  # Just date part
            self.table.setItem(row, 2, QTableWidgetItem(date_taken))
            
            # Type
            file_type = file_data.get('file_type', '').upper()
            self.table.setItem(row, 3, QTableWidgetItem(file_type))
            
            # Status
            if file_data.get('ai_processed'):
                status = "✓ Analyzed"
                color = Qt.darkGreen
            else:
                status = "Pending"
                color = Qt.darkGray
            
            status_item = QTableWidgetItem(status)
            status_item.setForeground(color)
            self.table.setItem(row, 4, status_item)
        
        self.status_label.setText(f"Total: {len(files)} files")
    
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
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            file_data = self.table.item(row, 1).data(Qt.UserRole)
            self.file_selected.emit(file_data)
    
    def show_suspect_matches(self, matched_files):
        """Display only files matching the suspect"""
        self.table.setRowCount(len(matched_files))

        for row, file_data in enumerate(matched_files):
            # Flag icon + Match indicator
            match_conf = file_data.get('match_confidence', 0)
            flag_icon = "⚠️" if file_data.get('is_flagged') else ""
            match_icon = "✓"
            flag_item = QTableWidgetItem(f"{flag_icon}{match_icon}")
            flag_item.setTextAlignment(Qt.AlignCenter)
            flag_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 0, flag_item)

            # Filename with confidence
            filename = file_data.get('file_name', '')
            match_count = file_data.get('match_count', 1)
            filename_display = f"{filename} ({match_conf:.1f}% - {match_count} face(s))"
            filename_item = QTableWidgetItem(filename_display)
            filename_item.setData(Qt.UserRole, file_data)
            filename_item.setForeground(Qt.darkGreen)
            filename_item.setToolTip(f"Match confidence: {match_conf:.1f}%\nFaces found: {match_count}")
            self.table.setItem(row, 1, filename_item)

            # Date taken
            date_taken = file_data.get('date_taken', '')
            if date_taken:
                date_taken = date_taken.split('T')[0]
            self.table.setItem(row, 2, QTableWidgetItem(date_taken))

            # Type
            file_type = file_data.get('file_type', '').upper()
            self.table.setItem(row, 3, QTableWidgetItem(file_type))

            # Status - show as SUSPECT MATCH
            status_item = QTableWidgetItem("🎯 SUSPECT MATCH")
            status_item.setForeground(Qt.darkGreen)
            self.table.setItem(row, 4, status_item)

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
        self.table.setRowCount(len(search_results))

        for row, file_data in enumerate(search_results):
            # Flag icon + Search match indicator
            flag_icon = "⚠️" if file_data.get('is_flagged') else ""
            match_icon = "🔎"
            flag_item = QTableWidgetItem(f"{flag_icon}{match_icon}")
            flag_item.setTextAlignment(Qt.AlignCenter)
            flag_item.setForeground(Qt.blue)
            self.table.setItem(row, 0, flag_item)

            # Filename with match count
            filename = file_data.get('file_name', '')
            match_details = file_data.get('match_details', {})
            match_count = match_details.get('match_count', 0)
            matches_text = ', '.join(match_details.get('matches', []))

            filename_display = f"{filename} ({match_count} match(es))"
            filename_item = QTableWidgetItem(filename_display)
            filename_item.setData(Qt.UserRole, file_data)
            filename_item.setForeground(Qt.blue)
            filename_item.setToolTip(f"Matches:\n{matches_text}")
            self.table.setItem(row, 1, filename_item)

            # Date taken
            date_taken = file_data.get('date_taken', '')
            if date_taken:
                date_taken = date_taken.split('T')[0]
            self.table.setItem(row, 2, QTableWidgetItem(date_taken))

            # Type
            file_type = file_data.get('file_type', '').upper()
            self.table.setItem(row, 3, QTableWidgetItem(file_type))

            # Status - show as SEARCH MATCH
            status_item = QTableWidgetItem("🔎 SEARCH MATCH")
            status_item.setForeground(Qt.blue)
            self.table.setItem(row, 4, status_item)

        self.status_label.setText(
            f"Showing {len(search_results)} search result(s) | "
            "Click 'All Files' filter to reset"
        )
        self.status_label.setStyleSheet("font-size: 10px; color: #007ACC; font-weight: 600;")

        # Store search results
        self.search_results = search_results

    def clear(self):
        """Clear file list"""
        self.current_case_id = None
        self.all_files = []
        self.matched_files = []
        self.table.setRowCount(0)
        self.status_label.setText("No files")
        self.status_label.setStyleSheet("font-size: 10px; color: #999;")