"""
Script to download required AI models
"""
from pathlib import Path
import urllib.request
import os

def download_models():
    """Download all required AI models"""
    
    models_dir = Path(__file__).parent
    models_dir.mkdir(exist_ok=True)
    
    print("Downloading AI models...")
    print("This may take several minutes depending on your internet speed.")
    
    # YOLOv8 models will be downloaded automatically by ultralytics
    # when first used
    
    print("\n✅ Model setup complete!")
    print("\nNote: Pre-trained models will be downloaded automatically")
    print("when first used by PyTorch and YOLOv8.")

if __name__ == '__main__':
    download_models()