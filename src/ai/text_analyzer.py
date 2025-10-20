"""
Text File Analyzer - Extract and analyze text from various file types
"""
from pathlib import Path
from typing import Dict
import json
import csv


class TextAnalyzer:
    """Analyze text files, logs, CSV, JSON, XML"""

    def __init__(self):
        pass

    def analyze_text_file(self, file_path: Path) -> Dict:
        """
        Analyze a text file (.txt, .log, .csv, .json, .xml, etc.)

        Returns:
            Dictionary with extracted data
        """
        result = {
            'has_content': False,
            'content': '',
            'line_count': 0,
            'word_count': 0,
            'file_type': file_path.suffix.lower(),
            'keywords': [],
            'parsed_data': None
        }

        try:
            # Read file with error handling for different encodings
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with latin-1 encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()

            if not content.strip():
                return result

            result['has_content'] = True
            result['content'] = content
            result['line_count'] = len(content.split('\n'))
            result['word_count'] = len(content.split())

            # Extract forensic keywords
            result['keywords'] = self._extract_keywords(content)

            # Try to parse structured data
            if file_path.suffix.lower() == '.json':
                result['parsed_data'] = self._parse_json(file_path)
            elif file_path.suffix.lower() == '.xml':
                result['parsed_data'] = self._parse_xml(content)
            elif file_path.suffix.lower() == '.csv':
                result['parsed_data'] = self._parse_csv(file_path)

        except Exception as e:
            result['error'] = str(e)

        return result

    def _extract_keywords(self, text: str) -> list:
        """Extract forensically relevant keywords"""
        keywords = []

        # Convert to lowercase for searching
        text_lower = text.lower()

        # Forensic keywords to search for
        keyword_categories = {
            'communication': ['email', 'phone', 'call', 'message', 'sms', 'chat', 'whatsapp'],
            'location': ['gps', 'latitude', 'longitude', 'location', 'address'],
            'identity': ['name', 'username', 'password', 'id', 'ssn', 'license'],
            'financial': ['credit card', 'bank', 'account', 'payment', 'transaction'],
            'network': ['ip address', 'mac address', 'url', 'domain', 'wifi'],
            'security': ['password', 'encryption', 'key', 'token', 'auth'],
            'temporal': ['date', 'time', 'timestamp', 'schedule'],
        }

        for category, terms in keyword_categories.items():
            for term in terms:
                if term in text_lower:
                    keywords.append(f"{category}:{term}")

        return list(set(keywords))  # Remove duplicates

    def _parse_json(self, file_path: Path) -> Dict:
        """Parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {
                'type': 'json',
                'keys': list(data.keys()) if isinstance(data, dict) else None,
                'item_count': len(data) if isinstance(data, (list, dict)) else 1
            }
        except:
            return None

    def _parse_xml(self, content: str) -> Dict:
        """Parse XML content (basic parsing)"""
        try:
            # Count elements
            element_count = content.count('<') // 2  # Rough estimate
            return {
                'type': 'xml',
                'element_count': element_count
            }
        except:
            return None

    def _parse_csv(self, file_path: Path) -> Dict:
        """Parse CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if rows:
                return {
                    'type': 'csv',
                    'row_count': len(rows),
                    'column_count': len(rows[0]) if rows else 0,
                    'headers': rows[0] if rows else []
                }
        except:
            return None

    def analyze_document(self, file_path: Path) -> Dict:
        """
        Analyze document files (.pdf, .docx, etc.)
        Note: This is a basic implementation. For full PDF parsing,
        you would need PyPDF2 or pdfplumber
        """
        result = {
            'has_content': False,
            'file_type': file_path.suffix.lower(),
            'analyzed': True,
            'method': 'basic'
        }

        # For now, just mark as analyzed
        # TODO: Implement PDF text extraction with PyPDF2
        # TODO: Implement DOCX parsing with python-docx

        result['note'] = 'Document imported but full text extraction requires additional libraries'

        return result
