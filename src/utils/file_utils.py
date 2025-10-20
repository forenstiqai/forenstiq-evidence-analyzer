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
    Determine the category of a file

    Returns:
        Category string: 'image', 'video', 'document', 'audio', 'archive',
        'database', 'code', 'executable', 'email', 'system', 'other'
    """
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