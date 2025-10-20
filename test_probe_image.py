"""
Test script to analyze a single image with all AI modules
"""
from pathlib import Path
from src.core.ai_analyzer import AIAnalyzer

# Create a dummy file in the database to get a file_id
from src.database.db_manager import get_db_manager
from src.database.file_repository import FileRepository

# Initialize the database
db_manager = get_db_manager()
file_repo = FileRepository()

# Create a dummy case
from src.database.case_repository import CaseRepository
case_repo = CaseRepository()
case_id = case_repo.create_case({
    'case_number': 'TEST-CASE-1',
    'case_name': 'Test Case for Single Image',
})

# Add the image to the database
file_path = Path('./sample_data/PROBE.JPG')
file_id = file_repo.add_file({
    'case_id': case_id,
    'file_path': str(file_path),
    'file_name': file_path.name,
    'file_type': 'image',
    'file_size': file_path.stat().st_size,
    'file_hash': 'dummy_hash',
})

# Initialize the AI Analyzer
analyzer = AIAnalyzer()

# Analyze the file
results = analyzer.analyze_file(file_id)

# Print the results
print("--- Analysis Results ---")
print(f"File: {file_path.name}")
print(f"Tags: {results['ai_tags']}")
print(f"Confidence: {results['ai_confidence']}")
print(f"Faces Detected: {results['face_count']}")
print(f"OCR Text: {results['ocr_text']}")
print(f"Objects Detected: {results['objects_detected']}")
