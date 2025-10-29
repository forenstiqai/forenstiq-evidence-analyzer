"""
AI Analysis Orchestrator - Coordinates all AI processing
"""
from pathlib import Path
from typing import Dict, Callable
import json
from .ai_service import AIService
from ..database.file_repository import FileRepository
from ..utils.logger import get_logger

class AIAnalyzer:
    """Orchestrate AI analysis of evidence files using pre-loaded models from AIService."""
    
    def __init__(self, ai_service: AIService):
        self.logger = get_logger()
        self.file_repo = FileRepository()
        self.ai_service = ai_service

        # Get pre-loaded models from the AI service
        self.image_classifier = self.ai_service.image_classifier
        self.face_detector = self.ai_service.face_detector
        self.ocr_engine = self.ai_service.ocr_engine
        self.object_detector = self.ai_service.object_detector
        self.text_analyzer = self.ai_service.text_analyzer
        
        self.logger.info("AIAnalyzer initialized with shared AI models.")
    
    def analyze_file(self, file_id: int) -> Dict:
        """
        Analyze single file with all AI modules
        
        Returns:
            Dictionary with analysis results
        """
        # Get file info
        file_data = self.file_repo.get_file(file_id)
        if not file_data:
            raise ValueError(f"File {file_id} not found")
        
        file_path = Path(file_data['file_path'])
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_type = file_data['file_type']
        self.logger.info(f"Analyzing {file_type} file: {file_path.name}")

        results = {
            'file_id': file_id,
            'ai_tags': [],
            'ai_confidence': 0.0,
            'ocr_text': '',
            'face_count': 0,
            'objects_detected': []
        }

        # Route to appropriate analyzer based on file type
        if file_type == 'image':
            self._analyze_image(file_path, results)
        elif file_type == 'video':
            self._analyze_video(file_path, results)
        elif file_type == 'document':
            self._analyze_document(file_path, results)
        elif file_type in ['code', 'system']:
            self._analyze_text(file_path, results)
        elif file_type == 'audio':
            self._analyze_audio(file_path, results)
        elif file_type == 'database':
            self._analyze_database(file_path, results)
        elif file_type == 'email':
            self._analyze_email(file_path, results)
        elif file_type in ['archive', 'executable']:
            self._analyze_binary(file_path, results)
        else:
            # For other types, just mark as analyzed
            results['ai_tags'] = [f'{file_type}_file']
            self.logger.info(f"  → Marked as {file_type} file")

        # Update database
        analysis_data = {
            'ai_tags': json.dumps(results['ai_tags']),
            'ai_confidence': results['ai_confidence'],
            'ocr_text': results['ocr_text'],
            'face_count': results['face_count']
        }

        self.file_repo.update_ai_analysis(file_id, analysis_data)

        self.logger.info(f"✓ Analysis complete for {file_path.name}")

        return results

    def _analyze_image(self, file_path: Path, results: Dict):
        """Analyze image files"""
        # Image classification
        if self.image_classifier:
            try:
                tags = self.image_classifier.get_tags(file_path)
                results['ai_tags'] = tags

                # Get average confidence
                predictions = self.image_classifier.classify_image(file_path, top_k=3)
                if predictions:
                    results['ai_confidence'] = sum(p[1] for p in predictions) / len(predictions)

                self.logger.info(f"  → Image classification: {tags}")
            except Exception as e:
                self.logger.error(f"  ✗ Image classification error: {e}")

        # Face detection
        if self.face_detector:
            try:
                faces = self.face_detector.detect_faces(file_path)
                results['face_count'] = len(faces)
                self.logger.info(f"  → Faces detected: {len(faces)}")
            except Exception as e:
                self.logger.error(f"  ✗ Face detection error: {e}")

        # OCR
        if self.ocr_engine:
            try:
                ocr_result = self.ocr_engine.extract_text(file_path)
                if ocr_result['has_text'] and ocr_result['confidence'] > 0.5:
                    results['ocr_text'] = ocr_result['text']
                    self.logger.info(f"  → OCR extracted {ocr_result['word_count']} words")
                else:
                    self.logger.info(f"  → OCR: No text found")
            except Exception as e:
                self.logger.error(f"  ✗ OCR error: {e}")

        # Object detection
        if self.object_detector:
            try:
                objects = self.object_detector.get_forensic_objects(file_path)
                results['objects_detected'] = objects
                results['ai_tags'].extend(objects)
                results['ai_tags'] = list(set(results['ai_tags']))  # Remove duplicates
                self.logger.info(f"  → Objects detected: {objects if objects else 'none'}")
            except Exception as e:
                self.logger.error(f"  ✗ Object detection error: {e}")

    def _analyze_video(self, file_path: Path, results: Dict):
        """Analyze video files - mark as analyzed for now"""
        results['ai_tags'] = ['video_file']
        self.logger.info(f"  → Video file marked as analyzed")

    def _analyze_document(self, file_path: Path, results: Dict):
        """Analyze document files"""
        if self.text_analyzer:
            try:
                doc_result = self.text_analyzer.analyze_document(file_path)
                results['ai_tags'] = ['document']
                self.logger.info(f"  → Document marked as analyzed")
            except Exception as e:
                self.logger.error(f"  ✗ Document analysis error: {e}")
        else:
            results['ai_tags'] = ['document']

    def _analyze_text(self, file_path: Path, results: Dict):
        """Analyze text-based files (code, logs, etc.)"""
        if self.text_analyzer:
            try:
                text_result = self.text_analyzer.analyze_text_file(file_path)
                if text_result['has_content']:
                    results['ocr_text'] = text_result['content'][:1000]  # First 1000 chars
                    results['ai_tags'] = text_result['keywords']
                    results['ai_confidence'] = 1.0
                    self.logger.info(f"  → Text analyzed: {text_result['word_count']} words, {len(text_result['keywords'])} keywords")
                else:
                    results['ai_tags'] = ['empty_file']
                    self.logger.info(f"  → Empty or unreadable file")
            except Exception as e:
                self.logger.error(f"  ✗ Text analysis error: {e}")
                results['ai_tags'] = ['text_file']
        else:
            results['ai_tags'] = ['text_file']

    def _analyze_audio(self, file_path: Path, results: Dict):
        """Analyze audio files"""
        results['ai_tags'] = ['audio_file']
        self.logger.info(f"  → Audio file marked as analyzed")

    def _analyze_database(self, file_path: Path, results: Dict):
        """Analyze database files"""
        results['ai_tags'] = ['database_file']
        self.logger.info(f"  → Database file marked as analyzed")

    def _analyze_email(self, file_path: Path, results: Dict):
        """Analyze email files"""
        if self.text_analyzer:
            try:
                # Try to read as text
                text_result = self.text_analyzer.analyze_text_file(file_path)
                if text_result['has_content']:
                    results['ocr_text'] = text_result['content'][:1000]
                    results['ai_tags'] = ['email'] + text_result['keywords']
                    self.logger.info(f"  → Email analyzed")
                else:
                    results['ai_tags'] = ['email']
            except:
                results['ai_tags'] = ['email']
        else:
            results['ai_tags'] = ['email']

    def _analyze_binary(self, file_path: Path, results: Dict):
        """Analyze binary files (archives, executables)"""
        results['ai_tags'] = ['binary_file']
        self.logger.info(f"  → Binary file marked as analyzed")
    
    def analyze_case(self, case_id: int, progress_callback: Callable = None) -> Dict:
        """
        Analyze all unprocessed files in a case

        Args:
            case_id: Case ID to analyze
            progress_callback: Function(current, total, filename)

        Returns:
            Summary statistics
        """
        # Get ALL unprocessed files (not just images)
        files = self.file_repo.get_unprocessed_files(case_id)

        stats = {
            'total': len(files),
            'processed': 0,
            'errors': 0,
            'faces_found': 0,
            'text_found': 0,
            'objects_found': 0
        }

        self.logger.info(f"Starting case analysis: {len(files)} files to process")

        if len(files) == 0:
            self.logger.info("No unprocessed files found")
            return stats

        for idx, file_data in enumerate(files):
            try:
                if progress_callback:
                    progress_callback(idx + 1, stats['total'], file_data['file_name'])

                results = self.analyze_file(file_data['file_id'])

                stats['processed'] += 1
                stats['faces_found'] += results['face_count']

                if results['ocr_text']:
                    stats['text_found'] += 1

                if results['objects_detected']:
                    stats['objects_found'] += len(results['objects_detected'])

            except Exception as e:
                self.logger.error(f"Error analyzing {file_data['file_name']}: {e}")
                stats['errors'] += 1

        self.logger.info(f"Case analysis complete. Processed: {stats['processed']}, Errors: {stats['errors']}")

        return stats