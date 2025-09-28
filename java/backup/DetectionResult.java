package com.ridesecure.model;

import java.awt.Rectangle;
import java.util.List;

/**
 * Wrapper class for ML detection results
 * 
 * Contains detection bounding boxes, confidence scores,
 * and classification results from YOLO models.
 */
public class DetectionResult {
    
    private List<Detection> detections;
    private String modelName;
    private String modelVersion;
    private long inferenceTimeMs;
    private int frameWidth;
    private int frameHeight;
    
    public DetectionResult() {}
    
    public DetectionResult(List<Detection> detections, String modelName) {
        this.detections = detections;
        this.modelName = modelName;
    }
    
    /**
     * Individual detection within a frame
     */
    public static class Detection {
        private Rectangle boundingBox;
        private String className;
        private double confidence;
        private String label;
        
        public Detection() {}
        
        public Detection(Rectangle boundingBox, String className, double confidence) {
            this.boundingBox = boundingBox;
            this.className = className;
            this.confidence = confidence;
            this.label = String.format("%s (%.1f%%)", className, confidence * 100);
        }
        
        // Getters and Setters
        public Rectangle getBoundingBox() {
            return boundingBox;
        }
        
        public void setBoundingBox(Rectangle boundingBox) {
            this.boundingBox = boundingBox;
        }
        
        public String getClassName() {
            return className;
        }
        
        public void setClassName(String className) {
            this.className = className;
        }
        
        public double getConfidence() {
            return confidence;
        }
        
        public void setConfidence(double confidence) {
            this.confidence = confidence;
        }
        
        public String getLabel() {
            return label;
        }
        
        public void setLabel(String label) {
            this.label = label;
        }
        
        @Override
        public String toString() {
            return String.format("Detection{class='%s', confidence=%.3f, box=%s}", 
                className, confidence, boundingBox);
        }
    }
    
    // Getters and Setters
    public List<Detection> getDetections() {
        return detections;
    }
    
    public void setDetections(List<Detection> detections) {
        this.detections = detections;
    }
    
    public String getModelName() {
        return modelName;
    }
    
    public void setModelName(String modelName) {
        this.modelName = modelName;
    }
    
    public String getModelVersion() {
        return modelVersion;
    }
    
    public void setModelVersion(String modelVersion) {
        this.modelVersion = modelVersion;
    }
    
    public long getInferenceTimeMs() {
        return inferenceTimeMs;
    }
    
    public void setInferenceTimeMs(long inferenceTimeMs) {
        this.inferenceTimeMs = inferenceTimeMs;
    }
    
    public int getFrameWidth() {
        return frameWidth;
    }
    
    public void setFrameWidth(int frameWidth) {
        this.frameWidth = frameWidth;
    }
    
    public int getFrameHeight() {
        return frameHeight;
    }
    
    public void setFrameHeight(int frameHeight) {
        this.frameHeight = frameHeight;
    }
    
    // Utility methods
    public boolean hasDetections() {
        return detections != null && !detections.isEmpty();
    }
    
    public int getDetectionCount() {
        return detections != null ? detections.size() : 0;
    }
    
    public double getMaxConfidence() {
        if (detections == null || detections.isEmpty()) {
            return 0.0;
        }
        return detections.stream()
            .mapToDouble(Detection::getConfidence)
            .max()
            .orElse(0.0);
    }
    
    @Override
    public String toString() {
        return String.format("DetectionResult{model='%s', detections=%d, maxConf=%.3f, time=%dms}", 
            modelName, getDetectionCount(), getMaxConfidence(), inferenceTimeMs);
    }
}