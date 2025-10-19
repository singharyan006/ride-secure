"""
Database service for Python API to connect to Supabase
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Load environment variables
load_dotenv()


class DatabaseService:
    """Handle Supabase PostgreSQL connections and operations"""
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
        }
        self._test_connection()
    
    def _test_connection(self):
        """Test database connection"""
        try:
            conn = self._get_connection()
            conn.close()
            print(f"✅ Python API connected to Supabase: {self.connection_params['host']}")
        except Exception as e:
            print(f"❌ Python API DB connection failed: {e}")
            raise
    
    def _get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def save_violation(
        self,
        video_source: str,
        frame_number: int,
        track_id: int,
        bbox_x1: int,
        bbox_y1: int,
        bbox_x2: int,
        bbox_y2: int,
        confidence: float,
        raw_detection: Dict[Any, Any]
    ) -> Optional[int]:
        """
        Save violation to database
        
        Returns: violation ID if successful, None otherwise
        """
        sql = """
            INSERT INTO violations (
                video_source, frame_number,
                x1, y1, x2, y2,
                confidence_score, raw_detection
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            RETURNING id
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Convert raw_detection dict to JSON string
            raw_json = json.dumps(raw_detection)
            
            cursor.execute(sql, (
                video_source,
                frame_number,
                bbox_x1,
                bbox_y1,
                bbox_x2,
                bbox_y2,
                confidence,
                raw_json
            ))
            
            violation_id = cursor.fetchone()[0]
            conn.commit()
            
            cursor.close()
            conn.close()
            
            print(f"  ✅ Saved violation ID={violation_id}, frame={frame_number}, track={track_id}")
            return violation_id
            
        except Exception as e:
            print(f"  ❌ Failed to save violation: {e}")
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            return None
    
    def get_recent_violations(self, limit: int = 100):
        """Get recent violations from database"""
        sql = """
            SELECT id, timestamp, video_source, frame_number,
                   x1, y1, x2, y2,
                   confidence_score, raw_detection
            FROM violations
            ORDER BY timestamp DESC
            LIMIT %s
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(sql, (limit,))
            violations = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to list of dicts
            return [dict(v) for v in violations]
            
        except Exception as e:
            print(f"❌ Failed to fetch violations: {e}")
            if 'conn' in locals():
                conn.close()
            return []
    
    def get_violations_by_video(self, video_source: str):
        """Get all violations for a specific video"""
        sql = """
            SELECT id, timestamp, video_source, frame_number,
                   x1, y1, x2, y2,
                   confidence_score, raw_detection
            FROM violations
            WHERE video_source = %s
            ORDER BY frame_number ASC
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(sql, (video_source,))
            violations = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(v) for v in violations]
            
        except Exception as e:
            print(f"❌ Failed to fetch violations for video: {e}")
            if 'conn' in locals():
                conn.close()
            return []


# Singleton instance
_db_service = None

def get_db_service() -> DatabaseService:
    """Get or create DatabaseService singleton"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
