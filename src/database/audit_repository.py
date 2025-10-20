"""
Audit log data access layer
"""
from datetime import datetime
from typing import List, Dict, Optional
import json
from .db_manager import get_db_manager

class AuditRepository:
    """Repository for audit logging"""
    
    def __init__(self):
        self.db = get_db_manager()
    
    def log_action(self, action: str, case_id: Optional[int] = None,
                   user_name: str = 'System', details: Dict = None):
        """
        Log an action
        
        Args:
            action: Action name (e.g., 'create_case', 'analyze_file')
            case_id: Associated case ID (optional)
            user_name: User who performed action
            details: Additional details as dictionary
        """
        query = '''
            INSERT INTO audit_log (case_id, user_name, action, details)
            VALUES (?, ?, ?, ?)
        '''
        
        details_json = json.dumps(details) if details else None
        
        params = (case_id, user_name, action, details_json)
        self.db.execute_insert(query, params)
    
    def get_case_logs(self, case_id: int, limit: int = 100) -> List[Dict]:
        """Get audit logs for a case"""
        query = '''
            SELECT * FROM audit_log 
            WHERE case_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        results = self.db.execute_query(query, (case_id, limit))
        logs = []
        
        for row in results:
            log = dict(row)
            # Parse JSON details
            if log.get('details'):
                try:
                    log['details'] = json.loads(log['details'])
                except:
                    pass
            logs.append(log)
        
        return logs
    
    def get_all_logs(self, limit: int = 1000) -> List[Dict]:
        """Get all audit logs"""
        query = '''
            SELECT * FROM audit_log 
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        results = self.db.execute_query(query, (limit,))
        logs = []
        
        for row in results:
            log = dict(row)
            if log.get('details'):
                try:
                    log['details'] = json.loads(log['details'])
                except:
                    pass
            logs.append(log)
        
        return logs
    
    def get_logs_by_action(self, action: str, limit: int = 100) -> List[Dict]:
        """Get logs filtered by action type"""
        query = '''
            SELECT * FROM audit_log 
            WHERE action = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        results = self.db.execute_query(query, (action, limit))
        return [dict(row) for row in results]