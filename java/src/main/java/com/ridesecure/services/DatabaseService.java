package com.ridesecure.services;

import com.ridesecure.models.Violation;
import com.ridesecure.config.EnvConfig;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Database service for Supabase PostgreSQL
 * 
 * Simplified - just save and retrieve violations
 */
public class DatabaseService {
    
    public DatabaseService() {
        try {
            Class.forName("org.postgresql.Driver");
            testConnection();
        } catch (Exception e) {
            System.err.println("❌ DatabaseService initialization failed: " + e.getMessage());
        }
    }
    
    private Connection getConnection() throws SQLException {
        String url = EnvConfig.getDatabaseUrl();
        String user = EnvConfig.getDatabaseUser();
        String password = EnvConfig.getDatabasePassword();
        return DriverManager.getConnection(url, user, password);
    }
    
    public boolean testConnection() {
        try (Connection conn = getConnection()) {
            if (conn != null) {
                System.out.println("✅ Connected to Supabase: " + EnvConfig.get("DB_HOST"));
                return true;
            }
        } catch (SQLException e) {
            System.err.println("❌ Database connection failed: " + e.getMessage());
        }
        return false;
    }
    
    /**
     * Save violation to database (matches Supabase schema)
     */
    public boolean saveViolation(Violation violation) {
        String sql = """
            INSERT INTO violations (
                video_source, frame_number,
                bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                confidence, raw_detection
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?::jsonb)
        """;

        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {

            stmt.setString(1, violation.getVideoSource());
            stmt.setInt(2, violation.getFrameNumber());
            stmt.setInt(3, violation.getBboxX1());
            stmt.setInt(4, violation.getBboxY1());
            stmt.setInt(5, violation.getBboxX2());
            stmt.setInt(6, violation.getBboxY2());
            stmt.setDouble(7, violation.getConfidence());
            stmt.setString(8, violation.getRawDetection());

            int rowsAffected = stmt.executeUpdate();

            if (rowsAffected > 0) {
                try (ResultSet generatedKeys = stmt.getGeneratedKeys()) {
                    if (generatedKeys.next()) {
                        violation.setId(generatedKeys.getInt(1));
                    }
                }
                System.out.println("✅ Violation saved: ID=" + violation.getId() + ", frame=" + violation.getFrameNumber());
                return true;
            }

        } catch (SQLException e) {
            System.err.println("❌ Failed to save violation: " + e.getMessage());
            e.printStackTrace();
        }

        return false;
    }
    
    /**
     * Get all violations from database
     */
    public List<Violation> getAllViolations() {
        String sql = """
            SELECT id, timestamp, video_source, frame_number,
                   bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                   confidence, raw_detection
            FROM violations
            ORDER BY timestamp DESC
        """;
        
        List<Violation> violations = new ArrayList<>();
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {
            
            while (rs.next()) {
                Violation violation = new Violation();
                violation.setId(rs.getInt("id"));
                violation.setTimestamp(rs.getTimestamp("timestamp").toLocalDateTime());
                violation.setVideoSource(rs.getString("video_source"));
                violation.setFrameNumber(rs.getInt("frame_number"));
                violation.setBboxX1(rs.getInt("bbox_x1"));
                violation.setBboxY1(rs.getInt("bbox_y1"));
                violation.setBboxX2(rs.getInt("bbox_x2"));
                violation.setBboxY2(rs.getInt("bbox_y2"));
                violation.setConfidence(rs.getDouble("confidence"));
                violation.setRawDetection(rs.getString("raw_detection"));
                
                violations.add(violation);
            }
            
            System.out.println("✅ Retrieved " + violations.size() + " violations");
            
        } catch (SQLException e) {
            System.err.println("❌ Failed to retrieve violations: " + e.getMessage());
        }
        
        return violations;
    }
}
