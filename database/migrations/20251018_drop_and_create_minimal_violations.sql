-- Destructive migration: drop existing tables and create minimal violations table
-- WARNING: This will delete data in the dropped tables. Backup first.

BEGIN;

DROP TABLE IF EXISTS public.model_performance CASCADE;
DROP TABLE IF EXISTS public.detection_sessions CASCADE;
DROP TABLE IF EXISTS public.violations CASCADE;

CREATE TABLE public.violations (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    video_source TEXT,
    frame_number INTEGER,
    x1 INTEGER,
    y1 INTEGER,
    x2 INTEGER,
    y2 INTEGER,
    class_id INTEGER,
    class_name VARCHAR(100),
    confidence_score DOUBLE PRECISION,
    track_id VARCHAR(100),
    license_plate VARCHAR(50),
    plate_confidence DOUBLE PRECISION,
    snapshot_path TEXT,
    raw_detection JSONB,
    violation_type VARCHAR(50) DEFAULT 'NO_HELMET',
    status VARCHAR(20) DEFAULT 'DETECTED',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON public.violations (timestamp);
CREATE INDEX IF NOT EXISTS idx_violations_class_name ON public.violations (class_name);
CREATE INDEX IF NOT EXISTS idx_violations_track_id ON public.violations (track_id);

COMMIT;
