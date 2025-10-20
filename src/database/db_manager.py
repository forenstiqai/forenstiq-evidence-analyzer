"""
Database connection manager
"""
import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

class DatabaseManager:
    """Manage SQLite database connections"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.connection = None
        self._ensure_database()
    
    def _ensure_database(self):
        """Ensure database and schema exist"""
        # Create directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create database and schema
        conn = self.get_connection()
        self._create_schema(conn)
        conn.close()
    
    def _create_schema(self, conn: sqlite3.Connection):
        """Create database schema"""
        schema_file = Path(__file__).parent / 'schema.sql'
        
        if schema_file.exists():
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign keys
        return conn
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute query and return results"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute insert and return last row ID"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update and return affected rows"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """Execute delete and return affected rows"""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# Global database instance
_db_manager = None

def get_db_manager(db_path: Optional[Path] = None) -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    
    if _db_manager is None:
        if db_path is None:
            db_path = Path('./data/forenstiq_cases.db')
        _db_manager = DatabaseManager(db_path)
    
    return _db_manager