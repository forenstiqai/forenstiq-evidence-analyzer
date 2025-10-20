"""
Extract metadata from image files (EXIF, GPS, etc.)
"""
from pathlib import Path
from typing import Dict, Optional
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import exifread
from datetime import datetime

class MetadataExtractor:
    """Extract metadata from image files"""
    
    def extract_metadata(self, image_path: Path) -> Dict:
        """
        Extract all available metadata from image
        
        Returns:
            Dictionary with metadata fields
        """
        metadata = {
            'date_created': None,
            'date_modified': None,
            'date_accessed': None,
            'date_taken': None,
            'camera_make': None,
            'camera_model': None,
            'gps_latitude': None,
            'gps_longitude': None,
            'gps_altitude': None,
            'image_width': None,
            'image_height': None,
            'orientation': None
        }

        try:
            # Get file system dates
            stat = image_path.stat()
            metadata['date_created'] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            metadata['date_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            metadata['date_accessed'] = datetime.fromtimestamp(stat.st_atime).isoformat()
            
            # Try PIL first
            pil_metadata = self._extract_pil(image_path)
            metadata.update(pil_metadata)
            
            # If GPS not found, try exifread (sometimes more reliable)
            if not metadata.get('gps_latitude'):
                exifread_metadata = self._extract_exifread(image_path)
                metadata.update(exifread_metadata)
            
        except Exception as e:
            print(f"Error extracting metadata from {image_path}: {e}")
        
        return metadata
    
    def _extract_pil(self, image_path: Path) -> Dict:
        """Extract metadata using PIL"""
        metadata = {}
        
        try:
            with Image.open(image_path) as img:
                # Image dimensions
                metadata['image_width'] = img.width
                metadata['image_height'] = img.height
                
                # EXIF data
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        
                        if tag == 'DateTime':
                            metadata['date_taken'] = self._parse_exif_datetime(value)
                        elif tag == 'Make':
                            metadata['camera_make'] = str(value).strip()
                        elif tag == 'Model':
                            metadata['camera_model'] = str(value).strip()
                        elif tag == 'Orientation':
                            metadata['orientation'] = value
                        elif tag == 'GPSInfo':
                            gps_data = self._parse_gps(value)
                            metadata.update(gps_data)
        
        except Exception as e:
            print(f"PIL extraction error: {e}")
        
        return metadata
    
    def _extract_exifread(self, image_path: Path) -> Dict:
        """Extract metadata using exifread library"""
        metadata = {}
        
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                
                # Date taken
                if 'EXIF DateTimeOriginal' in tags:
                    metadata['date_taken'] = self._parse_exif_datetime(
                        str(tags['EXIF DateTimeOriginal'])
                    )
                
                # Camera info
                if 'Image Make' in tags:
                    metadata['camera_make'] = str(tags['Image Make']).strip()
                if 'Image Model' in tags:
                    metadata['camera_model'] = str(tags['Image Model']).strip()
                
                # GPS coordinates
                gps_lat = self._get_gps_coordinate(tags, 'GPS GPSLatitude', 
                                                   'GPS GPSLatitudeRef')
                gps_lon = self._get_gps_coordinate(tags, 'GPS GPSLongitude',
                                                   'GPS GPSLongitudeRef')
                
                if gps_lat:
                    metadata['gps_latitude'] = gps_lat
                if gps_lon:
                    metadata['gps_longitude'] = gps_lon
                
                # Altitude
                if 'GPS GPSAltitude' in tags:
                    try:
                        alt = tags['GPS GPSAltitude']
                        metadata['gps_altitude'] = float(alt.values[0].num) / float(alt.values[0].den)
                    except:
                        pass
        
        except Exception as e:
            print(f"exifread extraction error: {e}")
        
        return metadata
    
    def _parse_gps(self, gps_info: Dict) -> Dict:
        """Parse GPS info from PIL EXIF"""
        gps_data = {}
        
        try:
            # Convert GPS info
            gps_dict = {}
            for key in gps_info.keys():
                decode = GPSTAGS.get(key, key)
                gps_dict[decode] = gps_info[key]
            
            # Latitude
            if 'GPSLatitude' in gps_dict and 'GPSLatitudeRef' in gps_dict:
                lat = self._convert_to_degrees(gps_dict['GPSLatitude'])
                if gps_dict['GPSLatitudeRef'] == 'S':
                    lat = -lat
                gps_data['gps_latitude'] = lat
            
            # Longitude
            if 'GPSLongitude' in gps_dict and 'GPSLongitudeRef' in gps_dict:
                lon = self._convert_to_degrees(gps_dict['GPSLongitude'])
                if gps_dict['GPSLongitudeRef'] == 'W':
                    lon = -lon
                gps_data['gps_longitude'] = lon
            
            # Altitude
            if 'GPSAltitude' in gps_dict:
                alt = gps_dict['GPSAltitude']
                gps_data['gps_altitude'] = float(alt)
        
        except Exception as e:
            print(f"GPS parsing error: {e}")
        
        return gps_data
    
    def _convert_to_degrees(self, value) -> float:
        """Convert GPS coordinates to degrees"""
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    
    def _get_gps_coordinate(self, tags: Dict, coord_tag: str, ref_tag: str) -> Optional[float]:
        """Extract GPS coordinate from exifread tags"""
        try:
            if coord_tag in tags and ref_tag in tags:
                coord = tags[coord_tag]
                ref = str(tags[ref_tag])
                
                # Parse coordinate values
                degrees = float(coord.values[0].num) / float(coord.values[0].den)
                minutes = float(coord.values[1].num) / float(coord.values[1].den)
                seconds = float(coord.values[2].num) / float(coord.values[2].den)
                
                decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
                
                # Apply reference (N/S or E/W)
                if ref in ['S', 'W']:
                    decimal = -decimal
                
                return decimal
        except Exception as e:
            print(f"GPS coordinate error: {e}")
        
        return None
    
    def _parse_exif_datetime(self, exif_date: str) -> Optional[str]:
        """Parse EXIF datetime to ISO format"""
        try:
            # EXIF format: 'YYYY:MM:DD HH:MM:SS'
            parts = exif_date.split(' ')
            if len(parts) == 2:
                date_part = parts[0].replace(':', '-')
                time_part = parts[1]
                dt = datetime.strptime(f"{date_part} {time_part}", '%Y-%m-%d %H:%M:%S')
                return dt.isoformat()
        except Exception as e:
            print(f"Date parsing error: {e}")
        
        return None