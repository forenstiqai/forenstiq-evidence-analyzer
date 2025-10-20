#!/usr/bin/env python3
"""
Database migration script to add file_relative_path column to evidence_files table
"""
import sqlite3
import sys
from pathlib import Path

def migrate_database():
    """Add file_relative_path column to evidence_files table"""
    # Use default database path
    db_path = Path('./data/forenstiq_cases.db')

    print(f"Migrating database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(evidence_files)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'file_relative_path' in columns:
            print("✓ Column 'file_relative_path' already exists. No migration needed.")
            conn.close()
            return

        # Add the new column
        print("Adding 'file_relative_path' column to evidence_files table...")
        cursor.execute("""
            ALTER TABLE evidence_files
            ADD COLUMN file_relative_path TEXT
        """)

        conn.commit()
        print("✓ Migration completed successfully!")

        # Verify the column was added
        cursor.execute("PRAGMA table_info(evidence_files)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'file_relative_path' in columns:
            print("✓ Column 'file_relative_path' verified in database schema.")
        else:
            print("✗ Error: Column was not added successfully.")

        conn.close()

    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add file_relative_path Column")
    print("=" * 60)
    migrate_database()
    print("\nMigration process complete.")
