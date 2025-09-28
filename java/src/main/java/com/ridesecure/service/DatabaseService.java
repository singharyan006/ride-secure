package com.ridesecure.service;

import com.ridesecure.model.Violation;
import com.ridesecure.config.EnvConfig;

import java.sql.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Database service for managing violations and detection data
 * 
 * Provides CRUD operations for violations, sessions, and model performance
 * tracking using Supabase PostgreSQL database.
 */
public class DatabaseService {
    
    private static DatabaseService instance;
    
    private DatabaseService() {
        try {
            // Load PostgreSQL JDBC driver
            Class.forName("org.postgresql.Driver");
            initializeDatabase();
            System.out.println("✅ DatabaseService connected to Supabase successfully");
        } catch (Exception e) {
            System.err.println("❌ Failed to initialize DatabaseService: " + e.getMessage());
            EnvConfig.printConfig(); // Show config for debugging
            throw new RuntimeException("Database initialization failed", e);
        }
    }
    
    public static DatabaseService getInstance() {
        if (instance == null) {
            instance = new DatabaseService();
        }
        return instance;
    }
    
    /**
     * Initialize database connection and test connectivity
     */
    private void initializeDatabase() throws SQLException {        
        try (Connection conn = getConnection()) {
            if (conn != null) {
                System.out.println("✅ Connected to Supabase PostgreSQL: " + EnvConfig.get("DB_HOST"));
                
                // Test the connection with a simple query
                try (Statement stmt = conn.createStatement();
                     ResultSet rs = stmt.executeQuery("SELECT COUNT(*) FROM violations")) {
                    
                    if (rs.next()) {
                        int count = rs.getInt(1);
                        System.out.println("✅ Database test successful. Found " + count + " violations in database.");
                    }
                }
            }
        }
    }
    

    
    /**
     * Get database connection using .env configuration
     */
    private Connection getConnection() throws SQLException {
        String url = EnvConfig.getDatabaseUrl();
        String user = EnvConfig.getDatabaseUser();
        String password = EnvConfig.getDatabasePassword();
        
        return DriverManager.getConnection(url, user, password);
    }
    
    /**
     * Save violation to database
     */
    public boolean saveViolation(Violation violation) {
        String sql = """
            INSERT INTO violations (
                video_source, frame_number, license_plate, 
                confidence_score, plate_confidence, violation_type, 
                snapshot_path, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """;
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, violation.getVideoSource());
            stmt.setInt(2, violation.getFrameNumber());
            stmt.setString(3, violation.getLicensePlate());
            stmt.setDouble(4, violation.getDetectionConfidence());
            
            if (violation.getPlateConfidence() != null) {
                stmt.setDouble(5, violation.getPlateConfidence());
            } else {
                stmt.setNull(5, Types.DECIMAL);
            }
            
            stmt.setString(6, violation.getViolationType());
            stmt.setString(7, violation.getSnapshotPath());
            stmt.setString(8, violation.getStatus());
            
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                // Get generated ID
                try (ResultSet generatedKeys = stmt.getGeneratedKeys()) {
                    if (generatedKeys.next()) {
                        violation.setId(generatedKeys.getInt(1));
                    }
                }
                
