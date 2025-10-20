"""
Generate demo data for testing
"""
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

def generate_demo_data():
    """Generate demo cases and files"""
    
    print("Generating demo data...")
    
    # Create data directory
    data_dir = Path('./data')
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / 'forenstiq_cases.db'
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Load schema
    schema_path = Path('./src/database/schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
        conn.executescript(schema_sql)
    
    # Demo cases
    demo_cases = [
        {
            'case_number': 'DEMO-2024-0001',
            'case_name': 'Mobile Phone Seizure - Suspect A',
            'investigator_name': 'John Smith',
            'agency_name': 'State Forensic Laboratory',
            'incident_date': '2024-01-15',
            'status': 'open',
            'notes': 'Phone seized during arrest. Contains potential evidence of fraud.'
        },
        {
            'case_number': 'DEMO-2024-0002',
            'case_name': 'Computer Hard Drive Analysis',
            'investigator_name': 'Jane Doe',
            'agency_name': 'Cyber Crime Division',
            'incident_date': '2024-02-20',
            'status': 'open',
            'notes': 'Hard drive from suspect\'s computer. Looking for deleted files.'
        },
        {
            'case_number': 'DEMO-2024-0003',
            'case_name': 'Vehicle Accident Documentation',
            'investigator_name': 'Mike Johnson',
            'agency_name': 'Traffic Police',
            'incident_date': '2024-03-10',
            'status': 'closed',
            'notes': 'Photos from accident scene. Case closed with findings.'
        }
    ]
    
    case_ids = []
    for case in demo_cases:
        cursor.execute('''
            INSERT INTO cases (
                case_number, case_name, investigator_name, agency_name,
                incident_date, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            case['case_number'],
            case['case_name'],
            case['investigator_name'],
            case['agency_name'],
            case['incident_date'],
            case['status'],
            case['notes']
        ))
        case_ids.append(cursor.lastrowid)
    
    # Demo files (mock data - no actual files)
    file_types = ['image', 'video', 'document']
    sample_tags = [
        ['person', 'outdoor', 'building'],
        ['car', 'vehicle', 'street'],
        ['phone', 'screen', 'text'],
        ['document', 'paper', 'writing'],
        ['indoor', 'room', 'furniture']
    ]
    
    for case_id in case_ids:
        # Generate 10-30 files per case
        num_files = random.randint(10, 30)
        
        for i in range(num_files):
            file_type = random.choice(['image'] * 7 + ['video'] * 2 + ['document'])
            
            # Random dates
            base_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            # File data
            file_data = {
                'case_id': case_id,
                'file_path': f'/demo/evidence/case_{case_id}/file_{i:04d}.jpg',
                'file_name': f'IMG_{i:04d}.jpg' if file_type == 'image' else f'VID_{i:04d}.mp4',
                'file_type': file_type,
                'file_size': random.randint(500000, 5000000),
                'file_hash': f'sha256_{random.randint(1000000, 9999999)}',
                'date_taken': base_date.isoformat(),
                'date_created': base_date.isoformat(),
                'date_modified': base_date.isoformat(),
            }
            
            # Random GPS (somewhere in India)
            if random.random() > 0.3:
                file_data['gps_latitude'] = random.uniform(17.0, 18.0)
                file_data['gps_longitude'] = random.uniform(78.0, 79.0)
            
            # Camera info
            if file_type == 'image':
                file_data['camera_make'] = random.choice(['Apple', 'Samsung', 'OnePlus', 'Google'])
                file_data['camera_model'] = random.choice(['iPhone 13', 'Galaxy S21', 'OnePlus 9', 'Pixel 6'])
            
            # AI analysis (for some files)
            if random.random() > 0.3:
                file_data['ai_processed'] = 1
                file_data['ai_tags'] = json.dumps(random.choice(sample_tags))
                file_data['ai_confidence'] = random.uniform(0.6, 0.95)
                file_data['face_count'] = random.randint(0, 3)
                
                if random.random() > 0.7:
                    file_data['ocr_text'] = f'Sample text extracted from image {i}'
            
            # Flagged (some files)
            if random.random() > 0.8:
                file_data['is_flagged'] = 1
                file_data['flag_reason'] = 'Contains suspicious content'
            
            # Insert file
            columns = ', '.join(file_data.keys())
            placeholders = ', '.join(['?' for _ in file_data])
            query = f'INSERT INTO evidence_files ({columns}) VALUES ({placeholders})'
            
            cursor.execute(query, tuple(file_data.values()))
    
    # Update case file counts
    for case_id in case_ids:
        cursor.execute('''
            UPDATE cases 
            SET total_files = (SELECT COUNT(*) FROM evidence_files WHERE case_id = ?),
                total_flagged = (SELECT COUNT(*) FROM evidence_files WHERE case_id = ? AND is_flagged = 1)
            WHERE case_id = ?
        ''', (case_id, case_id, case_id))
    
    # Add some audit logs
    for case_id in case_ids:
        cursor.execute('''
            INSERT INTO audit_log (case_id, user_name, action, details)
            VALUES (?, ?, ?, ?)
        ''', (case_id, 'Demo User', 'create_case', json.dumps({'source': 'demo_data'})))
        
        cursor.execute('''
            INSERT INTO audit_log (case_id, user_name, action, details)
            VALUES (?, ?, ?, ?)
        ''', (case_id, 'Demo User', 'import_files', json.dumps({'count': 20})))
    
    conn.commit()
    conn.close()
    
    print(f"✓ Demo data generated successfully!")
    print(f"  - Created {len(demo_cases)} demo cases")
    print(f"  - Database location: {db_path}")
    print(f"\nYou can now run the application and open these demo cases.")

if __name__ == '__main__':
    generate_demo_data()
