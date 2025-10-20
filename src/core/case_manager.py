"""
Case management business logic
"""
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..database.case_repository import CaseRepository
from ..database.file_repository import FileRepository
from ..database.audit_repository import AuditRepository

class CaseManager:
    """Manage forensic cases"""
    
    def __init__(self):
        self.case_repo = CaseRepository()
        self.file_repo = FileRepository()
        self.audit_repo = AuditRepository()
    
    def create_case(self, case_data: Dict) -> int:
        """
        Create new case
        
        Args:
            case_data: Dictionary with case information
        
        Returns:
            case_id of created case
        """
        # Generate case number if not provided
        if not case_data.get('case_number'):
            case_data['case_number'] = self._generate_case_number()
        
        # Create case
        case_id = self.case_repo.create_case(case_data)
        
        # Log action
        self.audit_repo.log_action(
            action='create_case',
            case_id=case_id,
            details={'case_number': case_data['case_number']}
        )
        
        return case_id
    
    def open_case(self, case_id: int) -> Optional[Dict]:
        """Open existing case"""
        case = self.case_repo.get_case(case_id)
        
        if case:
            # Log action
            self.audit_repo.log_action(
                action='open_case',
                case_id=case_id
            )
        
        return case
    
    def close_case(self, case_id: int):
        """Close case"""
        self.case_repo.update_case(case_id, {'status': 'closed'})
        
        # Log action
        self.audit_repo.log_action(
            action='close_case',
            case_id=case_id
        )
    
    def get_case_summary(self, case_id: int) -> Dict:
        """Get comprehensive case summary"""
        case = self.case_repo.get_case(case_id)
        if not case:
            return None
        
        # Get statistics
        stats = self.case_repo.get_case_statistics(case_id)
        
        # Get recent files
        files = self.file_repo.get_files_by_case(case_id)
        recent_files = files[:10]  # Last 10 files
        
        # Get flagged files
        flagged_files = self.file_repo.get_files_by_case(case_id, flagged_only=True)
        
        return {
            'case_info': case,
            'statistics': stats,
            'recent_files': recent_files,
            'flagged_files': flagged_files
        }
    
    def delete_case(self, case_id: int) -> bool:
        """Delete case and all associated data"""
        # Log before deletion
        self.audit_repo.log_action(
            action='delete_case',
            case_id=case_id
        )
        
        # Delete case (cascade deletes files, faces, etc.)
        return self.case_repo.delete_case(case_id)
    
    def _generate_case_number(self) -> str:
        """Generate unique case number"""
        # Format: CASE-YYYY-NNNN
        year = datetime.now().year
        
        # Count existing cases this year
        all_cases = self.case_repo.get_all_cases()
        year_cases = [c for c in all_cases if c['case_number'].startswith(f'CASE-{year}')]
        
        next_num = len(year_cases) + 1
        
        return f'CASE-{year}-{next_num:04d}'