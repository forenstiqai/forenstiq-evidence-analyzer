-- Forenstiq Evidence Analyzer Database Schema
-- SQLite Database

-- Cases table
CREATE TABLE IF NOT EXISTS cases (
    case_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT UNIQUE NOT NULL,
    case_name TEXT NOT NULL,
    investigator_name TEXT,
    agency_name TEXT,
    incident_date DATE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'open',
    notes TEXT,
    evidence_source_path TEXT,
    total_files INTEGER DEFAULT 0,
    total_flagged INTEGER DEFAULT 0
);

-- Evidence files table
CREATE TABLE IF NOT EXISTS evidence_files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_relative_path TEXT,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    file_hash TEXT,
    source_archive TEXT,

    -- Metadata
    date_created TIMESTAMP,
    date_modified TIMESTAMP,
    date_accessed TIMESTAMP,
    date_taken TIMESTAMP,
    
    -- Geolocation
    gps_latitude REAL,
    gps_longitude REAL,
    gps_altitude REAL,
    location_name TEXT,
    
    -- Camera info
    camera_make TEXT,
    camera_model TEXT,
    
    -- Analysis results
    ai_processed BOOLEAN DEFAULT 0,
    ai_tags TEXT,
    ai_confidence REAL,
    ocr_text TEXT,
    face_count INTEGER DEFAULT 0,
    is_flagged BOOLEAN DEFAULT 0,
    flag_reason TEXT,
    analyst_notes TEXT,
    
    -- Timestamps
    imported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_date TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);

-- Face detections table
CREATE TABLE IF NOT EXISTS face_detections (
    face_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    case_id INTEGER NOT NULL,
    face_encoding BLOB,
    bounding_box TEXT,
    confidence REAL,
    face_cluster_id INTEGER,
    identified_person TEXT,
    
    FOREIGN KEY (file_id) REFERENCES evidence_files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);

-- Object detections table
CREATE TABLE IF NOT EXISTS object_detections (
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    case_id INTEGER NOT NULL,
    object_class TEXT NOT NULL,
    confidence REAL,
    bounding_box TEXT,
    
    FOREIGN KEY (file_id) REFERENCES evidence_files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER,
    user_name TEXT,
    action TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE SET NULL
);

-- Tags table
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT UNIQUE NOT NULL,
    tag_category TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File-Tag mapping
CREATE TABLE IF NOT EXISTS file_tags (
    file_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (file_id, tag_id),
    FOREIGN KEY (file_id) REFERENCES evidence_files(file_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- System settings
CREATE TABLE IF NOT EXISTS settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence_files(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_date ON evidence_files(date_taken);
CREATE INDEX IF NOT EXISTS idx_evidence_flagged ON evidence_files(is_flagged);
CREATE INDEX IF NOT EXISTS idx_face_file ON face_detections(file_id);
CREATE INDEX IF NOT EXISTS idx_face_cluster ON face_detections(face_cluster_id);
CREATE INDEX IF NOT EXISTS idx_object_file ON object_detections(file_id);
CREATE INDEX IF NOT EXISTS idx_audit_case ON audit_log(case_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);