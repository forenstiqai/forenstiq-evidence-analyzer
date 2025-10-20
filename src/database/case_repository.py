"""
Case data access layer
"""
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path
from .db_manager import get_db_manager

class CaseRepository:
    """Repository for case operations"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def create_case(self, case_data: Dict) -> int:
        """
        Create new case
        
        Args:
            case_data: Dictionary with case information
        
        Returns:
            case_id of created case
        """
        query = '''
            INSERT INTO cases (
                case_number, case_name, investigator_name, agency_name,
                incident_date, status, notes, evidence_source_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        params = (
            case_data.get('case_number'),
            case_data.get('case_name'),
            case_data.get('investigator_name'),
            case_data.get('agency_name'),
            case_data.get('incident_date'),
            case_data.get('status', 'open'),
            case_data.get('notes'),
            case_data.get('evidence_source_path')
        )
        
        return self.db.execute_insert(query, params)
    
    def get_case(self, case_id: int) -> Optional[Dict]:
        """Get case by ID"""
        query = 'SELECT * FROM cases WHERE case_id = ?'
        results = self.db.execute_query(query, (case_id,))
        
        if results:
            return dict(results[0])
        return None
    
    def get_case_by_number(self, case_number: str) -> Optional[Dict]:
        """Get case by case number"""
        query = 'SELECT * FROM cases WHERE case_number = ?'
        results = self.db.execute_query(query, (case_number,))
        
        if results:
            return dict(results[0])
        return None
    
    def get_all_cases(self, status: Optional[str] = None) -> List[Dict]:
        """Get all cases, optionally filtered by status"""
        if status:
            query = 'SELECT * FROM cases WHERE status = ? ORDER BY last_modified DESC'
            results = self.db.execute_query(query, (status,))
        else:
            query = 'SELECT * FROM cases ORDER BY last_modified DESC'
            results = self.db.execute_query(query)
        
        return [dict(row) for row in results]
    
    def update_case(self, case_id: int, case_data: Dict) -> bool:
        """Update case information"""
        # Build dynamic UPDATE query
        fields = []
        values = []
        
        updateable_fields = [
            'case_name', 'investigator_name', 'agency_name',
            'incident_date', 'status', 'notes', 'evidence_source_path'
        ]
        
        for field in updateable_fields:
            if field in case_data:
                fields.append(f'{field} = ?')
                values.append(case_data[field])
        
        if not fields:
            return False
        
        # Add last_modified
        fields.append('last_modified = ?')
        values.append(datetime.now().isoformat())
        
        # Add case_id for WHERE clause
        values.append(case_id)
        
        query = f"UPDATE cases SET {', '.join(fields)} WHERE case_id = ?"
        affected = self.db.execute_update(query, tuple(values))
        
        return affected > 0
    
    def delete_case(self, case_id: int) -> bool:
        """Delete case (cascade deletes all related data)"""
        query = 'DELETE FROM cases WHERE case_id = ?'
        affected = self.db.execute_delete(query, (case_id,))
        return affected > 0
    
    def update_file_counts(self, case_id: int):
        """Update total_files and total_flagged counts"""
        query = '''
            UPDATE cases 
            SET total_files = (
                SELECT COUNT(*) FROM evidence_files WHERE case_id = ?
            ),
            total_flagged = (
                SELECT COUNT(*) FROM evidence_files WHERE case_id = ? AND is_flagged = 1
            ),
            last_modified = ?
            WHERE case_id = ?
        '''
        
        timestamp = datetime.now().isoformat()
        self.db.execute_update(query, (case_id, case_id, timestamp, case_id))
    
    def get_case_statistics(self, case_id: int) -> Dict:
        """Get case statistics"""
        query = '''
            SELECT 
                COUNT(*) as total_files,
                SUM(CASE WHEN ai_processed = 1 THEN 1 ELSE 0 END) as processed_files,
                SUM(CASE WHEN is_flagged = 1 THEN 1 ELSE 0 END) as flagged_files,
                SUM(CASE WHEN face_count > 0 THEN 1 ELSE 0 END) as files_with_faces,
                SUM(face_count) as total_faces,
                COUNT(DISTINCT date_taken) as unique_dates
            FROM evidence_files
            WHERE case_id = ?
        '''
        
        results = self.db.execute_query(query, (case_id,))
        if results:
            return dict(results[0])
        return {}