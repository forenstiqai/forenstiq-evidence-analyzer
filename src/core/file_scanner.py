"""
Scan directories and import evidence files
"""
from pathlib import Path
from typing import List, Dict, Callable
from ..utils.file_utils import scan_directory, get_file_category, get_file_hash
from .metadata_extractor import MetadataExtractor
from ..database.file_repository import FileRepository
from ..database.case_repository import CaseRepository

from ..utils.logger import get_logger

class FileScanner:
    """Scan and import evidence files into database"""
    
    def __init__(self):
        self.logger = get_logger()
        self.metadata_extractor = MetadataExtractor()
        self.file_repo = FileRepository()
        self.case_repo = CaseRepository()
    
    def scan_and_import(self, directory: Path, case_id: int,
                        progress_callback: Callable = None) -> Dict:
        """
        Scan directory and import all files

        Args:
            directory: Directory to scan
            case_id: Case ID to associate files with
            progress_callback: Optional callback function(current, total, filename)

        Returns:
            Dictionary with import statistics
        """
        stats = {
            'total_files': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'images': 0,
            'videos': 0,
            'documents': 0,
            'audio': 0,
            'archives': 0,
            'databases': 0,
            'code': 0,
            'executables': 0,
            'emails': 0,
            'system': 0,
            'other': 0
        }

        # Store the base directory for relative path calculation
        base_directory = directory

        # Scan directory
        all_files = scan_directory(directory, recursive=True)
        stats['total_files'] = len(all_files)

        # Process each file
        for idx, file_path in enumerate(all_files):
            self.logger.info(f"Processing file: {file_path}")
            try:
                if progress_callback:
                    progress_callback(idx + 1, stats['total_files'], file_path.name)

                # Determine file category
                file_category = get_file_category(file_path)

                # Update statistics
                if file_category == 'image':
                    stats['images'] += 1
                elif file_category == 'video':
                    stats['videos'] += 1
                elif file_category == 'document':
                    stats['documents'] += 1
                elif file_category == 'audio':
                    stats['audio'] += 1
                elif file_category == 'archive':
                    stats['archives'] += 1
                elif file_category == 'database':
                    stats['databases'] += 1
                elif file_category == 'code':
                    stats['code'] += 1
                elif file_category == 'executable':
                    stats['executables'] += 1
                elif file_category == 'email':
                    stats['emails'] += 1
                elif file_category == 'system':
                    stats['system'] += 1
                else:
                    stats['other'] += 1

                # Import ALL files (no longer skip non-media files)
                self._import_file(file_path, case_id, file_category, base_directory)
                stats['imported'] += 1

            except Exception as e:
                self.logger.error(f"Error importing {file_path}: {e}")
                stats['errors'] += 1

        # Update case file counts
        self.case_repo.update_file_counts(case_id)

        return stats
    
    def _import_file(self, file_path: Path, case_id: int, file_type: str, base_directory: Path = None):
        """Import single file into database"""
        # Calculate file hash
        file_hash = get_file_hash(file_path)

        # Calculate relative path
        file_relative_path = None
        if base_directory:
            try:
                file_relative_path = str(file_path.relative_to(base_directory))
            except ValueError:
                # If file is not relative to base_directory, use just the filename
                file_relative_path = file_path.name

        # Extract metadata (for images)
        metadata = {}
        if file_type == 'image':
            metadata = self.metadata_extractor.extract_metadata(file_path)

        # Prepare file data
        file_data = {
            'case_id': case_id,
            'file_path': str(file_path),
            'file_relative_path': file_relative_path,
            'file_name': file_path.name,
            'file_type': file_type,
            'file_size': file_path.stat().st_size,
            'file_hash': file_hash,
            'date_created': metadata.get('date_created'),
            'date_modified': metadata.get('date_modified'),
            'date_accessed': metadata.get('date_accessed'),
            'date_taken': metadata.get('date_taken'),
            'gps_latitude': metadata.get('gps_latitude'),
            'gps_longitude': metadata.get('gps_longitude'),
            'gps_altitude': metadata.get('gps_altitude'),
            'camera_make': metadata.get('camera_make'),
            'camera_model': metadata.get('camera_model')
        }

        # Add to database
        self.logger.info(f"Importing file: {file_path.name}")
        self.logger.info(f"File data: {file_data}")
        self.file_repo.add_file(file_data)