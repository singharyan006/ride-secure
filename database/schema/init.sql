-- RideSecure Database Schema
-- SQLite database for storing helmet violation records

-- Create violations table
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    video_source VARCHAR(255) NOT NULL,
    frame_number INTEGER NOT NULL,
    detection_confidence REAL NOT NULL,
    license_plate VARCHAR(20),
    plate_confidence REAL,
    snapshot_path VARCHAR(500),
    location_info TEXT,
    violation_type VARCHAR(50) DEFAULT 'NO_HELMET',
    status VARCHAR(20) DEFAULT 'DETECTED',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create detection_sessions table to track processing sessions
CREATE TABLE IF NOT EXISTS detection_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_name VARCHAR(100) NOT NULL,
    video_path VARCHAR(500) NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    total_frames INTEGER,
    processed_frames INTEGER DEFAULT 0,
    violations_detected INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'RUNNING',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create model_performance table to track detection accuracy
CREATE TABLE IF NOT EXISTS model_performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    test_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    accuracy_score REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
CREATE INDEX IF NOT EXISTS idx_violations_license_plate ON violations(license_plate);
CREATE INDEX IF NOT EXISTS idx_violations_video_source ON violations(video_source);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON detection_sessions(status);

-- Insert sample data for testing
INSERT OR IGNORE INTO model_performance (model_name, model_version, accuracy_score, precision_score, recall_score, f1_score, notes) 
VALUES 
    ('helmet_detection_yolo_v8', '1.0.0', 0.89, 0.87, 0.91, 0.89, 'Initial training on 5K images'),
    ('license_plate_yolo_v8', '1.0.0', 0.82, 0.85, 0.79, 0.82, 'Trained on Indian license plates');

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_violations_timestamp 
AFTER UPDATE ON violations
FOR EACH ROW
BEGIN
    UPDATE violations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;