                System.out.println("Violation saved with ID: " + violation.getId());
                return true;
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to save violation: " + e.getMessage());
        }
        
        return false;
    }
    
    /**
     * Get all violations from database
     */
    public List<Violation> getAllViolations() {
        String sql = """
            SELECT id, timestamp, video_source, frame_number, 
                   license_plate, confidence_score, plate_confidence, 
                   violation_type, snapshot_path, status, created_at
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
                violation.setDetectionConfidence(rs.getDouble("confidence_score"));
                violation.setLicensePlate(rs.getString("license_plate"));
                
                double plateConf = rs.getDouble("plate_confidence");
                if (!rs.wasNull()) {
                    violation.setPlateConfidence(plateConf);
                }
                
                violation.setSnapshotPath(rs.getString("snapshot_path"));
                violation.setViolationType(rs.getString("violation_type"));
                violation.setStatus(rs.getString("status"));
                violation.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
                
                violations.add(violation);
            }
            
            System.out.println("Retrieved " + violations.size() + " violations from database");
            
        } catch (SQLException e) {
            System.err.println("Failed to retrieve violations: " + e.getMessage());
        }
        
        return violations;
    }
    
    /**
     * Get violations by license plate
     */
    public List<Violation> getViolationsByLicensePlate(String licensePlate) {
        String sql = """
            SELECT id, timestamp, video_source, frame_number, 
                   license_plate, confidence_score, plate_confidence, 
                   violation_type, snapshot_path, status, created_at
            FROM violations
            WHERE license_plate LIKE ?
            ORDER BY timestamp DESC
        """;
        
        List<Violation> violations = new ArrayList<>();
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setString(1, "%" + licensePlate + "%");
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    Violation violation = new Violation();
                    violation.setId(rs.getInt("id"));
                    violation.setTimestamp(rs.getTimestamp("timestamp").toLocalDateTime());
                    violation.setVideoSource(rs.getString("video_source"));
                    violation.setFrameNumber(rs.getInt("frame_number"));
                    violation.setDetectionConfidence(rs.getDouble("confidence_score"));
                    violation.setLicensePlate(rs.getString("license_plate"));
                    
                    double plateConf = rs.getDouble("plate_confidence");
                    if (!rs.wasNull()) {
                        violation.setPlateConfidence(plateConf);
                    }
                    
                    violation.setSnapshotPath(rs.getString("snapshot_path"));
                    violation.setViolationType(rs.getString("violation_type"));
                    violation.setStatus(rs.getString("status"));
                    violation.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
                    
                    violations.add(violation);
                }
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to retrieve violations by license plate: " + e.getMessage());
        }
        
        return violations;
    }
    
    /**
     * Update violation status
     */
    public boolean updateViolationStatus(int violationId, String newStatus) {
        String sql = "UPDATE violations SET status = ? WHERE id = ?";
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setString(1, newStatus);
            stmt.setInt(2, violationId);
            
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                System.out.println("Updated violation " + violationId + " status to " + newStatus);
                return true;
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to update violation status: " + e.getMessage());
        }
        
        return false;
    }
    
    /**
     * Get violation statistics
     */
    public ViolationStats getViolationStats() {
        String sql = """
            SELECT 
                COUNT(*) as total_violations,
                COUNT(CASE WHEN status = 'DETECTED' THEN 1 END) as pending_violations,
                COUNT(CASE WHEN status = 'PROCESSED' THEN 1 END) as processed_violations,
                AVG(confidence_score) as avg_confidence
            FROM violations
        """;
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql);
             ResultSet rs = stmt.executeQuery()) {
            
            if (rs.next()) {
                return new ViolationStats(
                    rs.getInt("total_violations"),
                    rs.getInt("pending_violations"),
                    rs.getInt("processed_violations"),
                    rs.getDouble("avg_confidence")
                );
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to retrieve violation statistics: " + e.getMessage());
        }
        
        return new ViolationStats(0, 0, 0, 0.0);
    }
    
    /**
     * Start detection session
     */
    public int startDetectionSession(String sessionName, String videoPath) {
        String sql = """
            INSERT INTO detection_sessions (session_name, video_path, start_time, status)
            VALUES (?, ?, CURRENT_TIMESTAMP, 'RUNNING')
        """;
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            
            stmt.setString(1, sessionName);
            stmt.setString(2, videoPath);
            
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                try (ResultSet generatedKeys = stmt.getGeneratedKeys()) {
                    if (generatedKeys.next()) {
                        int sessionId = generatedKeys.getInt(1);
                        System.out.println("Started detection session: " + sessionName + " with ID: " + sessionId);
                        return sessionId;
                    }
                }
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to start detection session: " + e.getMessage());
        }
        
        return -1;
    }
    
    /**
     * End detection session
     */
    public boolean endDetectionSession(int sessionId, int totalFrames, int violationsDetected) {
        String sql = """
            UPDATE detection_sessions 
            SET end_time = CURRENT_TIMESTAMP, 
                total_frames = ?, 
                violations_detected = ?, 
                status = 'COMPLETED'
            WHERE id = ?
        """;
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setInt(1, totalFrames);
            stmt.setInt(2, violationsDetected);
            stmt.setInt(3, sessionId);
            
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                System.out.println("Ended detection session: " + sessionId);
                return true;
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to end detection session: " + e.getMessage());
        }
        
        return false;
    }
    
    /**
     * Test database connection
     */
    public boolean testConnection() {
        try (Connection conn = getConnection()) {
            return conn != null && !conn.isClosed();
        } catch (SQLException e) {
            System.err.println("Database connection test failed: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Delete violation by ID
     */
    public boolean deleteViolation(int violationId) {
        String sql = "DELETE FROM violations WHERE id = ?";
        
        try (Connection conn = getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            
            stmt.setInt(1, violationId);
            int rowsAffected = stmt.executeUpdate();
            
            if (rowsAffected > 0) {
                System.out.println("Deleted violation with ID: " + violationId);
                return true;
            }
            
        } catch (SQLException e) {
            System.err.println("Failed to delete violation: " + e.getMessage());
        }
        
        return false;
    }
    
    /**
     * Violation statistics data class
     */
    public static class ViolationStats {
        private final int totalViolations;
        private final int pendingViolations;
        private final int processedViolations;
        private final double averageConfidence;
        
        public ViolationStats(int totalViolations, int pendingViolations, 
                            int processedViolations, double averageConfidence) {
            this.totalViolations = totalViolations;
            this.pendingViolations = pendingViolations;
            this.processedViolations = processedViolations;
            this.averageConfidence = averageConfidence;
        }
        
        // Getters
        public int getTotalViolations() { return totalViolations; }
        public int getPendingViolations() { return pendingViolations; }
        public int getProcessedViolations() { return processedViolations; }
        public double getAverageConfidence() { return averageConfidence; }
    }
}