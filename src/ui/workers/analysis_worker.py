"""
Background worker for AI analysis
"""
from PyQt5.QtCore import QThread, pyqtSignal
from ...core.ai_analyzer import AIAnalyzer

class AnalysisWorker(QThread):
    """Worker thread for AI analysis"""
    
    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(dict)  # stats
    error = pyqtSignal(str)  # error message
    
    def __init__(self, case_id):
        super().__init__()
        self.case_id = case_id
        self.analyzer = None
        self._is_cancelled = False
    
    def run(self):
        """Run analysis in background"""
        try:
            # Initialize analyzer here (in worker thread)
            self.analyzer = AIAnalyzer()
            
            stats = self.analyzer.analyze_case(
                self.case_id,
                progress_callback=self.emit_progress
            )
            
            if not self._is_cancelled:
                self.finished.emit(stats)
                
        except Exception as e:
            self.error.emit(str(e))
    
    def emit_progress(self, current, total, filename):
        """Emit progress signal"""
        if not self._is_cancelled:
            self.progress.emit(current, total, filename)
    
    def cancel(self):
        """Cancel the analysis"""
        self._is_cancelled = True