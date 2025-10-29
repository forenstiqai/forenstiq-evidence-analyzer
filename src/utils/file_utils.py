"""
File system utilities
"""
import os
import hashlib
from pathlib import Path
from typing import List, Optional

def get_file_hash(file_path: Path, algorithm='sha256') -> str:
    """
    Calculate file hash
    
    Args:
        file_path: Path to file
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
    
    Returns:
        Hexadecimal hash string
    """
    hash_func = hashlib.new(algorithm)
    
    with open(file_path, 'rb') as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)


def is_image_file(file_path: Path) -> bool:
    """Check if file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                       '.tiff', '.tif', '.webp', '.heic', '.heif'}
    return file_path.suffix.lower() in image_extensions


def is_video_file(file_path: Path) -> bool:
    """Check if file is a video"""
    video_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.flv',
                       '.mkv', '.webm', '.m4v', '.mpeg', '.mpg'}
    return file_path.suffix.lower() in video_extensions


def is_document_file(file_path: Path) -> bool:
    """Check if file is a document"""
    document_extensions = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.txt', '.rtf', '.csv', '.pages',
        '.numbers', '.keynote'
    }
    return file_path.suffix.lower() in document_extensions


def is_audio_file(file_path: Path) -> bool:
    """Check if file is an audio file"""
    audio_extensions = {
        '.mp3', '.wav', '.aac', '.flac', '.m4a', '.wma', '.ogg',
        '.opus', '.aiff', '.ape', '.alac'
    }
    return file_path.suffix.lower() in audio_extensions


def is_archive_file(file_path: Path) -> bool:
    """Check if file is an archive/compressed file"""
    archive_extensions = {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz',
        '.tar.gz', '.tgz', '.tar.bz2', '.tbz2'
    }
    return file_path.suffix.lower() in archive_extensions


def is_database_file(file_path: Path) -> bool:
    """Check if file is a database file"""
    db_extensions = {
        '.db', '.sqlite', '.sqlite3', '.sql', '.mdb', '.accdb',
        '.dbf', '.pdb', '.frm', '.ibd'
    }
    return file_path.suffix.lower() in db_extensions


def is_code_file(file_path: Path) -> bool:
    """Check if file is source code"""
    code_extensions = {
        '.py', '.java', '.cpp', '.c', '.h', '.js', '.ts', '.jsx',
        '.tsx', '.php', '.rb', '.go', '.rs', '.swift', '.kt',
        '.html', '.css', '.scss', '.sass', '.xml', '.json', '.yaml',
        '.yml', '.sh', '.bat', '.ps1'
    }
    return file_path.suffix.lower() in code_extensions


def is_executable_file(file_path: Path) -> bool:
    """Check if file is executable"""
    executable_extensions = {
        '.exe', '.dll', '.app', '.apk', '.ipa', '.deb', '.rpm',
        '.dmg', '.pkg', '.msi', '.bin', '.so', '.dylib'
    }
    return file_path.suffix.lower() in executable_extensions


def is_email_file(file_path: Path) -> bool:
    """Check if file is an email file"""
    email_extensions = {
        '.eml', '.msg', '.pst', '.ost', '.mbox', '.emlx'
    }
    return file_path.suffix.lower() in email_extensions


def is_system_file(file_path: Path) -> bool:
    """Check if file is a system/config file"""
    system_extensions = {
        '.log', '.ini', '.cfg', '.conf', '.reg', '.plist',
        '.dat', '.tmp', '.bak', '.sys'
    }
    return file_path.suffix.lower() in system_extensions


def get_file_category(file_path: Path) -> str:
    """
    Determine the forensic category of a file
    Enhanced detection for 27 evidence types based on 2024-2025 police seizure patterns

    Returns:
        Category string: 'messaging', 'messages', 'calls', 'social_media',
        'banking', 'cryptocurrency', 'image', 'video', 'cctv', 'document',
        'contacts', 'location', 'browser', 'cloud', 'database', 'archive',
        'memory', 'network', 'sim_data', 'fraud_device', 'iot', 'encrypted',
        'audio', 'email', 'executable', 'system', 'other'
    """
    filename = file_path.name.lower()
    parent_folder = file_path.parent.name.lower()

    # Priority 1: Communication Evidence - Messaging Apps (WhatsApp, Telegram, Signal)
    if (filename in ['msgstore.db', 'wa.db', 'msgstore.db.crypt14', 'msgstore.db.crypt15'] or
        'whatsapp' in filename or 'whatsapp' in parent_folder or
        'telegram' in filename or 'telegram' in parent_folder or
        'signal' in filename or 'signal' in parent_folder or
        'viber' in filename or 'wechat' in filename):
        return 'messaging'

    # Priority 1: SMS/Messages (text messages, MMS)
    if (filename in ['mmssms.db', 'sms.db', 'messages.db'] or
        'sms' in filename or 'mms' in filename or 'messages' in parent_folder):
        return 'messages'

    # Priority 1: Call Logs (CDR - Call Detail Records)
    if (filename in ['calls.db', 'call_log.db', 'calllog.db'] or
        'call' in filename and '.db' in filename or
        'cdr' in filename or filename.endswith('.cdr')):
        return 'calls'

    # Priority 1: Social Media (Facebook, Instagram, Twitter, Snapchat)
    if ('facebook' in filename or 'facebook' in parent_folder or
        'instagram' in filename or 'instagram' in parent_folder or
        'twitter' in filename or 'twitter' in parent_folder or
        'snapchat' in filename or 'snapchat' in parent_folder or
        'tiktok' in filename or 'linkedin' in filename or
        'social' in parent_folder):
        return 'social_media'

    # Priority 2: Banking/UPI Data (traditional finance)
    if ('upi' in filename or 'banking' in filename or 'bank' in filename or
        'paytm' in filename or 'phonepe' in filename or 'googlepay' in filename or
        'bhim' in filename or 'transaction' in filename or
        parent_folder in ['banking', 'upi', 'payments']):
        return 'banking'

    # Priority 2: Cryptocurrency (Bitcoin, Ethereum, wallets, blockchain)
    if ('wallet' in filename and file_path.suffix.lower() in ['.dat', '.wallet', '.json'] or
        'bitcoin' in filename or 'ethereum' in filename or 'crypto' in filename or
        'blockchain' in filename or parent_folder in ['crypto', 'cryptocurrency', 'wallets']):
        return 'cryptocurrency'

    # Priority 3: CCTV/Surveillance (DVR exports, separate from personal videos)
    if ('cctv' in filename or 'cctv' in parent_folder or
        'dvr' in filename or 'dvr' in parent_folder or
        'surveillance' in filename or 'surveillance' in parent_folder or
        'nvr' in filename or parent_folder in ['cctv', 'dvr', 'surveillance', 'cameras']):
        return 'cctv'

    # Priority 5: Contacts (phone book, address book)
    if (filename in ['contacts.db', 'contacts2.db', 'phonebook.db'] or
        'contact' in filename and '.db' in filename or
        parent_folder == 'contacts'):
        return 'contacts'

    # Priority 5: Location/GPS Data (movement tracking, geolocation)
    if (filename.endswith('.gpx') or filename.endswith('.kml') or
        filename.endswith('.kmz') or 'gps' in filename or
        'location' in filename or 'geolocation' in filename or
        parent_folder in ['gps', 'location', 'tracks']):
        return 'location'

    # Priority 6: Browser Data (history, cookies, cache, passwords)
    if (filename in ['history', 'cookies', 'cache', 'login data', 'preferences'] or
        'browser' in parent_folder or parent_folder in ['chrome', 'firefox', 'safari', 'edge'] or
        'history' in filename and '.db' in filename):
        return 'browser'

    # Priority 6: Cloud Storage (Google Drive, Dropbox, iCloud exports)
    if ('googledrive' in filename or 'google drive' in parent_folder or
        'dropbox' in filename or 'dropbox' in parent_folder or
        'icloud' in filename or 'icloud' in parent_folder or
        'onedrive' in filename or 'onedrive' in parent_folder or
        parent_folder in ['cloud', 'google drive', 'dropbox', 'icloud', 'onedrive']):
        return 'cloud'

    # Priority 7: Memory/Volatile Data (RAM dumps, live forensics)
    if (file_path.suffix.lower() in ['.raw', '.mem', '.dmp', '.vmem'] or
        'memory' in filename or 'memdump' in filename or 'ram' in filename or
        parent_folder in ['memory', 'dumps', 'ramdump']):
        return 'memory'

    # Priority 8: Network Logs (router logs, connection logs)
    if (('router' in filename or 'network' in filename or 'dns' in filename) or
        parent_folder in ['router', 'network', 'logs', 'pcap'] or
        file_path.suffix.lower() in ['.pcap', '.pcapng']):
        return 'network'

    # Priority 8: SIM Card Data (SIM dumps, ICCID, IMSI)
    if ('sim' in filename and '.bin' in filename or
        'iccid' in filename or 'imsi' in filename or
        parent_folder == 'sim'):
        return 'sim_data'

    # Priority 8: Fraud Device Data (SIM box, GSM gateway, skimmers)
    if ('simbox' in filename or 'gsm' in filename or 'skimmer' in filename or
        parent_folder in ['simbox', 'gsm_gateway', 'fraud']):
        return 'fraud_device'

    # Priority 10: Smart Devices/IoT (smartwatch, fitness tracker, vehicle data)
    if (file_path.suffix.lower() in ['.fit', '.tcx'] or
        'garmin' in filename or 'fitbit' in filename or 'smartwatch' in filename or
        'vehicle' in filename or 'infotainment' in filename or
        parent_folder in ['smartwatch', 'fitness', 'vehicle', 'iot', 'wearables']):
        return 'iot'

    # Priority 10: Encrypted/Protected Files (encrypted containers, password-protected)
    if (file_path.suffix.lower() in ['.encrypted', '.enc', '.tc', '.hc'] or
        'encrypted' in filename or 'truecrypt' in filename or 'veracrypt' in filename):
        return 'encrypted'

    # Extension-based detection for standard categories
    if is_image_file(file_path):
        return 'image'
    elif is_video_file(file_path):
        return 'video'
    elif is_document_file(file_path):
        return 'document'
    elif is_audio_file(file_path):
        return 'audio'
    elif is_archive_file(file_path):
        return 'archive'
    elif is_database_file(file_path):
        return 'database'
    elif is_code_file(file_path):
        return 'code'
    elif is_executable_file(file_path):
        return 'executable'
    elif is_email_file(file_path):
        return 'email'
    elif is_system_file(file_path):
        return 'system'
    else:
        return 'other'


def scan_directory(directory: Path, 
                   recursive: bool = True,
                   extensions: Optional[List[str]] = None) -> List[Path]:
    """
    Scan directory for files
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        extensions: List of file extensions to include (e.g., ['.jpg', '.png'])
    
    Returns:
        List of file paths
    """
    files = []
    
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = Path(root) / filename
            if extensions is None or file_path.suffix.lower() in extensions:
                files.append(file_path)
        if not recursive:
            break
    
    return files


def safe_filename(filename: str) -> str:
    """
    Convert filename to safe version (remove illegal characters)
    """
    # Characters not allowed in Windows filenames
    illegal_chars = '<>:"/\\|?*'
    
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    
    return filename


def ensure_directory(directory: Path):
    """Create directory if it doesn't exist"""
    directory.mkdir(parents=True, exist_ok=True)


def get_relative_path(file_path: Path, base_path: Path) -> Path:
    """Get relative path from base path"""
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        return file_path


def cleanup_temp_directory():
    """Clean up temporary extraction directory"""
    import shutil
    from .logger import get_logger

    temp_dir = Path('temp')

    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
            logger = get_logger()
            logger.info("Temp directory cleaned")
            return True
        except Exception as e:
            logger = get_logger()
            logger.error(f"Failed to clean temp directory: {e}")
            return False
    return True


def get_temp_file_path(filename: str) -> Path:
    """Get a temporary file path for extraction"""
    from datetime import datetime

    temp_dir = Path('temp')
    temp_dir.mkdir(exist_ok=True)

    # Create unique subdirectory using timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    extract_dir = temp_dir / timestamp
    extract_dir.mkdir(exist_ok=True)

    return extract_dir / filename