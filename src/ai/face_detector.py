"""
Face detection and recognition
"""
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import pickle

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Face detection disabled.")

class FaceDetector:
    """Detect and recognize faces in images"""
    
    def __init__(self):
        self.face_cascade = None
        self.use_dlib = FACE_RECOGNITION_AVAILABLE
        self._load_cascade()
    
    def _load_cascade(self):
        """Load Haar Cascade for face detection (fallback)"""
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"Error loading face cascade: {e}")
    
    def detect_faces(self, image_path: Path) -> List[Dict]:
        """
        Detect faces in image
        
        Returns:
            List of face dictionaries with bounding boxes and encodings
        """
        faces = []
        
        try:
            if self.use_dlib:
                faces = self._detect_faces_dlib(image_path)
            else:
                faces = self._detect_faces_opencv(image_path)
        except Exception as e:
            print(f"Error detecting faces in {image_path}: {e}")
        
        return faces
    
    def _detect_faces_dlib(self, image_path: Path) -> List[Dict]:
        """Detect faces using face_recognition library (dlib)"""
        # Load image
        image = face_recognition.load_image_file(str(image_path))
        
        # Detect face locations
        face_locations = face_recognition.face_locations(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        faces = []
        for location, encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = location
            
            face_data = {
                'bounding_box': {
                    'x': left,
                    'y': top,
                    'width': right - left,
                    'height': bottom - top
                },
                'confidence': 1.0,  # face_recognition doesn't provide confidence
                'encoding': encoding.tobytes()  # Store as bytes
            }
            faces.append(face_data)
        
        return faces
    
    def _detect_faces_opencv(self, image_path: Path) -> List[Dict]:
        """Detect faces using OpenCV Haar Cascade (fallback)"""
        # Load image
        image = cv2.imread(str(image_path))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        face_rects = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        faces = []
        for (x, y, w, h) in face_rects:
            face_data = {
                'bounding_box': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                },
                'confidence': 0.8,  # Haar cascade doesn't provide confidence
                'encoding': None  # No encoding without dlib
            }
            faces.append(face_data)
        
        return faces
    
    def compare_faces(self, encoding1: bytes, encoding2: bytes, 
                     tolerance: float = 0.6) -> bool:
        """
        Compare two face encodings
        
        Args:
            encoding1: First face encoding (bytes)
            encoding2: Second face encoding (bytes)
            tolerance: Match threshold (lower is more strict)
        
        Returns:
            True if faces match
        """
        if not self.use_dlib or encoding1 is None or encoding2 is None:
            return False
        
        try:
            # Convert bytes back to numpy arrays
            enc1 = np.frombuffer(encoding1, dtype=np.float64)
            enc2 = np.frombuffer(encoding2, dtype=np.float64)
            
            # Compare
            distance = np.linalg.norm(enc1 - enc2)
            return distance <= tolerance
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False