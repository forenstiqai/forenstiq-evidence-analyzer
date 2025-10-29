"""
Face Matching and Recognition Module
Compare a suspect's face against evidence photos
"""
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition library not available. Face matching features disabled.")

import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import cv2


class FaceMatcher:
    """Match faces across images for suspect identification"""

    def __init__(self, tolerance: float = 0.6):
        """
        Initialize face matcher

        Args:
            tolerance: Lower is more strict (0.6 is default, 0.5 is strict)
        """
        self.tolerance = tolerance
        self.suspect_encodings = []
        self.suspect_image_path = None

    def load_suspect_photo(self, image_path: Path) -> Dict:
        """
        Load and encode suspect's photo

        Args:
            image_path: Path to suspect's photo

        Returns:
            Dictionary with status and face count
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return {
                'success': False,
                'error': 'Face recognition library not available',
                'face_count': 0
            }

        try:
            # Load image
            image = face_recognition.load_image_file(str(image_path))

            # Find faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if not face_encodings:
                return {
                    'success': False,
                    'error': 'No face detected in the suspect photo',
                    'face_count': 0
                }

            # Store encodings
            self.suspect_encodings = face_encodings
            self.suspect_image_path = image_path

            return {
                'success': True,
                'face_count': len(face_encodings),
                'message': f'Loaded {len(face_encodings)} face(s) from suspect photo'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Error loading suspect photo: {str(e)}',
                'face_count': 0
            }

    def match_faces_in_image(self, image_path: Path) -> Dict:
        """
        Check if suspect appears in an image

        Args:
            image_path: Path to evidence image

        Returns:
            Dictionary with match results
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return {
                'has_match': False,
                'error': 'Face recognition library not available',
                'match_count': 0,
                'confidence': 0.0
            }

        if not self.suspect_encodings:
            return {
                'has_match': False,
                'error': 'No suspect photo loaded',
                'match_count': 0,
                'confidence': 0.0
            }

        try:
            # Load image
            image = face_recognition.load_image_file(str(image_path))

            # Find faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            if not face_encodings:
                return {
                    'has_match': False,
                    'match_count': 0,
                    'total_faces': 0,
                    'confidence': 0.0,
                    'matches': []
                }

            # Compare each face with suspect faces
            matches = []
            for idx, encoding in enumerate(face_encodings):
                # Compare with all suspect encodings
                distances = face_recognition.face_distance(self.suspect_encodings, encoding)
                min_distance = float(np.min(distances))

                is_match = min_distance <= self.tolerance

                if is_match:
                    confidence = (1.0 - min_distance) * 100  # Convert to percentage
                    matches.append({
                        'face_index': idx,
                        'location': face_locations[idx],
                        'confidence': confidence,
                        'distance': min_distance
                    })

            return {
                'has_match': len(matches) > 0,
                'match_count': len(matches),
                'total_faces': len(face_encodings),
                'confidence': max([m['confidence'] for m in matches]) if matches else 0.0,
                'matches': matches
            }

        except Exception as e:
            return {
                'has_match': False,
                'error': f'Error matching faces: {str(e)}',
                'match_count': 0,
                'confidence': 0.0
            }

    def create_annotated_image(self, image_path: Path, output_path: Path) -> bool:
        """
        Create annotated image with matched faces highlighted

        Args:
            image_path: Input image path
            output_path: Output path for annotated image

        Returns:
            True if successful
        """
        try:
            # Get matches
            match_result = self.match_faces_in_image(image_path)

            if not match_result['has_match']:
                return False

            # Load image with OpenCV
            image = cv2.imread(str(image_path))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Draw rectangles around matched faces
            for match in match_result['matches']:
                top, right, bottom, left = match['location']
                confidence = match['confidence']

                # Draw green rectangle for matches
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 3)

                # Add label
                label = f"MATCH: {confidence:.1f}%"
                cv2.putText(image, label, (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Save
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), image)

            return True

        except Exception as e:
            print(f"Error creating annotated image: {e}")
            return False

    def batch_match_images(self, image_paths: List[Path],
                          progress_callback=None) -> List[Dict]:
        """
        Match suspect face against multiple images

        Args:
            image_paths: List of image paths to check
            progress_callback: Optional callback(current, total, filename)

        Returns:
            List of dictionaries with match results
        """
        results = []
        total = len(image_paths)

        for idx, image_path in enumerate(image_paths):
            if progress_callback:
                progress_callback(idx + 1, total, image_path.name)

            match_result = self.match_faces_in_image(image_path)
            match_result['image_path'] = str(image_path)
            match_result['filename'] = image_path.name

            results.append(match_result)

        return results

    def get_suspect_info(self) -> Optional[Dict]:
        """Get information about loaded suspect photo"""
        if not self.suspect_encodings or not self.suspect_image_path:
            return None

        return {
            'image_path': str(self.suspect_image_path),
            'face_count': len(self.suspect_encodings),
            'tolerance': self.tolerance
        }

    def clear_suspect(self):
        """Clear loaded suspect photo"""
        self.suspect_encodings = []
        self.suspect_image_path = None

    def set_tolerance(self, tolerance: float):
        """
        Set matching tolerance

        Args:
            tolerance: 0.0-1.0, lower is stricter (recommended: 0.5-0.7)
        """
        if 0.0 <= tolerance <= 1.0:
            self.tolerance = tolerance
        else:
            raise ValueError("Tolerance must be between 0.0 and 1.0")
