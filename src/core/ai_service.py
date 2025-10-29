"""
AI Service Singleton - Manages the lifecycle of AI models.
"""
from ..ai.image_classifier import ImageClassifier
from ..ai.face_detector import FaceDetector
from ..ai.ocr_engine import OCREngine
from ..ai.object_detector import ObjectDetector
from ..ai.text_analyzer import TextAnalyzer
from ..utils.logger import get_logger
from ..utils.config_loader import get_config

class AIService:
    """
    A singleton service to manage and provide access to AI models.
    This ensures that models are loaded only once during the application's lifetime.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.logger = get_logger()
        self.config = get_config()
        self._initialized = True
        
        self.logger.info("Initializing AI Service Singleton...")

        # Check what AI modules are enabled in the config
        self.face_detection_enabled = self.config.get_bool('AI', 'face_detection_enabled', True)
        self.ocr_enabled = self.config.get_bool('AI', 'ocr_enabled', True)
        self.object_detection_enabled = self.config.get_bool('AI', 'object_detection_enabled', True)

        # Initialize AI models
        self.image_classifier = None
        self.face_detector = None
        self.ocr_engine = None
        self.object_detector = None
        self.text_analyzer = None

        self._load_models()

    def _load_models(self):
        """Load all configured AI models."""
        self.logger.info("Loading AI models...")

        try:
            self.image_classifier = ImageClassifier()
            self.logger.info("✓ Image classifier loaded")
        except Exception as e:
            self.logger.error(f"✗ Image classifier failed to load: {e}")

        if self.face_detection_enabled:
            try:
                self.face_detector = FaceDetector()
                self.logger.info("✓ Face detector loaded")
            except Exception as e:
                self.logger.error(f"✗ Face detector failed to load: {e}")
        else:
            self.logger.info("○ Face detection is disabled.")

        if self.ocr_enabled:
            try:
                tesseract_path = self.config.get('OCR', 'tesseract_path')
                self.ocr_engine = OCREngine(tesseract_path)
                self.logger.info("✓ OCR engine loaded")
            except Exception as e:
                self.logger.error(f"✗ OCR engine failed to load: {e}")
        else:
            self.logger.info("○ OCR is disabled.")

        if self.object_detection_enabled:
            try:
                self.object_detector = ObjectDetector()
                self.logger.info("✓ Object detector loaded")
            except Exception as e:
                self.logger.error(f"✗ Object detector failed to load: {e}")
        else:
            self.logger.info("○ Object detection is disabled.")
            
        try:
            self.text_analyzer = TextAnalyzer()
            self.logger.info("✓ Text analyzer loaded")
        except Exception as e:
            self.logger.error(f"✗ Text analyzer failed to load: {e}")

        self.logger.info("AI model loading complete.")

def get_ai_service():
    """Global accessor for the AIService singleton instance."""
    return AIService()
