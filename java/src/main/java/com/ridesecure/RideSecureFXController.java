package com.ridesecure;

import com.ridesecure.model.Violation;
import com.ridesecure.service.DatabaseService;

import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.StackPane;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.animation.Timeline;
import javafx.animation.KeyFrame;
import javafx.event.ActionEvent;
import javafx.util.Duration;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.ResourceBundle;
import javax.imageio.ImageIO;

public class RideSecureFXController implements Initializable {
    
    // Video Display
    @FXML private StackPane videoStackPane;
    @FXML private ImageView videoImageView;
    @FXML private Label videoStatusLabel;
    
    // Video Controls
    @FXML private Button openVideoButton;
    @FXML private Button playButton;
    @FXML private Button pauseButton;
    @FXML private Button stopButton;
    @FXML private Slider timeSlider;
    @FXML private Label timeLabel;
    
    // Detection Controls
    @FXML private Button startDetectionButton;
    @FXML private Button stopDetectionButton;
    @FXML private CheckBox realTimeCheckbox;
    @FXML private ProgressBar progressBar;
    @FXML private Label statusLabel;
    
    // Statistics
    @FXML private Label totalViolationsLabel;
    @FXML private Label accuracyLabel;
    @FXML private Label speedLabel;
    
    // Table
    @FXML private TableView<ViolationTableItem> violationsTable;
    @FXML private TableColumn<ViolationTableItem, Integer> idColumn;
    @FXML private TableColumn<ViolationTableItem, String> timeColumn;
    @FXML private TableColumn<ViolationTableItem, String> plateColumn;
    @FXML private TableColumn<ViolationTableItem, String> confidenceColumn;
    @FXML private TableColumn<ViolationTableItem, String> statusColumn;
    
    // Action Buttons
    @FXML private Button exportButton;
    @FXML private Button clearButton;
    @FXML private Button settingsButton;
    
    // Status Bar
    @FXML private Label statusBarLeft;
    
