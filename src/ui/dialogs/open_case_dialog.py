"""
Open Case Dialog - Select and open an existing case
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
    QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from ...database.case_repository import CaseRepository

class OpenCaseDialog(QDialog):
    """Dialog for opening existing cases"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.case_repo = CaseRepository()
        self.selected_case_id = None
        
        self.init_ui()
        self.load_cases()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Open Case")
        self.setModal(True)
        self.resize(800, 500)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Select a case to open:")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Filter by case number or name...")
        self.search_edit.textChanged.connect(self.filter_cases)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Cases table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Case Number", "Case Name", "Investigator", "Created", "Status", "Files"
        ])
        
        # Table styling
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Double-click to open
        self.table.doubleClicked.connect(self.on_double_click)
        
        layout.addWidget(self.table)
        
        # Info label
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.open_button = QPushButton("Open Case")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_selected_case)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #0066FF;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052CC;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        button_layout.addWidget(self.open_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Enable open button when row selected
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_cases(self):
        """Load all cases into table"""
        try:
            cases = self.case_repo.get_all_cases()
            self.all_cases = cases
            self.display_cases(cases)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load cases: {str(e)}"
            )
    
    def display_cases(self, cases):
        """Display cases in table"""
        self.table.setRowCount(len(cases))
        
        for row, case in enumerate(cases):
            # Case number
            self.table.setItem(row, 0, QTableWidgetItem(case.get('case_number', '')))
            
            # Case name
            self.table.setItem(row, 1, QTableWidgetItem(case.get('case_name', '')))
            
            # Investigator
            self.table.setItem(row, 2, QTableWidgetItem(case.get('investigator_name', '')))
            
            # Created date
            created = case.get('created_date', '')
            if created:
                created = created.split('T')[0]  # Just the date part
            self.table.setItem(row, 3, QTableWidgetItem(created))
            
            # Status
            status = case.get('status', 'open').upper()
            status_item = QTableWidgetItem(status)
            if status == 'OPEN':
                status_item.setForeground(Qt.darkGreen)
            elif status == 'CLOSED':
                status_item.setForeground(Qt.darkRed)
            self.table.setItem(row, 4, status_item)
            
            # Files count
            self.table.setItem(row, 5, QTableWidgetItem(str(case.get('total_files', 0))))
            
            # Store case_id in first column
            self.table.item(row, 0).setData(Qt.UserRole, case['case_id'])
        
        self.info_label.setText(f"Total cases: {len(cases)}")
    
    def filter_cases(self, text):
        """Filter cases based on search text"""
        if not text:
            self.display_cases(self.all_cases)
            return
        
        text = text.lower()
        filtered = [
            case for case in self.all_cases
            if text in case.get('case_number', '').lower() or
               text in case.get('case_name', '').lower()
        ]
        
        self.display_cases(filtered)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        self.open_button.setEnabled(len(self.table.selectedItems()) > 0)
    
    def on_double_click(self):
        """Handle double-click on table row"""
        self.open_selected_case()
    
    def open_selected_case(self):
        """Open the selected case"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            self.selected_case_id = self.table.item(row, 0).data(Qt.UserRole)
            self.accept()
    
    def get_selected_case_id(self):
        """Get the selected case ID"""
        return self.selected_case_id