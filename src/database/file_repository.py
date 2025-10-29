"""
Evidence file data access layer
"""
from datetime import datetime
from typing import List, Optional, Dict
from .db_manager import get_db_manager

class FileRepository:
    """Repository for evidence file operations"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def add_file(self, file_data: Dict) -> int:
        """Add evidence file to database"""
        query = '''
            INSERT INTO evidence_files (
                case_id, file_path, file_relative_path, file_name, file_type, file_size, file_hash,
                source_archive, date_created, date_modified, date_accessed, date_taken,
                gps_latitude, gps_longitude, gps_altitude,
                camera_make, camera_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        params = (
            file_data.get('case_id'),
            file_data.get('file_path'),
            file_data.get('file_relative_path'),
            file_data.get('file_name'),
            file_data.get('file_type'),
            file_data.get('file_size'),
            file_data.get('file_hash'),
            file_data.get('source_archive'),
            file_data.get('date_created'),
            file_data.get('date_modified'),
            file_data.get('date_accessed'),
            file_data.get('date_taken'),
            file_data.get('gps_latitude'),
            file_data.get('gps_longitude'),
            file_data.get('gps_altitude'),
            file_data.get('camera_make'),
            file_data.get('camera_model')
        )

        return self.db.execute_insert(query, params)
    
    def get_file(self, file_id: int) -> Optional[Dict]:
        """Get file by ID"""
        query = 'SELECT * FROM evidence_files WHERE file_id = ?'
        results = self.db.execute_query(query, (file_id,))
        
        if results:
            return dict(results[0])
        return None
    
    def get_files_by_case(self, case_id: int, 
                          flagged_only: bool = False) -> List[Dict]:
        """Get all files for a case"""
        if flagged_only:
            query = '''
                SELECT * FROM evidence_files 
                WHERE case_id = ? AND is_flagged = 1
                ORDER BY date_taken DESC
            '''
        else:
            query = '''
                SELECT * FROM evidence_files 
                WHERE case_id = ?
                ORDER BY date_taken DESC
            '''
        
        results = self.db.execute_query(query, (case_id,))
        return [dict(row) for row in results]
    
    def update_ai_analysis(self, file_id: int, analysis_data: Dict):
        """Update file with AI analysis results"""
        query = '''
            UPDATE evidence_files 
            SET ai_processed = 1,
                ai_tags = ?,
                ai_confidence = ?,
                ocr_text = ?,
                face_count = ?,
                analyzed_date = ?
            WHERE file_id = ?
        '''
        
        params = (
            analysis_data.get('ai_tags'),
            analysis_data.get('ai_confidence'),
            analysis_data.get('ocr_text'),
            analysis_data.get('face_count', 0),
            datetime.now().isoformat(),
            file_id
        )
        
        self.db.execute_update(query, params)
    
    def flag_file(self, file_id: int, reason: str = ''):
        """Flag file as evidence"""
        query = '''
            UPDATE evidence_files 
            SET is_flagged = 1, flag_reason = ?
            WHERE file_id = ?
        '''
        self.db.execute_update(query, (reason, file_id))
    
    def unflag_file(self, file_id: int):
        """Remove flag from file"""
        query = '''
            UPDATE evidence_files 
            SET is_flagged = 0, flag_reason = NULL
            WHERE file_id = ?
        '''
        self.db.execute_update(query, (file_id,))
    
    def add_note(self, file_id: int, note: str):
        """Add analyst note to file"""
        query = 'UPDATE evidence_files SET analyst_notes = ? WHERE file_id = ?'
        self.db.execute_update(query, (note, file_id))
    
    def search_files(self, case_id: int, search_params: Dict) -> List[Dict]:
        """Search files with various filters"""
        query = 'SELECT * FROM evidence_files WHERE case_id = ?'
        params = [case_id]
        
        # Date range filter
        if search_params.get('date_from'):
            query += ' AND date_taken >= ?'
            params.append(search_params['date_from'])
        
        if search_params.get('date_to'):
            query += ' AND date_taken <= ?'
            params.append(search_params['date_to'])
        
        # File type filter
        if search_params.get('file_type'):
            query += ' AND file_type = ?'
            params.append(search_params['file_type'])
        
        # Flagged filter
        if search_params.get('flagged_only'):
            query += ' AND is_flagged = 1'
        
        # Face count filter
        if search_params.get('has_faces'):
            query += ' AND face_count > 0'
        
        # Text search in OCR
        if search_params.get('text_search'):
            query += ' AND ocr_text LIKE ?'
            params.append(f'%{search_params["text_search"]}')
        
        # Tag search
        if search_params.get('tag_search'):
            query += ' AND ai_tags LIKE ?'
            params.append(f'%{search_params["tag_search"]}')
        
        query += ' ORDER BY date_taken DESC'
        
        results = self.db.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    def delete_file(self, file_id: int) -> bool:
        """Delete file from database"""
        query = 'DELETE FROM evidence_files WHERE file_id = ?'
        affected = self.db.execute_delete(query, (file_id,))
        return affected > 0
    
    def get_unprocessed_files(self, case_id: int) -> List[Dict]:
        """Get files that haven't been processed by AI yet"""
        query = '''
            SELECT * FROM evidence_files
            WHERE case_id = ? AND ai_processed = 0
            ORDER BY imported_date ASC
        '''
        results = self.db.execute_query(query, (case_id,))
        return [dict(row) for row in results]

    def get_unprocessed_count(self, case_id: int) -> int:
        """Get count of files that haven't been processed by AI yet"""
        query = '''
            SELECT COUNT(*)
            FROM evidence_files
            WHERE case_id = ? AND ai_processed = 0
        '''
        results = self.db.execute_query(query, (case_id,))

        if results:
            return results[0][0]
        return 0