    // Data
    private File currentVideoFile;
    private List<BufferedImage> videoFrames;
    private int currentFrameIndex = 0;
    private int totalFrames = 0;
    private double frameRate = 30.0;
    private boolean isPlaying = false;
    private Timeline videoTimeline;
    private Timeline detectionTimeline;
    private DatabaseService databaseService;
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        initializeDatabase();
        setupTableColumns();
        setupTimeSlider();
        updateStatus("Ready - Load a video to begin");
    }
    
    private void initializeDatabase() {
        try {
            databaseService = DatabaseService.getInstance();
            System.out.println("✓ Database service initialized successfully");
            loadExistingViolations();
        } catch (Exception e) {
            System.out.println("⚠ Database service unavailable: " + e.getMessage());
            System.out.println("→ Application will run in offline mode");
            databaseService = null;
            showAlert(Alert.AlertType.WARNING, "Database Warning", 
                     "Database connection failed. Running in offline mode.", 
                     e.getMessage());
        }
    }
    
    private void setupTableColumns() {
        idColumn.setCellValueFactory(new PropertyValueFactory<>("id"));
        timeColumn.setCellValueFactory(new PropertyValueFactory<>("time"));
        plateColumn.setCellValueFactory(new PropertyValueFactory<>("licensePlate"));
        confidenceColumn.setCellValueFactory(new PropertyValueFactory<>("confidence"));
        statusColumn.setCellValueFactory(new PropertyValueFactory<>("status"));
    }
    
    private void setupTimeSlider() {
        timeSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (!timeSlider.isValueChanging() && !isPlaying && videoFrames != null) {
                currentFrameIndex = newVal.intValue();
                showFrame(currentFrameIndex);
            }
        });
    }
    
    @FXML
    private void openVideoFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Open Video File");
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("Video Files", "*.mp4", "*.avi", "*.mov", "*.mkv"),
            new FileChooser.ExtensionFilter("All Files", "*.*")
        );
        
        Stage stage = (Stage) openVideoButton.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        
        if (selectedFile != null) {
            currentVideoFile = selectedFile;
            loadVideo();
        }
    }
    
    private void loadVideo() {
        if (currentVideoFile == null) return;
        
        videoStatusLabel.setText("Loading video frames...");
        updateStatus("Extracting frames from: " + currentVideoFile.getName());
        
        Task<Void> frameExtractionTask = new Task<Void>() {
            @Override
            protected Void call() throws Exception {
                extractVideoFrames();
                return null;
            }
            
            @Override
            protected void succeeded() {
                Platform.runLater(() -> {
                    if (videoFrames != null && !videoFrames.isEmpty()) {
                        totalFrames = videoFrames.size();
                        timeSlider.setMax(totalFrames - 1);
                        timeSlider.setValue(0);
                        currentFrameIndex = 0;
                        
                        showFrame(0);
                        videoStatusLabel.setText(currentVideoFile.getName() + " (" + totalFrames + " frames)");
                        updateStatus("Video loaded successfully: " + totalFrames + " frames");
                        
                        // Enable controls
                        playButton.setDisable(false);
                        pauseButton.setDisable(false);
                        stopButton.setDisable(false);
                        timeSlider.setDisable(false);
                        startDetectionButton.setDisable(false);
                    } else {
                        videoStatusLabel.setText("Failed to load video");
                        updateStatus("Failed to extract frames");
                        showAlert(Alert.AlertType.ERROR, "Video Error", 
                                "Could not extract frames from video.", 
                                "Make sure FFmpeg is installed or try a different video format.");
                    }
                });
            }
            
            @Override
            protected void failed() {
                Platform.runLater(() -> {
                    videoStatusLabel.setText("Failed to load video");
                    updateStatus("Failed to extract frames: " + getException().getMessage());
                    showAlert(Alert.AlertType.ERROR, "Video Error", 
                            "Failed to load video.", getException().getMessage());
                });
            }
        };
        
        Thread frameExtractionThread = new Thread(frameExtractionTask);
        frameExtractionThread.setDaemon(true);
        frameExtractionThread.start();
    }
    
    @FXML
    private void playVideo() {
        if (videoFrames == null || videoFrames.isEmpty()) {
            updateStatus("No video loaded");
            return;
        }
        
        isPlaying = true;
        updateStatus("Playing video: " + currentVideoFile.getName());
        
        if (videoTimeline != null) {
            videoTimeline.stop();
        }
        
        Duration frameDuration = Duration.millis(1000.0 / frameRate);
        videoTimeline = new Timeline(new KeyFrame(frameDuration, e -> {
            if (isPlaying && currentFrameIndex < videoFrames.size()) {
                showFrame(currentFrameIndex);
                currentFrameIndex++;
                timeSlider.setValue(currentFrameIndex);
                
                if (currentFrameIndex >= videoFrames.size()) {
                    stopVideo();
                }
            }
        }));
        
        videoTimeline.setCycleCount(Timeline.INDEFINITE);
        videoTimeline.play();
        
        playButton.setDisable(true);
        pauseButton.setDisable(false);
        stopButton.setDisable(false);
    }
    
    @FXML
    private void pauseVideo() {
        isPlaying = false;
        if (videoTimeline != null) {
            videoTimeline.stop();
        }
        
        updateStatus("Video paused");
        playButton.setDisable(false);
        pauseButton.setDisable(true);
    }
    
    @FXML
    private void stopVideo() {
        isPlaying = false;
        if (videoTimeline != null) {
            videoTimeline.stop();
        }
        
        currentFrameIndex = 0;
        timeSlider.setValue(0);
        timeLabel.setText("00:00");
        
        if (videoFrames != null && !videoFrames.isEmpty()) {
            showFrame(0);
        }
        
        updateStatus("Video stopped");
        playButton.setDisable(false);
        pauseButton.setDisable(true);
        stopButton.setDisable(false);
    }
    
    @FXML
    private void startDetection() {
        if (currentVideoFile == null) {
            showAlert(Alert.AlertType.WARNING, "No Video", "Please load a video file first.", "");
            return;
        }
        
        startDetectionButton.setDisable(true);
        stopDetectionButton.setDisable(false);
        progressBar.setProgress(0);
        
        updateStatus("Starting helmet detection...");
        
        // Simulate detection process
        if (detectionTimeline != null) {
            detectionTimeline.stop();
        }
        
        final int[] progress = {0};
        final int[] violationCount = {0};
        
        detectionTimeline = new Timeline(new KeyFrame(Duration.millis(100), e -> {
            progress[0]++;
            progressBar.setProgress(progress[0] / 100.0);
            
            updateStatus("Processing frame " + progress[0] + "/100");
            
            // Simulate finding violations occasionally
            if (progress[0] % 20 == 0 && progress[0] > 0) {
                addMockViolation(++violationCount[0]);
            }
            
            if (progress[0] >= 100) {
                detectionTimeline.stop();
                finishDetection();
            }
        }));
        
        detectionTimeline.setCycleCount(100);
        detectionTimeline.play();
    }
    
    @FXML
    private void stopDetection() {
        if (detectionTimeline != null) {
            detectionTimeline.stop();
        }
        finishDetection();
        updateStatus("Detection stopped by user");
    }
    
    private void finishDetection() {
        startDetectionButton.setDisable(false);
        stopDetectionButton.setDisable(true);
        progressBar.setProgress(1.0);
        
        updateStatus("Detection completed");
        updateStatistics();
    }
    
    @FXML
    private void exportReport() {
        showAlert(Alert.AlertType.INFORMATION, "Export Report", 
                 "Export functionality will be implemented", "");
    }
    
    @FXML
    private void clearResults() {
        Alert alert = new Alert(Alert.AlertType.CONFIRMATION);
        alert.setTitle("Clear Results");
        alert.setHeaderText("Choose what to clear:");
        
        ButtonType tableOnly = new ButtonType("Clear Table Only");
        ButtonType tableAndDb = new ButtonType("Clear Table & Database");
        ButtonType cancel = new ButtonType("Cancel", ButtonBar.ButtonData.CANCEL_CLOSE);
        
        alert.getButtonTypes().setAll(tableOnly, tableAndDb, cancel);
        
        Optional<ButtonType> result = alert.showAndWait();
        if (result.isPresent()) {
            if (result.get() == tableOnly) {
                violationsTable.getItems().clear();
                updateStatus("Table cleared");
            } else if (result.get() == tableAndDb) {
                Alert confirmAlert = new Alert(Alert.AlertType.CONFIRMATION);
                confirmAlert.setTitle("Confirm Database Clear");
                confirmAlert.setHeaderText("This will permanently delete ALL violations from the database!");
                confirmAlert.setContentText("Are you sure?");
                
                Optional<ButtonType> confirmResult = confirmAlert.showAndWait();
                if (confirmResult.isPresent() && confirmResult.get() == ButtonType.OK) {
                    clearDatabase();
                    violationsTable.getItems().clear();
                    updateStatistics();
                    updateStatus("Database and table cleared");
                }
            }
        }
    }
    
    @FXML
    private void showSettings() {
        showAlert(Alert.AlertType.INFORMATION, "Settings", 
                 "Settings dialog will be implemented", "");
    }
    
    @FXML
    private void showAbout() {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle("About RideSecure");
        alert.setHeaderText("RideSecure - Helmet Detection System");
        alert.setContentText("Version 1.0.0\n\n" +
                           "A hybrid Java + Python application for automated\n" +
                           "motorcycle helmet compliance monitoring and\n" +
                           "license plate recognition.\n\n" +
                           "Built with JavaFX and CSS styling.");
        alert.showAndWait();
    }
    
    @FXML
    private void exitApplication() {
        Platform.exit();
    }
    
    // Helper methods (similar to Swing version but adapted for JavaFX)
    
    private void extractVideoFrames() {
        videoFrames = new ArrayList<>();
        
        try {
            // Create temp directory for frames
            File tempDir = new File(System.getProperty("java.io.tmpdir"), "ridesecure_frames");
            if (!tempDir.exists()) {
                tempDir.mkdirs();
            }
            
            // Clear old frames
            File[] oldFrames = tempDir.listFiles((dir, name) -> name.startsWith("frame_") && name.endsWith(".jpg"));
            if (oldFrames != null) {
                for (File frame : oldFrames) {
                    frame.delete();
                }
            }
            
            // Use FFmpeg to extract frames (if available)
            String ffmpegCmd = String.format(
                "ffmpeg -i \"%s\" -vf fps=10 \"%s/frame_%%04d.jpg\"",
                currentVideoFile.getAbsolutePath(),
                tempDir.getAbsolutePath()
            );
            
            // Try to run FFmpeg
            Process process = Runtime.getRuntime().exec(ffmpegCmd);
            
            // Wait for completion with timeout
            boolean finished = process.waitFor(30, java.util.concurrent.TimeUnit.SECONDS);
            
            if (finished && process.exitValue() == 0) {
                // Load extracted frames
                File[] frameFiles = tempDir.listFiles((dir, name) -> 
                    name.startsWith("frame_") && name.endsWith(".jpg"));
                
                if (frameFiles != null && frameFiles.length > 0) {
                    java.util.Arrays.sort(frameFiles);
                    frameRate = 10.0; // We extracted at 10 FPS
                    
                    for (File frameFile : frameFiles) {
                        try {
                            BufferedImage frame = ImageIO.read(frameFile);
                            if (frame != null) {
                                // Scale frame to fit display
                                BufferedImage scaledFrame = scaleImage(frame, 640, 360);
                                videoFrames.add(scaledFrame);
                            }
                        } catch (Exception e) {
                            System.err.println("Error loading frame: " + frameFile.getName());
                        }
                    }
                }
            } else {
                // FFmpeg not available, create placeholder frames
                System.out.println("FFmpeg not found, creating placeholder frames");
                createPlaceholderFrames();
            }
            
        } catch (Exception e) {
            System.err.println("Frame extraction failed: " + e.getMessage());
            createPlaceholderFrames();
        }
    }
    
    private void createPlaceholderFrames() {
        videoFrames = new ArrayList<>();
        frameRate = 30.0;
        
        // Create 100 placeholder frames with different colors/text
        for (int i = 0; i < 100; i++) {
            BufferedImage frame = new BufferedImage(640, 360, BufferedImage.TYPE_INT_RGB);
            java.awt.Graphics2D g2d = frame.createGraphics();
            
            // Different background colors
            java.awt.Color bgColor = java.awt.Color.getHSBColor((float)i / 100, 0.3f, 0.8f);
            g2d.setColor(bgColor);
            g2d.fillRect(0, 0, 640, 360);
            
            // Add frame info
            g2d.setColor(java.awt.Color.BLACK);
            g2d.setFont(new java.awt.Font("Arial", java.awt.Font.BOLD, 24));
            String frameText = "Frame " + (i + 1) + "/100";
            java.awt.FontMetrics fm = g2d.getFontMetrics();
            int textX = (640 - fm.stringWidth(frameText)) / 2;
            int textY = 180;
            g2d.drawString(frameText, textX, textY);
            
            // Add video filename
            g2d.setFont(new java.awt.Font("Arial", java.awt.Font.PLAIN, 16));
            String filename = currentVideoFile.getName();
            fm = g2d.getFontMetrics();
            textX = (640 - fm.stringWidth(filename)) / 2;
            textY = 200;
            g2d.drawString(filename, textX, textY);
            
            g2d.dispose();
            videoFrames.add(frame);
        }
    }
    
    private BufferedImage scaleImage(BufferedImage original, int maxWidth, int maxHeight) {
        int originalWidth = original.getWidth();
        int originalHeight = original.getHeight();
        
        // Calculate scaling factor while maintaining aspect ratio
        double scaleX = (double) maxWidth / originalWidth;
        double scaleY = (double) maxHeight / originalHeight;
        double scale = Math.min(scaleX, scaleY);
        
        int scaledWidth = (int) (originalWidth * scale);
        int scaledHeight = (int) (originalHeight * scale);
        
        BufferedImage scaled = new BufferedImage(scaledWidth, scaledHeight, BufferedImage.TYPE_INT_RGB);
        java.awt.Graphics2D g2d = scaled.createGraphics();
        g2d.setRenderingHint(java.awt.RenderingHints.KEY_INTERPOLATION, java.awt.RenderingHints.VALUE_INTERPOLATION_BILINEAR);
        g2d.drawImage(original, 0, 0, scaledWidth, scaledHeight, null);
        g2d.dispose();
        
        return scaled;
    }
    
    private void showFrame(int frameIndex) {
        if (videoFrames != null && frameIndex >= 0 && frameIndex < videoFrames.size()) {
            try {
                BufferedImage bufferedImage = videoFrames.get(frameIndex);
                
                // Convert BufferedImage to JavaFX Image
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
                ImageIO.write(bufferedImage, "png", outputStream);
                ByteArrayInputStream inputStream = new ByteArrayInputStream(outputStream.toByteArray());
                Image fxImage = new Image(inputStream);
                
                videoImageView.setImage(fxImage);
                
                // Update time
                double seconds = frameIndex / frameRate;
                int minutes = (int) seconds / 60;
                int secs = (int) seconds % 60;
                timeLabel.setText(String.format("%02d:%02d", minutes, secs));
                
            } catch (Exception e) {
                System.err.println("Error displaying frame: " + e.getMessage());
            }
        }
    }
    
    private void addMockViolation(int id) {
        // Create a real violation object
        Violation violation = new Violation();
        violation.setTimestamp(LocalDateTime.now());
        violation.setVideoSource(currentVideoFile != null ? currentVideoFile.getName() : "sample_video.mp4");
        violation.setFrameNumber(id * 125 + (int)(Math.random() * 100));
        
        double detectionConfidence = 70 + Math.random() * 30;
        violation.setDetectionConfidence(detectionConfidence / 100.0);
        
        String licensePlate = "MH" + String.format("%02d", (int)(Math.random() * 99)) + 
                             "AB" + String.format("%04d", (int)(Math.random() * 9999));
        violation.setLicensePlate(licensePlate);
        violation.setPlateConfidence(0.8 + Math.random() * 0.2);
        
        violation.setViolationType("NO_HELMET");
        violation.setStatus("DETECTED");
        violation.setLocationInfo("Traffic Junction " + (int)(Math.random() * 10 + 1));
        
        // Save to database
        if (databaseService != null && databaseService.saveViolation(violation)) {
            System.out.println("Violation saved: ID=" + violation.getId() + ", Plate=" + licensePlate);
        }
        
        // Add to table display
        String timestamp = violation.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
        String confidence = String.format("%.1f%%", detectionConfidence);
        
        ViolationTableItem tableItem = new ViolationTableItem(
            violation.getId(), timestamp, licensePlate, confidence, violation.getStatus()
        );
        
        Platform.runLater(() -> {
            violationsTable.getItems().add(tableItem);
            violationsTable.scrollTo(tableItem);
        });
    }
    
    private void loadExistingViolations() {
        if (databaseService == null) return;
        
        try {
            List<Violation> violations = databaseService.getAllViolations();
            
            for (Violation violation : violations) {
                String timestamp = violation.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
                String confidence = String.format("%.1f%%", violation.getDetectionConfidence() * 100);
                
                ViolationTableItem tableItem = new ViolationTableItem(
                    violation.getId(), timestamp, violation.getLicensePlate(), 
                    confidence, violation.getStatus()
                );
                violationsTable.getItems().add(tableItem);
            }
            
            updateStatistics();
            System.out.println("Loaded " + violations.size() + " existing violations from database");
            
        } catch (Exception e) {
            System.err.println("Failed to load existing violations: " + e.getMessage());
        }
    }
    
    private void clearDatabase() {
        if (databaseService == null) return;
        
        try {
            List<Violation> violations = databaseService.getAllViolations();
            for (Violation violation : violations) {
                databaseService.deleteViolation(violation.getId());
            }
            System.out.println("Cleared " + violations.size() + " violations from database");
        } catch (Exception e) {
            System.err.println("Failed to clear database: " + e.getMessage());
            showAlert(Alert.AlertType.ERROR, "Database Error", 
                     "Failed to clear database", e.getMessage());
        }
    }
    
    private void updateStatistics() {
        Platform.runLater(() -> {
            if (databaseService != null) {
                try {
                    DatabaseService.ViolationStats stats = databaseService.getViolationStats();
                    totalViolationsLabel.setText(String.valueOf(stats.getTotalViolations()));
                    accuracyLabel.setText(String.format("%.1f%%", stats.getAverageConfidence() * 100));
                } catch (Exception e) {
                    totalViolationsLabel.setText(String.valueOf(violationsTable.getItems().size()));
                    accuracyLabel.setText("85.7%"); // Mock value
                }
            } else {
                totalViolationsLabel.setText(String.valueOf(violationsTable.getItems().size()));
                accuracyLabel.setText("85.7%"); // Mock value
            }
            speedLabel.setText("12.5 FPS"); // Mock value
        });
    }
    
    private void updateStatus(String status) {
        Platform.runLater(() -> {
            statusLabel.setText(status);
            statusBarLeft.setText(" " + status);
        });
    }
    
    private void showAlert(Alert.AlertType type, String title, String header, String content) {
        Platform.runLater(() -> {
            Alert alert = new Alert(type);
            alert.setTitle(title);
            alert.setHeaderText(header);
            alert.setContentText(content);
            alert.showAndWait();
        });
    }
    
    // Table item class for JavaFX TableView
    public static class ViolationTableItem {
        private Integer id;
        private String time;
        private String licensePlate;
        private String confidence;
        private String status;
        
        public ViolationTableItem(Integer id, String time, String licensePlate, String confidence, String status) {
            this.id = id;
            this.time = time;
            this.licensePlate = licensePlate;
            this.confidence = confidence;
            this.status = status;
        }
        
        // Getters for JavaFX property binding
        public Integer getId() { return id; }
        public String getTime() { return time; }
        public String getLicensePlate() { return licensePlate; }
        public String getConfidence() { return confidence; }
        public String getStatus() { return status; }
    }
}