package com.ridesecure.services;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ridesecure.models.Violation;
import okhttp3.*;

import java.io.File;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * API Service - Communicates with Python FastAPI backend
 * 
 * Simple HTTP client that:
 * 1. Sends video file to Python
 * 2. Python processes entire video
 * 3. Returns all violations at once
 */
public class APIService {
    
    private static final String API_BASE_URL = "http://127.0.0.1:8000";
    private final OkHttpClient client;
    private final ObjectMapper objectMapper;
    
    public APIService() {
        // Create HTTP client with generous timeouts (video processing takes time!)
        this.client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(300, TimeUnit.SECONDS)  // 5 minutes for video processing
                .writeTimeout(60, TimeUnit.SECONDS)
                .build();
        
        this.objectMapper = new ObjectMapper();
    }
    
    /**
     * Result class for video processing
     */
    public static class ProcessingResult {
        public final List<Violation> violations;
        public final String annotatedVideoPath;
        
        public ProcessingResult(List<Violation> violations, String annotatedVideoPath) {
            this.violations = violations;
            this.annotatedVideoPath = annotatedVideoPath;
        }
    }
    
    /**
     * Process entire video file through Python ML backend
     * 
     * Python will:
     * 1. Process the video
     * 2. Detect violations
     * 3. Save directly to Supabase database
     * 4. Generate annotated video
     * 5. Return summary
     * 
     * Then we fetch violations from database to display
     * 
     * @param videoFile The video file to process
     * @return ProcessingResult with violations and annotated video path
     * @throws Exception if API call fails
     */
    public ProcessingResult processVideo(File videoFile) throws Exception {
        System.out.println("📤 Sending video to Python API: " + videoFile.getName());
        System.out.println("   File size: " + (videoFile.length() / 1024) + " KB");
        
        // Build multipart request with video file
        RequestBody requestBody = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("file", videoFile.getName(),
                        RequestBody.create(videoFile, MediaType.parse("video/mp4")))
                .addFormDataPart("coco_model", "yolov8n")
                .addFormDataPart("helmet_model", "custom_helmet")
                .addFormDataPart("conf", "0.4")
                .addFormDataPart("save_to_db", "true")  // Tell Python to save to DB
                .addFormDataPart("create_annotated_video", "true")  // Generate annotated video!
                .build();
        
        Request request = new Request.Builder()
                .url(API_BASE_URL + "/process-video")
                .post(requestBody)
                .build();
        
        // Execute request
        long startTime = System.currentTimeMillis();
        try (Response response = client.newCall(request).execute()) {
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("⏱️ API response received in " + (duration / 1000.0) + " seconds");
            
            if (!response.isSuccessful()) {
                String errorBody = response.body() != null ? response.body().string() : "Unknown error";
                throw new Exception("API call failed with code " + response.code() + ": " + errorBody);
            }
            
            String responseBody = response.body().string();
            System.out.println("📥 API Response: " + responseBody.substring(0, Math.min(200, responseBody.length())) + "...");
            
            // Parse response to get stats and annotated video path
            JsonNode rootNode = objectMapper.readTree(responseBody);
            int totalViolations = rootNode.path("stats").path("total_violations").asInt(0);
            int savedToDb = rootNode.path("stats").path("saved_to_db").asInt(0);
            String annotatedVideoPath = rootNode.path("annotated_video_path").asText(null);
            
            System.out.println("✅ Python processed video and saved " + savedToDb + " violations to database");
            if (annotatedVideoPath != null) {
                System.out.println("✅ Annotated video created: " + annotatedVideoPath);
            }
            
            // Now fetch violations from database
            List<Violation> violations = fetchViolationsByVideo(videoFile.getName());
            
            return new ProcessingResult(violations, annotatedVideoPath);
        }
    }
    
    /**
     * Fetch violations for a specific video from database via Python API
     * 
     * @param videoName Name of the video file
     * @return List of violations from database
     * @throws Exception if API call fails
     */
    public List<Violation> fetchViolationsByVideo(String videoName) throws Exception {
        System.out.println("📥 Fetching violations from database for: " + videoName);
        
        Request request = new Request.Builder()
                .url(API_BASE_URL + "/violations/by-video/" + videoName)
                .get()
                .build();
        
        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new Exception("Failed to fetch violations: HTTP " + response.code());
            }
            
            String responseBody = response.body().string();
            JsonNode rootNode = objectMapper.readTree(responseBody);
            JsonNode violationsArray = rootNode.get("violations");
            
            if (violationsArray == null || !violationsArray.isArray()) {
                System.out.println("⚠️ No violations in database for this video");
                return new ArrayList<>();
            }
            
            List<Violation> violations = new ArrayList<>();
            
            for (JsonNode violationNode : violationsArray) {
                try {
                    Violation violation = new Violation();
                    violation.setId(violationNode.get("id").asInt());
                    violation.setVideoSource(videoName);
                    
                    // Parse timestamp
                    String timestampStr = violationNode.get("timestamp").asText();
                    // Convert ISO timestamp to LocalDateTime
                    violation.setTimestamp(LocalDateTime.parse(timestampStr.substring(0, 19)));
                    
                    // Get frame number
                    violation.setFrameNumber(violationNode.get("frame_number").asInt());
                    
                    // Get bounding box (match database schema: x1, y1, x2, y2)
                    violation.setBboxX1(violationNode.get("x1").asInt());
                    violation.setBboxY1(violationNode.get("y1").asInt());
                    violation.setBboxX2(violationNode.get("x2").asInt());
                    violation.setBboxY2(violationNode.get("y2").asInt());
                    
                    // Get confidence (match database schema: confidence_score)
                    violation.setConfidence(violationNode.get("confidence_score").asDouble());
                    
                    // Store raw JSON
                    if (violationNode.has("raw_detection")) {
                        violation.setRawDetection(violationNode.get("raw_detection").toString());
                    }
                    
                    violations.add(violation);
                    
                } catch (Exception e) {
                    System.err.println("⚠️ Failed to parse violation: " + e.getMessage());
                }
            }
            
            System.out.println("✅ Fetched " + violations.size() + " violations from database");
            return violations;
        }
    }
}
