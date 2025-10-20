"""
Forensic Search Engine - Search across all evidence files
"""
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from ..database.file_repository import FileRepository
from ..utils.logger import get_logger
import json


class ForensicSearchEngine:
    """Search evidence files by person, date, keywords"""

    def __init__(self):
        self.logger = get_logger()
        self.file_repo = FileRepository()

    def search(self, case_id: int, search_params: Dict) -> List[Dict]:
        """
        Search evidence files based on criteria

        Args:
            case_id: Case ID to search in
            search_params: Dictionary with search criteria:
                - person: Person name to search for
                - date_from: Start date (YYYY-MM-DD)
                - date_to: End date (YYYY-MM-DD)
                - keywords: List of keywords
                - file_types: 'all' or list of file types
                - suspect_photo: Path to suspect photo (optional)

        Returns:
            List of matching files with match details
        """
        self.logger.info(f"Starting forensic search in case {case_id}")
        self.logger.info(f"Search params: {search_params}")

        # Get files from case
        all_files = self.file_repo.get_files_by_case(case_id)

        # Filter by file type if specified
        if search_params.get('file_types') != 'all':
            file_types = search_params.get('file_types', [])
            all_files = [f for f in all_files if f['file_type'] in file_types]

        self.logger.info(f"Searching through {len(all_files)} files")

        results = []

        for file_data in all_files:
            matches = self._check_file_matches(file_data, search_params)
            if matches['is_match']:
                file_data['match_details'] = matches
                results.append(file_data)

        self.logger.info(f"Found {len(results)} matching files")

        # Sort by relevance (number of matches)
        results.sort(key=lambda x: x['match_details']['match_count'], reverse=True)

        return results

    def _check_file_matches(self, file_data: Dict, search_params: Dict) -> Dict:
        """
        Check if a file matches search criteria

        Returns:
            Dictionary with match details
        """
        match_info = {
            'is_match': False,
            'match_count': 0,
            'matches': []
        }

        # Search in file name
        if search_params.get('person'):
            if self._search_in_text(file_data['file_name'], search_params['person']):
                match_info['matches'].append(f"Name in filename: {file_data['file_name']}")
                match_info['match_count'] += 1

        # Search in OCR text
        if file_data.get('ocr_text') and search_params.get('person'):
            if self._search_in_text(file_data['ocr_text'], search_params['person']):
                match_info['matches'].append(f"Name found in file content")
                match_info['match_count'] += 1

        # Search for keywords
        if search_params.get('keywords'):
            for keyword in search_params['keywords']:
                # Check in filename
                if self._search_in_text(file_data['file_name'], keyword):
                    match_info['matches'].append(f"Keyword '{keyword}' in filename")
                    match_info['match_count'] += 1

                # Check in OCR text
                if file_data.get('ocr_text') and self._search_in_text(file_data['ocr_text'], keyword):
                    match_info['matches'].append(f"Keyword '{keyword}' in content")
                    match_info['match_count'] += 1

                # Check in AI tags
                if file_data.get('ai_tags'):
                    try:
                        tags = json.loads(file_data['ai_tags']) if isinstance(file_data['ai_tags'], str) else file_data['ai_tags']
                        for tag in tags:
                            if keyword.lower() in tag.lower():
                                match_info['matches'].append(f"Keyword '{keyword}' in AI tags")
                                match_info['match_count'] += 1
                                break
                    except:
                        pass

        # Date filtering
        if search_params.get('date_from') and search_params.get('date_to'):
            if self._check_date_range(file_data, search_params['date_from'], search_params['date_to']):
                match_info['matches'].append(f"File date within search range")
                match_info['match_count'] += 1

        # If we found any matches, mark as match
        if match_info['match_count'] > 0:
            match_info['is_match'] = True

        return match_info

    def _search_in_text(self, text: str, search_term: str) -> bool:
        """Case-insensitive text search"""
        if not text or not search_term:
            return False
        return search_term.lower() in text.lower()

    def _check_date_range(self, file_data: Dict, date_from: str, date_to: str) -> bool:
        """Check if file date is within range"""
        try:
            # Try different date fields
            file_date_str = file_data.get('date_taken') or \
                           file_data.get('date_created') or \
                           file_data.get('date_modified')

            if not file_date_str:
                return False

            # Parse dates
            file_date = datetime.strptime(file_date_str[:10], "%Y-%m-%d")
            from_date = datetime.strptime(date_from, "%Y-%m-%d")
            to_date = datetime.strptime(date_to, "%Y-%m-%d")

            return from_date <= file_date <= to_date

        except Exception as e:
            self.logger.debug(f"Date parsing error: {e}")
            return False

    def search_with_face_match(self, case_id: int, search_params: Dict, face_matcher) -> List[Dict]:
        """
        Enhanced search with face matching

        Args:
            case_id: Case ID
            search_params: Search parameters
            face_matcher: FaceMatcher instance with loaded suspect photo

        Returns:
            List of matching files
        """
        # First do regular search
        results = self.search(case_id, search_params)

        # If suspect photo provided, also search by face
        if search_params.get('suspect_photo') and face_matcher:
            self.logger.info("Performing face matching search")

            # Get all image files from case
            all_images = [f for f in self.file_repo.get_files_by_case(case_id)
                         if f['file_type'] == 'image']

            for img_data in all_images:
                try:
                    file_path = Path(img_data['file_path'])
                    match_result = face_matcher.match_faces_in_image(file_path)

                    if match_result['has_match']:
                        # Add to results if not already there
                        if img_data['file_id'] not in [r['file_id'] for r in results]:
                            img_data['match_details'] = {
                                'is_match': True,
                                'match_count': 1,
                                'matches': [f"Face match: {match_result['confidence']:.1f}% confidence"]
                            }
                            img_data['face_match_confidence'] = match_result['confidence']
                            results.append(img_data)
                        else:
                            # Add face match info to existing result
                            for r in results:
                                if r['file_id'] == img_data['file_id']:
                                    r['match_details']['matches'].append(
                                        f"Face match: {match_result['confidence']:.1f}% confidence"
                                    )
                                    r['match_details']['match_count'] += 1
                                    r['face_match_confidence'] = match_result['confidence']

                except Exception as e:
                    self.logger.error(f"Face matching error for {img_data['file_name']}: {e}")

        # Re-sort by relevance
        results.sort(key=lambda x: x['match_details']['match_count'], reverse=True)

        return results
