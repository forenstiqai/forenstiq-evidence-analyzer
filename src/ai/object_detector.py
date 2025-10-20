"""
Object detection using YOLO
"""
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics (YOLOv8) not available. Object detection disabled.")

class ObjectDetector:
    """Detect objects in images using YOLO"""
    
    def __init__(self, model_size: str = 'n'):
        """
        Initialize object detector
        
        Args:
            model_size: YOLO model size ('n', 's', 'm', 'l', 'x')
                       'n' = nano (fastest), 'x' = extra large (most accurate)
        """
        self.model = None
        self.model_size = model_size
        self.yolo_available = YOLO_AVAILABLE
        
        if self.yolo_available:
            self._load_model()
    
    def _load_model(self):
        """Load YOLOv8 model"""
        try:
            print(f"Loading YOLOv8{self.model_size} model...")
            self.model = YOLO(f'yolov8{self.model_size}.pt')
            print("Object detection model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.yolo_available = False
    
    def detect_objects(self, image_path: Path, 
                       confidence_threshold: float = 0.5) -> List[Dict]:
        """
        Detect objects in image
        
        Args:
            image_path: Path to image
            confidence_threshold: Minimum confidence for detections
        
        Returns:
            List of detection dictionaries
        """
        if not self.yolo_available or self.model is None:
            return []
        
        detections = []
        
        try:
            # Run inference
            results = self.model(str(image_path), verbose=False)
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    confidence = float(box.conf[0])
                    
                    if confidence >= confidence_threshold:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        # Get class
                        class_id = int(box.cls[0])
                        class_name = result.names[class_id]
                        
                        detection = {
                            'class': class_name,
                            'confidence': confidence,
                            'bounding_box': {
                                'x': int(x1),
                                'y': int(y1),
                                'width': int(x2 - x1),
                                'height': int(y2 - y1)
                            }
                        }
                        detections.append(detection)
            
        except Exception as e:
            print(f"Error detecting objects in {image_path}: {e}")
        
        return detections
    
    def get_forensic_objects(self, image_path: Path) -> List[str]:
        """
        Get forensically relevant objects detected
        
        Returns:
            List of object class names
        """
        detections = self.detect_objects(image_path)
        
        # Filter for forensically relevant objects
        relevant_classes = {
            'person', 'car', 'truck', 'motorcycle', 'bicycle',
            'cell phone', 'laptop', 'knife', 'gun', 'bottle',
            'backpack', 'handbag', 'suitcase', 'clock', 'book'
        }
        
        objects = []
        for det in detections:
            if det['class'] in relevant_classes:
                objects.append(det['class'])
        
        return list(set(objects))  # Remove duplicates