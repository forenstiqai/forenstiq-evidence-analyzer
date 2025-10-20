"""
Image processing utilities
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Tuple, Optional

def load_image(image_path: Path) -> Optional[np.ndarray]:
    """
    Load image from file
    
    Returns:
        Image as numpy array (BGR format) or None if failed
    """
    try:
        image = cv2.imread(str(image_path))
        return image
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def load_image_pil(image_path: Path) -> Optional[Image.Image]:
    """
    Load image using PIL
    
    Returns:
        PIL Image object or None if failed
    """
    try:
        return Image.open(image_path)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None


def resize_image(image: np.ndarray, 
                 max_width: int = None, 
                 max_height: int = None) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image: Input image (numpy array)
        max_width: Maximum width
        max_height: Maximum height
    
    Returns:
        Resized image
    """
    height, width = image.shape[:2]
    
    if max_width and width > max_width:
        ratio = max_width / width
        new_width = max_width
        new_height = int(height * ratio)
    elif max_height and height > max_height:
        ratio = max_height / height
        new_height = max_height
        new_width = int(width * ratio)
    else:
        return image
    
    return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)


def create_thumbnail(image_path: Path, 
                     output_path: Path, 
                     size: Tuple[int, int] = (200, 200)):
    """
    Create thumbnail of image
    
    Args:
        image_path: Input image path
        output_path: Output thumbnail path
        size: Thumbnail size (width, height)
    """
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path, 'JPEG', quality=85)
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")


def numpy_to_pixmap(image: np.ndarray):
    """
    Convert numpy array to QPixmap for PyQt5
    
    Args:
        image: Image as numpy array (BGR format from OpenCV)
    
    Returns:
        QPixmap object
    """
    from PyQt5.QtGui import QImage, QPixmap
    
    # Convert BGR to RGB
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    height, width = image.shape[:2]
    
    if len(image.shape) == 3:
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    else:
        bytes_per_line = width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
    
    return QPixmap.fromImage(q_image)


def pil_to_pixmap(pil_image: Image.Image):
    """
    Convert PIL Image to QPixmap
    
    Args:
        pil_image: PIL Image object
    
    Returns:
        QPixmap object
    """
    from PyQt5.QtGui import QImage, QPixmap
    from io import BytesIO
    
    # Convert to RGB if necessary
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    
    # Convert to bytes
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Create QImage
    q_image = QImage()
    q_image.loadFromData(buffer.read())
    
    return QPixmap.fromImage(q_image)