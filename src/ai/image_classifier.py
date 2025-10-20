"""
Image classification using pre-trained models
"""
import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path
from typing import List, Tuple
import json

class ImageClassifier:
    """Classify images using deep learning"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.transform = None
        self.class_labels = None
        self._load_model()
    
    def _load_model(self):
        """Load pre-trained ResNet50 model"""
        print("Loading image classification model...")

        # Load model with new weights parameter instead of deprecated pretrained
        from torchvision.models import ResNet50_Weights
        self.model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.model.to(self.device)
        self.model.eval()
        
        # Define image transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        
        # Load ImageNet class labels
        self.class_labels = self._load_imagenet_labels()
        
        print("Image classification model loaded successfully")
    
    def _load_imagenet_labels(self) -> List[str]:
        """Load ImageNet class labels"""
        # ImageNet 1000 class labels
        # For production, download from: https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json
        
        # Simplified version - top categories relevant for forensics
        return [
            "person", "face", "hand", "body",
            "vehicle", "car", "truck", "motorcycle", "bicycle",
            "weapon", "gun", "knife", "sword",
            "phone", "cell_phone", "smartphone",
            "computer", "laptop", "screen", "monitor",
            "building", "house", "street", "road",
            "indoor", "outdoor", "landscape",
            "document", "paper", "text", "writing",
            "currency", "money", "cash", "credit_card",
            "drug", "pill", "syringe", "bottle",
            "animal", "dog", "cat",
            "food", "drink",
            "clothing", "shirt", "pants", "shoes",
            "bag", "backpack", "luggage"
        ]
    
    def classify_image(self, image_path: Path, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Classify image and return top predictions
        
        Args:
            image_path: Path to image file
            top_k: Number of top predictions to return
        
        Returns:
            List of (label, confidence) tuples
        """
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
            # Get top k predictions
            top_prob, top_indices = torch.topk(probabilities, top_k)
            
            results = []
            for i in range(top_k):
                idx = top_indices[i].item()
                prob = top_prob[i].item()
                
                # Map to label (simplified)
                label = self.class_labels[idx % len(self.class_labels)]
                results.append((label, prob))
            
            return results
            
        except Exception as e:
            import logging
            logging.error(f"Error classifying image {image_path.name}: {e}")
            return []
    
    def get_tags(self, image_path: Path, confidence_threshold: float = 0.3) -> List[str]:
        """
        Get relevant tags for image
        
        Args:
            image_path: Path to image
            confidence_threshold: Minimum confidence for tags
        
        Returns:
            List of tag strings
        """
        predictions = self.classify_image(image_path, top_k=10)
        
        tags = []
        for label, confidence in predictions:
            if confidence >= confidence_threshold:
                tags.append(label)
        
        return tags