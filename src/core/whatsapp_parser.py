"""
WhatsApp Database Parser for Forenstiq Lab Intelligence
Parses WhatsApp msgstore.db and wa.db files directly from phone extractions

This parser handles:
- Messages from msgstore.db
- Contacts from wa.db
- Media references
- Group chats
- Call logs (if available)
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
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


class WhatsAppParser:
    """
    Parser for WhatsApp database files extracted from Android devices

    Supports:
    - msgstore.db (encrypted and unencrypted)
    - wa.db (contacts database)
    - Media file references
    """

    def __init__(
        self,
        db_path: str,
        wa_db_path: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """
        Initialize WhatsApp parser

        Args:
            db_path: Path to msgstore.db file
            wa_db_path: Optional path to wa.db file for contacts
            progress_callback: Optional callback for progress updates
        """
        self.db_path = Path(db_path)
        self.wa_db_path = Path(wa_db_path) if wa_db_path else None
        self.progress_callback = progress_callback

        self.messages = []
        self.contacts = []
        self.call_logs = []
        self.media_files = []

    def _update_progress(self, percent: int, message: str):
        """Update progress if callback is provided"""
        if self.progress_callback:
            self.progress_callback(percent, message)

    def validate_file(self) -> bool:
        """
        Validate that the file is a valid WhatsApp database

        Returns:
            bool: True if valid, False otherwise
        """
        if not self.db_path.exists():
            return False

        # Check if it's a SQLite database
        try:
            with open(self.db_path, 'rb') as f:
                header = f.read(16)
                # SQLite database file header
                if not header.startswith(b'SQLite format 3'):
                    return False

            # Try to connect and check for WhatsApp tables
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Check for common WhatsApp tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND "
                "(name='messages' OR name='message' OR name='chat')"
            )

            tables = cursor.fetchall()
            conn.close()

            return len(tables) > 0

        except Exception as e:
            print(f"Validation error: {e}")
            return False

    def parse(self) -> Dict[str, Any]:
        """
        Parse the WhatsApp database

        Returns:
            dict: Parsed data containing messages, contacts, etc.
        """
        self._update_progress(0, "Starting WhatsApp database parse...")

        # Parse main database
        self._parse_msgstore()

        # Parse contacts if wa.db is provided
        if self.wa_db_path and self.wa_db_path.exists():
            self._parse_wa_db()

        # Build summary
        summary = {
            'contacts': len(self.contacts),
            'messages': len(self.messages),
            'call_logs': len(self.call_logs),
            'media': len(self.media_files)
        }

        self._update_progress(100, "WhatsApp parsing complete!")

        return {
            'contacts': self.contacts,
            'messages': self.messages,
            'call_logs': self.call_logs,
            'media': self.media_files,
            'summary': summary,
            'source': 'whatsapp_db',
            'source_file': str(self.db_path)
        }

    def _parse_msgstore(self):
        """Parse msgstore.db for messages and media"""
        self._update_progress(10, "Parsing WhatsApp messages...")

        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Get table structure first
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            # Different WhatsApp versions have different schemas
            if 'message' in tables:
                self._parse_message_table(cursor)
            elif 'messages' in tables:
                self._parse_messages_table(cursor)

            # Parse call logs if available
            if 'call_log' in tables:
                self._parse_call_log_table(cursor)

            conn.close()

        except Exception as e:
            print(f"Error parsing msgstore: {e}")
            raise

    def _parse_message_table(self, cursor):
        """Parse 'message' table (newer WhatsApp schema)"""
        self._update_progress(20, "Reading messages from database...")

        try:
            # Query messages
            cursor.execute("""
                SELECT
                    _id,
                    key_remote_jid,
                    key_from_me,
                    data,
                    timestamp,
                    media_wa_type,
                    media_mime_type,
                    media_name,
                    media_caption,
                    thumb_image
                FROM message
                ORDER BY timestamp ASC
            """)

            rows = cursor.fetchall()
            total = len(rows)

            for idx, row in enumerate(rows):
                # Update progress
                if idx % 100 == 0:
                    progress = 20 + int((idx / total) * 40)
                    self._update_progress(progress, f"Parsing message {idx}/{total}...")

                message = self._parse_message_row(row)
                if message:
                    self.messages.append(message)

        except Exception as e:
            print(f"Error parsing message table: {e}")

    def _parse_messages_table(self, cursor):
        """Parse 'messages' table (older WhatsApp schema)"""
        self._update_progress(20, "Reading messages from database...")

        try:
            cursor.execute("""
                SELECT * FROM messages
                ORDER BY timestamp ASC
            """)

            rows = cursor.fetchall()
            total = len(rows)

            for idx, row in enumerate(rows):
                if idx % 100 == 0:
                    progress = 20 + int((idx / total) * 40)
                    self._update_progress(progress, f"Parsing message {idx}/{total}...")

                message = self._parse_message_row(row)
                if message:
                    self.messages.append(message)

        except Exception as e:
            print(f"Error parsing messages table: {e}")

    def _parse_message_row(self, row: sqlite3.Row) -> Optional[Dict]:
        """Parse a single message row"""
        try:
            # Extract phone number from JID
            jid = row['key_remote_jid'] if 'key_remote_jid' in row.keys() else row.get('jid', '')
            phone_number = jid.split('@')[0] if '@' in jid else jid

            # Determine message direction
            from_me = row.get('key_from_me', 0) == 1
            direction = 'outgoing' if from_me else 'incoming'

            # Get message content
            content = row.get('data', '') or row.get('text_data', '') or ''

            # Get timestamp (WhatsApp uses milliseconds)
            timestamp = row.get('timestamp', 0)
            if timestamp:
                # Convert from milliseconds to seconds
                dt = datetime.fromtimestamp(timestamp / 1000.0)
            else:
                dt = datetime.now()

            # Determine message type
            media_type = row.get('media_wa_type', 0)
            if media_type == 0:
                msg_type = MessageType.TEXT
            elif media_type == 1:
                msg_type = MessageType.IMAGE
            elif media_type == 2:
                msg_type = MessageType.AUDIO
            elif media_type == 3:
                msg_type = MessageType.VIDEO
            else:
                msg_type = MessageType.OTHER

            # Handle media
            if media_type > 0:
                media_name = row.get('media_name', '') or row.get('media_url', '')
                media_caption = row.get('media_caption', '')

                if media_name:
                    self.media_files.append({
                        'filename': media_name,
                        'type': msg_type.value,
                        'mime_type': row.get('media_mime_type', ''),
                        'caption': media_caption,
                        'timestamp': dt.isoformat()
                    })

                # Use caption as content if no text
                if media_caption and not content:
                    content = f"[Media: {media_caption}]"
                elif not content:
                    content = f"[{msg_type.value.upper()}]"

            # Build contact info
            contact = {
                'name': phone_number,  # Will be enriched from contacts
                'phone_number': phone_number,
                'jid': jid
            }

            # Add to contacts list if not already there
            if not any(c['phone_number'] == phone_number for c in self.contacts):
                self.contacts.append(contact)

            return {
                'id': row.get('_id', ''),
                'phone_number': phone_number,
                'direction': direction,
                'content': content,
                'timestamp': dt.isoformat(),
                'message_type': msg_type.value,
                'read_status': row.get('read_device_timestamp', 0) > 0
            }

        except Exception as e:
            print(f"Error parsing message row: {e}")
            return None

    def _parse_call_log_table(self, cursor):
        """Parse call log table"""
        self._update_progress(60, "Parsing call logs...")

        try:
            cursor.execute("""
                SELECT * FROM call_log
                ORDER BY timestamp DESC
            """)

            rows = cursor.fetchall()

            for row in rows:
                jid = row.get('jid', '')
                phone_number = jid.split('@')[0] if '@' in jid else jid

                timestamp = row.get('timestamp', 0)
                dt = datetime.fromtimestamp(timestamp / 1000.0) if timestamp else datetime.now()

                # Determine call type
                video_call = row.get('video_call', 0) == 1
                from_me = row.get('from_me', 0) == 1

                if video_call:
                    call_type = CallType.VIDEO_CALL
                else:
                    call_type = CallType.VOICE_CALL

                duration = row.get('duration', 0)

                self.call_logs.append({
                    'phone_number': phone_number,
                    'call_type': call_type.value,
                    'direction': 'outgoing' if from_me else 'incoming',
                    'duration': duration,
                    'timestamp': dt.isoformat()
                })

        except Exception as e:
            print(f"Error parsing call logs: {e}")

    def _parse_wa_db(self):
        """Parse wa.db for contact information"""
        self._update_progress(70, "Parsing WhatsApp contacts...")

        try:
            conn = sqlite3.connect(str(self.wa_db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Check for contact table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wa_contacts'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT
                        jid,
                        display_name,
                        number,
                        status,
                        status_timestamp
                    FROM wa_contacts
                """)

                for row in cursor.fetchall():
                    jid = row['jid']
                    phone_number = jid.split('@')[0] if '@' in jid else row.get('number', jid)

                    contact = {
                        'name': row.get('display_name', phone_number),
                        'phone_number': phone_number,
                        'jid': jid,
                        'status': row.get('status', ''),
                        'last_seen': row.get('status_timestamp', '')
                    }

                    # Update existing contact or add new
                    existing = next((c for c in self.contacts if c['phone_number'] == phone_number), None)
                    if existing:
                        existing.update(contact)
                    else:
                        self.contacts.append(contact)

            conn.close()

        except Exception as e:
            print(f"Error parsing wa.db: {e}")


if __name__ == "__main__":
    # Test parser
    import sys

    if len(sys.argv) < 2:
        print("Usage: python whatsapp_parser.py <msgstore.db> [wa.db]")
        sys.exit(1)

    msgstore = sys.argv[1]
    wa_db = sys.argv[2] if len(sys.argv) > 2 else None

    parser = WhatsAppParser(msgstore, wa_db, lambda p, m: print(f"[{p}%] {m}"))

    if parser.validate_file():
        print("✓ Valid WhatsApp database")
        data = parser.parse()
        print(f"\nParsed:")
        print(f"  - {data['summary']['contacts']} contacts")
        print(f"  - {data['summary']['messages']} messages")
        print(f"  - {data['summary']['call_logs']} calls")
        print(f"  - {data['summary']['media']} media files")
    else:
        print("✗ Invalid WhatsApp database")
