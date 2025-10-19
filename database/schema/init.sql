-- RideSecure Database Schema
-- SQLite database for storing helmet violation records

-- Create violations table
CREATE TABLE IF NOT EXISTS violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    video_source VARCHAR(255) NOT NULL,
    frame_number INTEGER NOT NULL,
    -- Bounding box coordinates (pixels)
    x1 INTEGER NOT NULL,
    y1 INTEGER NOT NULL,
    x2 INTEGER NOT NULL,
    y2 INTEGER NOT NULL,
    class_id INTEGER,
    class_name VARCHAR(100),
    confidence_score REAL NOT NULL,
    track_id VARCHAR(100),
    -- Optional license plate info
    license_plate VARCHAR(50),
    -- Minimal RideSecure Database Schema
    -- This schema creates only the required `violations` table for detection events.
    -- Use this when you want a lightweight DB layout focused on storing detections.

    -- Create violations table (minimal, flexible)
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        video_source TEXT,
        frame_number INTEGER,
        x1 INTEGER,
        y1 INTEGER,
        x2 INTEGER,
        y2 INTEGER,
        class_id INTEGER,
        class_name VARCHAR(100),
        confidence_score REAL,
        track_id VARCHAR(100),
        license_plate VARCHAR(50),
        plate_confidence REAL,
        snapshot_path VARCHAR(500),
        raw_detection TEXT, -- JSON string of original prediction if needed
        violation_type VARCHAR(50) DEFAULT 'NO_HELMET',
        status VARCHAR(20) DEFAULT 'DETECTED',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Indexes useful for queries
    CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp);
    CREATE INDEX IF NOT EXISTS idx_violations_class_name ON violations(class_name);
    CREATE INDEX IF NOT EXISTS idx_violations_track_id ON violations(track_id);