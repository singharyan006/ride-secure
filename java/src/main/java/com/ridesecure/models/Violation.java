package com.ridesecure.models;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Violation Model - Simplified to match Supabase schema
 * 
 * Represents a single helmet violation detection
 */
public class Violation {
    private Integer id;
    private LocalDateTime timestamp;
    private String videoSource;
    private Integer frameNumber;
    private Integer bboxX1;
    private Integer bboxY1;
    private Integer bboxX2;
    private Integer bboxY2;
    private Double confidence;
    private String rawDetection;  // JSON string
    
    private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    // Constructors
    public Violation() {
        this.timestamp = LocalDateTime.now();
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
    
    // For TableView display
    public String getTimestampFormatted() {
        return timestamp != null ? timestamp.format(FORMATTER) : "";
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
    
    public Integer getBboxX1() {
        return bboxX1;
    }
    
    public void setBboxX1(Integer bboxX1) {
        this.bboxX1 = bboxX1;
    }
    
    public Integer getBboxY1() {
        return bboxY1;
    }
    
    public void setBboxY1(Integer bboxY1) {
        this.bboxY1 = bboxY1;
    }
    
    public Integer getBboxX2() {
        return bboxX2;
    }
    
    public void setBboxX2(Integer bboxX2) {
        this.bboxX2 = bboxX2;
    }
    
    public Integer getBboxY2() {
        return bboxY2;
    }
    
    public void setBboxY2(Integer bboxY2) {
        this.bboxY2 = bboxY2;
    }
    
    public Double getConfidence() {
        return confidence;
    }
    
    public void setConfidence(Double confidence) {
        this.confidence = confidence;
    }
    
    public String getRawDetection() {
        return rawDetection;
    }
    
    public void setRawDetection(String rawDetection) {
        this.rawDetection = rawDetection;
    }
    
    @Override
    public String toString() {
        return String.format("Violation[id=%d, video=%s, frame=%d, conf=%.2f]",
                id, videoSource, frameNumber, confidence);
    }
}
