"""
Generic CSV Parser for Forenstiq Lab Intelligence
Parses CSV exports from various sources (call logs, contacts, SMS exports, etc.)

Handles:
- Call log CSV exports
- Contact CSV exports
- SMS/Message CSV exports
- Generic tabular data
"""

import csv
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import re
# from database.models import MessageType, CallType  # ORM not used - using repositories
# Message and call type constants (replacing non-existent ORM enums)
class MessageType:
    TEXT = type('MessageType', (), {'value': 'text'})()
    IMAGE = type('MessageType', (), {'value': 'image'})()
    AUDIO = type('MessageType', (), {'value': 'audio'})()
    VIDEO = type('MessageType', (), {'value': 'video'})()
    OTHER = type('MessageType', (), {'value': 'other'})()

class CallType:
    VOICE_CALL = type('CallType', (), {'value': 'voice_call'})()
    VIDEO_CALL = type('CallType', (), {'value': 'video_call'})()
    INCOMING = type('CallType', (), {'value': 'incoming'})()
    OUTGOING = type('CallType', (), {'value': 'outgoing'})()
    MISSED = type('CallType', (), {'value': 'missed'})()


class CSVParser:
    """
    Generic CSV parser with intelligent column mapping

    Auto-detects data type based on columns:
    - Contacts (name, phone, email columns)
    - Call Logs (duration, call type columns)
    - Messages (message, text, content columns)
    - Generic data (everything else)
    """

    def __init__(
        self,
        csv_path: str,
        data_type: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """
        Initialize CSV parser

        Args:
            csv_path: Path to CSV file
            data_type: Optional hint for data type ('contacts', 'calls', 'messages', 'generic')
            progress_callback: Optional callback for progress updates
        """
        self.csv_path = Path(csv_path)
        self.data_type = data_type
        self.progress_callback = progress_callback

        self.contacts = []
        self.messages = []
        self.call_logs = []
        self.generic_data = []

    def _update_progress(self, percent: int, message: str):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(percent, message)

    def validate_file(self) -> bool:
        """
        Validate that the file is a valid CSV

        Returns:
            bool: True if valid, False otherwise
        """
        if not self.csv_path.exists():
            return False

        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Try to read first few lines
                sample = f.read(1024)

                # Check if it looks like CSV
                dialect = csv.Sniffer().sniff(sample)
                return True

        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def parse(self) -> Dict[str, Any]:
        """
        Parse the CSV file

        Returns:
            dict: Parsed data
        """
        self._update_progress(0, "Starting CSV parse...")

        # Auto-detect data type if not specified
        if not self.data_type:
            self.data_type = self._detect_data_type()

        self._update_progress(10, f"Detected data type: {self.data_type}")

        # Parse based on type
        if self.data_type == 'contacts':
            self._parse_contacts()
        elif self.data_type == 'calls':
            self._parse_call_logs()
        elif self.data_type == 'messages':
            self._parse_messages()
        else:
            self._parse_generic()

        # Build summary
        summary = {
            'contacts': len(self.contacts),
            'messages': len(self.messages),
            'call_logs': len(self.call_logs),
            'generic_rows': len(self.generic_data)
        }

        self._update_progress(100, "CSV parsing complete!")

        return {
            'contacts': self.contacts,
            'messages': self.messages,
            'call_logs': self.call_logs,
            'generic_data': self.generic_data,
            'summary': summary,
            'source': 'csv',
            'data_type': self.data_type,
            'source_file': str(self.csv_path)
        }

    def _detect_data_type(self) -> str:
        """Auto-detect CSV data type based on column headers"""
        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                headers = [h.lower() if h else '' for h in reader.fieldnames or []]

                # Check for contact indicators
                contact_keywords = ['name', 'phone', 'email', 'contact']
                if any(any(kw in h for kw in contact_keywords) for h in headers):
                    return 'contacts'

                # Check for call log indicators
                call_keywords = ['duration', 'call', 'caller', 'type']
                if any(any(kw in h for kw in call_keywords) for h in headers):
                    return 'calls'

                # Check for message indicators
                message_keywords = ['message', 'text', 'content', 'body', 'sms']
                if any(any(kw in h for kw in message_keywords) for h in headers):
                    return 'messages'

                return 'generic'

        except Exception as e:
            print(f"Error detecting data type: {e}")
            return 'generic'

    def _parse_contacts(self):
        """Parse CSV as contacts"""
        self._update_progress(20, "Parsing contacts from CSV...")

        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                headers = [h.lower() if h else '' for h in reader.fieldnames or []]

                # Map common column name variations
                name_cols = ['name', 'contact_name', 'display_name', 'full_name']
                phone_cols = ['phone', 'phone_number', 'mobile', 'number', 'contact_number']
                email_cols = ['email', 'email_address', 'mail']

                # Find actual columns
                name_col = next((h for h in headers if any(nc in h for nc in name_cols)), None)
                phone_col = next((h for h in headers if any(pc in h for pc in phone_cols)), None)
                email_col = next((h for h in headers if any(ec in h for ec in email_cols)), None)

                rows = list(reader)
                total = len(rows)

                for idx, row in enumerate(rows):
                    if idx % 50 == 0:
                        progress = 20 + int((idx / total) * 60)
                        self._update_progress(progress, f"Parsing contact {idx}/{total}...")

                    # Get original case keys
                    orig_keys = {k.lower(): k for k in row.keys()}

                    contact = {}

                    if name_col:
                        contact['name'] = row.get(orig_keys.get(name_col, ''), '').strip()

                    if phone_col:
                        phone = row.get(orig_keys.get(phone_col, ''), '').strip()
                        # Clean phone number
                        phone = re.sub(r'[^\d+]', '', phone)
                        contact['phone_number'] = phone

                    if email_col:
                        contact['email'] = row.get(orig_keys.get(email_col, ''), '').strip()

                    # Add other fields
                    for key, value in row.items():
                        if key.lower() not in [name_col, phone_col, email_col]:
                            contact[key] = value

                    if contact.get('phone_number') or contact.get('name'):
                        self.contacts.append(contact)

        except Exception as e:
            print(f"Error parsing contacts: {e}")
            raise

    def _parse_call_logs(self):
        """Parse CSV as call logs"""
        self._update_progress(20, "Parsing call logs from CSV...")

        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                headers = [h.lower() if h else '' for h in reader.fieldnames or []]

                # Map column names
                phone_cols = ['phone', 'number', 'caller', 'contact']
                duration_cols = ['duration', 'length', 'time']
                type_cols = ['type', 'call_type', 'direction']
                timestamp_cols = ['date', 'time', 'timestamp', 'datetime']

                phone_col = next((h for h in headers if any(pc in h for pc in phone_cols)), None)
                duration_col = next((h for h in headers if any(dc in h for dc in duration_cols)), None)
                type_col = next((h for h in headers if any(tc in h for tc in type_cols)), None)
                timestamp_col = next((h for h in headers if any(tsc in h for tsc in timestamp_cols)), None)

                rows = list(reader)
                total = len(rows)

                for idx, row in enumerate(rows):
                    if idx % 50 == 0:
                        progress = 20 + int((idx / total) * 60)
                        self._update_progress(progress, f"Parsing call {idx}/{total}...")

                    orig_keys = {k.lower(): k for k in row.keys()}

                    call = {}

                    if phone_col:
                        phone = row.get(orig_keys.get(phone_col, ''), '').strip()
                        phone = re.sub(r'[^\d+]', '', phone)
                        call['phone_number'] = phone

                    if duration_col:
                        duration = row.get(orig_keys.get(duration_col, ''), '0').strip()
                        # Extract numeric duration
                        duration_match = re.search(r'\d+', duration)
                        call['duration'] = int(duration_match.group()) if duration_match else 0

                    if type_col:
                        call_type = row.get(orig_keys.get(type_col, ''), '').strip().lower()
                        if 'incoming' in call_type or 'received' in call_type:
                            call['direction'] = 'incoming'
                        elif 'outgoing' in call_type or 'dialed' in call_type:
                            call['direction'] = 'outgoing'
                        elif 'missed' in call_type:
                            call['direction'] = 'missed'
                        else:
                            call['direction'] = 'unknown'

                        if 'video' in call_type:
                            call['call_type'] = CallType.VIDEO_CALL.value
                        else:
                            call['call_type'] = CallType.VOICE_CALL.value
                    else:
                        call['call_type'] = CallType.VOICE_CALL.value
                        call['direction'] = 'unknown'

                    if timestamp_col:
                        timestamp_str = row.get(orig_keys.get(timestamp_col, ''), '').strip()
                        call['timestamp'] = self._parse_timestamp(timestamp_str)
                    else:
                        call['timestamp'] = datetime.now().isoformat()

                    if call.get('phone_number'):
                        self.call_logs.append(call)

        except Exception as e:
            print(f"Error parsing call logs: {e}")
            raise

    def _parse_messages(self):
        """Parse CSV as messages"""
        self._update_progress(20, "Parsing messages from CSV...")

        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                headers = [h.lower() if h else '' for h in reader.fieldnames or []]

                # Map columns
                phone_cols = ['phone', 'number', 'sender', 'recipient', 'contact']
                message_cols = ['message', 'text', 'content', 'body', 'sms']
                direction_cols = ['direction', 'type', 'status']
                timestamp_cols = ['date', 'time', 'timestamp', 'datetime']

                phone_col = next((h for h in headers if any(pc in h for pc in phone_cols)), None)
                message_col = next((h for h in headers if any(mc in h for mc in message_cols)), None)
                direction_col = next((h for h in headers if any(dc in h for dc in direction_cols)), None)
                timestamp_col = next((h for h in headers if any(tsc in h for tsc in timestamp_cols)), None)

                rows = list(reader)
                total = len(rows)

                for idx, row in enumerate(rows):
                    if idx % 50 == 0:
                        progress = 20 + int((idx / total) * 60)
                        self._update_progress(progress, f"Parsing message {idx}/{total}...")

                    orig_keys = {k.lower(): k for k in row.keys()}

                    message = {}

                    if phone_col:
                        phone = row.get(orig_keys.get(phone_col, ''), '').strip()
                        phone = re.sub(r'[^\d+]', '', phone)
                        message['phone_number'] = phone

                    if message_col:
                        message['content'] = row.get(orig_keys.get(message_col, ''), '').strip()

                    if direction_col:
                        direction = row.get(orig_keys.get(direction_col, ''), '').strip().lower()
                        if 'incoming' in direction or 'received' in direction or 'inbox' in direction:
                            message['direction'] = 'incoming'
                        elif 'outgoing' in direction or 'sent' in direction or 'outbox' in direction:
                            message['direction'] = 'outgoing'
                        else:
                            message['direction'] = 'unknown'
                    else:
                        message['direction'] = 'incoming'

                    if timestamp_col:
                        timestamp_str = row.get(orig_keys.get(timestamp_col, ''), '').strip()
                        message['timestamp'] = self._parse_timestamp(timestamp_str)
                    else:
                        message['timestamp'] = datetime.now().isoformat()

                    message['message_type'] = MessageType.TEXT.value

                    if message.get('phone_number') and message.get('content'):
                        self.messages.append(message)

        except Exception as e:
            print(f"Error parsing messages: {e}")
            raise

    def _parse_generic(self):
        """Parse CSV as generic data"""
        self._update_progress(20, "Parsing generic CSV data...")

        try:
            with open(self.csv_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)

                rows = list(reader)
                total = len(rows)

                for idx, row in enumerate(rows):
                    if idx % 100 == 0:
                        progress = 20 + int((idx / total) * 60)
                        self._update_progress(progress, f"Parsing row {idx}/{total}...")

                    self.generic_data.append(dict(row))

        except Exception as e:
            print(f"Error parsing generic CSV: {e}")
            raise

    def _parse_timestamp(self, timestamp_str: str) -> str:
        """Parse various timestamp formats"""
        if not timestamp_str:
            return datetime.now().isoformat()

        # Try common formats
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d-%m-%Y %H:%M:%S',
            '%d-%m-%Y %H:%M',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        # If nothing works, return current time
        return datetime.now().isoformat()


if __name__ == "__main__":
    # Test parser
    import sys

    if len(sys.argv) < 2:
        print("Usage: python csv_parser.py <file.csv> [type]")
        print("Types: contacts, calls, messages, generic")
        sys.exit(1)

    csv_file = sys.argv[1]
    data_type = sys.argv[2] if len(sys.argv) > 2 else None

    parser = CSVParser(csv_file, data_type, lambda p, m: print(f"[{p}%] {m}"))

    if parser.validate_file():
        print("✓ Valid CSV file")
        data = parser.parse()
        print(f"\nParsed ({data['data_type']}):")
        print(f"  - {data['summary']['contacts']} contacts")
        print(f"  - {data['summary']['messages']} messages")
        print(f"  - {data['summary']['call_logs']} calls")
        print(f"  - {data['summary']['generic_rows']} generic rows")
    else:
        print("✗ Invalid CSV file")
