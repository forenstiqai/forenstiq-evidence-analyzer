"""
Date and time utilities
"""
from datetime import datetime, date
from typing import Optional
from dateutil import parser

def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string to datetime object
    
    Handles various date formats automatically
    """
    if not date_string:
        return None
    
    try:
        return parser.parse(date_string)
    except Exception:
        return None


def format_datetime(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime object to string"""
    if dt is None:
        return ''
    return dt.strftime(format_str)


def parse_exif_date(exif_date: str) -> Optional[datetime]:
    """
    Parse EXIF date format to datetime
    
    EXIF format: 'YYYY:MM:DD HH:MM:SS'
    """
    if not exif_date:
        return None
    
    try:
        # Replace ':' with '-' in date part
        parts = exif_date.split(' ')
        if len(parts) == 2:
            date_part = parts[0].replace(':', '-')
            time_part = parts[1]
            datetime_str = f"{date_part} {time_part}"
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    except Exception:
        pass
    
    return None


def get_current_timestamp() -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def datetime_to_iso(dt: datetime) -> str:
    """Convert datetime to ISO format string"""
    if dt is None:
        return ''
    return dt.isoformat()


def iso_to_datetime(iso_string: str) -> Optional[datetime]:
    """Convert ISO format string to datetime"""
    if not iso_string:
        return None
    
    try:
        return datetime.fromisoformat(iso_string)
    except Exception:
        return None