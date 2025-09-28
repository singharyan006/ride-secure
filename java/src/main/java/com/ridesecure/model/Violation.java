package com.ridesecure.model;

import java.time.LocalDateTime;

/**
 * Data model representing a helmet violation detection
 * 
 * Contains all information about a detected violation including
 * detection metadata, license plate information, and database tracking.
 */
public class Violation {
    
    private Integer id;
    private LocalDateTime timestamp;
    private String videoSource;
    private Integer frameNumber;
    private Double detectionConfidence;
    private String licensePlate;
    private Double plateConfidence;
    private String snapshotPath;
    private String locationInfo;
    private String violationType;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // Default constructor
    public Violation() {
        this.timestamp = LocalDateTime.now();
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        this.violationType = "NO_HELMET";
        this.status = "DETECTED";
    }
    
    // Constructor with essential fields
    public Violation(String videoSource, Integer frameNumber, Double detectionConfidence) {
        this();
        this.videoSource = videoSource;
        this.frameNumber = frameNumber;
        this.detectionConfidence = detectionConfidence;
    }
    
    // Getters and Setters
    public Integer getId() {
        return id;
    }
    
    public void setId(Integer id) {
        this.id = id;
    }
    
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
    
    public String getVideoSource() {
        return videoSource;
    }
    
    public void setVideoSource(String videoSource) {
        this.videoSource = videoSource;
    }
    
    public Integer getFrameNumber() {
        return frameNumber;
    }
    
    public void setFrameNumber(Integer frameNumber) {
        this.frameNumber = frameNumber;
    }
    
    public Double getDetectionConfidence() {
        return detectionConfidence;
    }
    
    public void setDetectionConfidence(Double detectionConfidence) {
        this.detectionConfidence = detectionConfidence;
    }
    
    public String getLicensePlate() {
        return licensePlate;
    }
    
    public void setLicensePlate(String licensePlate) {
        this.licensePlate = licensePlate;
    }
    
    public Double getPlateConfidence() {
        return plateConfidence;
    }
    
    public void setPlateConfidence(Double plateConfidence) {
        this.plateConfidence = plateConfidence;
    }
    
    public String getSnapshotPath() {
        return snapshotPath;
    }
    
    public void setSnapshotPath(String snapshotPath) {
        this.snapshotPath = snapshotPath;
    }
    
    public String getLocationInfo() {
        return locationInfo;
    }
    
    public void setLocationInfo(String locationInfo) {
        this.locationInfo = locationInfo;
    }
    
    public String getViolationType() {
        return violationType;
    }
    
    public void setViolationType(String violationType) {
        this.violationType = violationType;
    }
    
    public String getStatus() {
        return status;
    }
    
    public void setStatus(String status) {
        this.status = status;
        this.updatedAt = LocalDateTime.now();
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    @Override
    public String toString() {
        return String.format("Violation{id=%d, plate='%s', confidence=%.2f, status='%s'}", 
            id, licensePlate, detectionConfidence, status);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        Violation violation = (Violation) obj;
        return id != null ? id.equals(violation.id) : violation.id == null;
    }
    
    @Override
    public int hashCode() {
        return id != null ? id.hashCode() : 0;
    }
}