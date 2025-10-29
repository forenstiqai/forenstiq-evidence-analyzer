"""
Single File Analysis Worker - For on-demand AI analysis
Analyzes a single file when user clicks on it
"""
from PyQt5.QtCore import QThread, pyqtSignal
from ...core.ai_analyzer import AIAnalyzer
from ...core.ai_service import AIService


class SingleFileAnalysisWorker(QThread):
    """Worker thread for analyzing a single file on-demand"""

    # Signals
    finished = pyqtSignal(dict)  # file_data with AI results
    error = pyqtSignal(str)  # error message

    def __init__(self, file_id: int, ai_service: AIService):
        super().__init__()
        self.file_id = file_id
        self.ai_service = ai_service
        self.analyzer = None

    def run(self):
        """Run analysis in background"""
        try:
            # Initialize analyzer with shared AI service
            self.analyzer = AIAnalyzer(self.ai_service)

            # Analyze single file
            results = self.analyzer.analyze_file(self.file_id)

            # Get updated file data from database
            from ...database.file_repository import FileRepository
            file_repo = FileRepository()
            updated_file = file_repo.get_file(self.file_id)

            if updated_file:
                self.finished.emit(updated_file)
            else:
                self.error.emit(f"File {self.file_id} not found after analysis")

        except Exception as e:
            self.error.emit(str(e))
