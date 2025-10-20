"""
Optical Character Recognition (OCR)
"""
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Dict, Optional
import cv2
import numpy as np
import platform
import subprocess

class OCREngine:
    """Extract text from images"""

    def __init__(self, tesseract_path: Optional[str] = None):
        # Auto-detect tesseract path if not provided
        if not tesseract_path:
            tesseract_path = self._find_tesseract()

        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.languages = 'eng'  # Can be extended: 'eng+hin+tel'

    def _find_tesseract(self) -> Optional[str]:
        """Auto-detect tesseract installation path"""
        system = platform.system()

        # Common paths for different operating systems
        common_paths = []

        if system == 'Darwin':  # macOS
            common_paths = [
                '/opt/homebrew/bin/tesseract',
                '/usr/local/bin/tesseract',
                '/opt/local/bin/tesseract'
            ]
        elif system == 'Windows':
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
        else:  # Linux
            common_paths = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract'
            ]

        # Check common paths
        for path in common_paths:
            if Path(path).exists():
                return path

        # Try using 'which' command (Unix-like systems)
        try:
            result = subprocess.run(['which', 'tesseract'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return None
    
    def extract_text(self, image_path: Path, preprocess: bool = True) -> Dict:
        """
        Extract text from image
        
        Args:
            image_path: Path to image
            preprocess: Whether to preprocess image for better OCR
        
        Returns:
            Dictionary with text and confidence
        """
        try:
            # Load image
            if preprocess:
                image = self._preprocess_image(image_path)
            else:
                image = Image.open(image_path)
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=self.languages)
            
            # Get detailed data with confidence
            data = pytesseract.image_to_data(image, lang=self.languages, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100.0,  # Normalize to 0-1
                'word_count': len(text.split()),
                'has_text': len(text.strip()) > 0
            }
            
        except Exception as e:
            # Log warning instead of printing
            import logging
            logging.warning(f"OCR error for {image_path.name}: {str(e)}")
            return {
                'text': '',
                'confidence': 0.0,
                'word_count': 0,
                'has_text': False,
                'error': str(e)
            }
    
    def _preprocess_image(self, image_path: Path) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Applies: grayscale, thresholding, noise removal
        """
        # Load with OpenCV
        image = cv2.imread(str(image_path))
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        
        # Noise removal
        gray = cv2.medianBlur(gray, 3)
        
        # Convert back to PIL Image
        return Image.fromarray(gray)
    
    def set_language(self, languages: str):
        """
        Set OCR languages
        
        Args:
            languages: Language codes (e.g., 'eng', 'eng+hin', 'eng+hin+tel')
        """
        self.languages = languages