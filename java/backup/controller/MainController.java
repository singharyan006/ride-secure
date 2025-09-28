package com.ridesecure.controller;

import javafx.application.Platform;
import javafx.concurrent.Task;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.layout.VBox;
import javafx.scene.media.Media;
import javafx.scene.media.MediaPlayer;
import javafx.scene.media.MediaView;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import com.ridesecure.model.Violation;
import com.ridesecure.service.VideoService;
import com.ridesecure.service.DatabaseService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.net.URL;
import java.time.LocalDateTime;
import java.util.ResourceBundle;

/**
 * Main UI Controller for RideSecure Desktop Application
 * 
 * Handles user interactions, video playback, detection results display,
 * and coordination between video processing and database services.
 */
public class MainController implements Initializable {
    
    private static final Logger logger = LoggerFactory.getLogger(MainController.class);
    
    // FXML injected components
    @FXML private VBox rootContainer;
    @FXML private MenuBar menuBar;
    @FXML private MenuItem openVideoMenuItem;
    @FXML private MenuItem exitMenuItem;
    
    // Video controls
    @FXML private VBox videoContainer;
    @FXML private MediaView mediaView;
    @FXML private Button playButton;
    @FXML private Button pauseButton;
    @FXML private Button stopButton;
    @FXML private Slider timeSlider;
    @FXML private Label timeLabel;
    
    // Detection controls
    @FXML private Button startDetectionButton;
    @FXML private Button stopDetectionButton;
    @FXML private CheckBox realTimeDetectionCheckbox;
    @FXML private ProgressBar detectionProgressBar;
    @FXML private Label detectionStatusLabel;
    
    // Results display
    @FXML private ImageView currentFrameImageView;
    @FXML private TableView<Violation> violationsTable;
    @FXML private TableColumn<Violation, Integer> idColumn;
    @FXML private TableColumn<Violation, LocalDateTime> timestampColumn;
    @FXML private TableColumn<Violation, String> licensePlateColumn;
    @FXML private TableColumn<Violation, Double> confidenceColumn;
    @FXML private TableColumn<Violation, String> statusColumn;
    
    // Statistics
    @FXML private Label totalViolationsLabel;
    @FXML private Label detectionAccuracyLabel;
    @FXML private Label processingSpeedLabel;
    
    // Services
    private VideoService videoService;
    private DatabaseService databaseService;
    private MediaPlayer mediaPlayer;
    private Task<Void> detectionTask;
    
    @Override
    public void initialize(URL location, ResourceBundle resources) {
        logger.info("Initializing MainController...");
        
        // Initialize services
        videoService = new VideoService();
        databaseService = new DatabaseService();
        
        // Setup UI components
        setupVideoControls();
        setupDetectionControls();
        setupViolationsTable();
        setupMenuActions();
        
        // Initialize status
        updateDetectionStatus("Ready", false);
        
        logger.info("MainController initialization complete");
    }
    
    /**
     * Setup video playback controls
     */
    private void setupVideoControls() {
        // Initially disable video controls
        playButton.setDisable(true);
        pauseButton.setDisable(true);
        stopButton.setDisable(true);
        timeSlider.setDisable(true);
        
        // Setup button actions
        playButton.setOnAction(e -> playVideo());
        pauseButton.setOnAction(e -> pauseVideo());
        stopButton.setOnAction(e -> stopVideo());
        
        // Setup time slider
        timeSlider.valueProperty().addListener((obs, oldVal, newVal) -> {
            if (mediaPlayer != null && timeSlider.isValueChanging()) {
                mediaPlayer.seek(mediaPlayer.getTotalDuration().multiply(newVal.doubleValue() / 100.0));
            }
        });
    }
    
    /**
     * Setup detection controls
     */
    private void setupDetectionControls() {
        startDetectionButton.setDisable(true);
        stopDetectionButton.setDisable(true);
        detectionProgressBar.setVisible(false);
        
        startDetectionButton.setOnAction(e -> startDetection());
        stopDetectionButton.setOnAction(e -> stopDetection());
        realTimeDetectionCheckbox.setOnAction(e -> toggleRealTimeDetection());
    }
    
    /**
     * Setup violations table columns
     */
    private void setupViolationsTable() {
        idColumn.setCellValueFactory(new PropertyValueFactory<>("id"));
        timestampColumn.setCellValueFactory(new PropertyValueFactory<>("timestamp"));
        licensePlateColumn.setCellValueFactory(new PropertyValueFactory<>("licensePlate"));
        confidenceColumn.setCellValueFactory(new PropertyValueFactory<>("detectionConfidence"));
        statusColumn.setCellValueFactory(new PropertyValueFactory<>("status"));
        
        // Format confidence column as percentage
        confidenceColumn.setCellFactory(col -> new TableCell<Violation, Double>() {
            @Override
            protected void updateItem(Double confidence, boolean empty) {
                super.updateItem(confidence, empty);
                if (empty || confidence == null) {
                    setText(null);
                } else {
                    setText(String.format("%.1f%%", confidence * 100));
                }
            }
        });
    }
    
    /**
     * Setup menu bar actions
     */
    private void setupMenuActions() {
        openVideoMenuItem.setOnAction(e -> openVideoFile());
        exitMenuItem.setOnAction(e -> exitApplication());
    }
    
    /**
     * Open video file dialog
     */
    @FXML
    private void openVideoFile() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Select Video File");
        fileChooser.getExtensionFilters().addAll(
            new FileChooser.ExtensionFilter("Video Files", "*.mp4", "*.avi", "*.mov", "*.mkv"),
            new FileChooser.ExtensionFilter("All Files", "*.*")
        );
        
        Stage stage = (Stage) rootContainer.getScene().getWindow();
        File selectedFile = fileChooser.showOpenDialog(stage);
        
        if (selectedFile != null) {
            loadVideo(selectedFile);
        }
    }
    
    /**
     * Load video file into media player
     */
    private void loadVideo(File videoFile) {
        try {
            logger.info("Loading video file: {}", videoFile.getAbsolutePath());
            
            // Cleanup existing media player
            if (mediaPlayer != null) {
                mediaPlayer.stop();
                mediaPlayer.dispose();
            }
            
            // Create new media player
            Media media = new Media(videoFile.toURI().toString());
            mediaPlayer = new MediaPlayer(media);
            mediaView.setMediaPlayer(mediaPlayer);
            
            // Setup media player listeners
            mediaPlayer.setOnReady(() -> {
                Platform.runLater(() -> {
                    enableVideoControls(true);
                    startDetectionButton.setDisable(false);
                    updateTimeLabel();
                });
            });
            
            mediaPlayer.setOnError(() -> {
                logger.error("Media player error: {}", mediaPlayer.getError());
                showAlert("Video Error", "Failed to load video file: " + mediaPlayer.getError().getMessage());
            });
            
            // Update time during playback
            mediaPlayer.currentTimeProperty().addListener((obs, oldTime, newTime) -> {
                Platform.runLater(() -> {
                    if (!timeSlider.isValueChanging()) {
                        double progress = newTime.toMillis() / mediaPlayer.getTotalDuration().toMillis() * 100.0;
                        timeSlider.setValue(progress);
                    }
                    updateTimeLabel();
                });
            });
            
            updateDetectionStatus("Video loaded: " + videoFile.getName(), false);
            
        } catch (Exception e) {
            logger.error("Failed to load video file", e);
            showAlert("Error", "Failed to load video file: " + e.getMessage());
        }
    }
    
    /**
     * Video control methods
     */
    @FXML
    private void playVideo() {
        if (mediaPlayer != null) {
            mediaPlayer.play();
        }
    }
    
    @FXML
    private void pauseVideo() {
        if (mediaPlayer != null) {
            mediaPlayer.pause();
        }
    }
    
    @FXML
    private void stopVideo() {
        if (mediaPlayer != null) {
            mediaPlayer.stop();
        }
    }
    
    /**
     * Start helmet detection process
     */
    @FXML
    private void startDetection() {
        if (mediaPlayer == null) {
            showAlert("No Video", "Please load a video file first");
            return;
        }
        
        logger.info("Starting helmet detection...");
        updateDetectionStatus("Starting detection...", true);
        
        // Create detection task
        detectionTask = new Task<Void>() {
            @Override
            protected Void call() throws Exception {
                // TODO: Implement actual detection logic
                // This is a mock implementation
                
                for (int i = 0; i <= 100; i++) {
                    if (isCancelled()) break;
                    
                    Thread.sleep(50); // Simulate processing time
                    
                    final int progress = i;
                    Platform.runLater(() -> {
                        detectionProgressBar.setProgress(progress / 100.0);
                        updateDetectionStatus("Processing frame " + progress + "/100", true);
                    });
                    
                    // Simulate finding violations occasionally
                    if (i % 20 == 0 && i > 0) {
                        Platform.runLater(() -> addMockViolation());
                    }
                }
                
                return null;
            }
            
            @Override
            protected void succeeded() {
                Platform.runLater(() -> {
                    updateDetectionStatus("Detection completed", false);
                    enableDetectionControls(false);
                });
            }
            
            @Override
            protected void failed() {
                Platform.runLater(() -> {
                    updateDetectionStatus("Detection failed", false);
                    enableDetectionControls(false);
                    showAlert("Detection Error", "Detection process failed: " + getException().getMessage());
                });
            }
        };
        
        // Start detection task
        Thread detectionThread = new Thread(detectionTask);
        detectionThread.setDaemon(true);
        detectionThread.start();
        
        enableDetectionControls(true);
    }
    
    /**
     * Stop detection process
     */
    @FXML
    private void stopDetection() {
        if (detectionTask != null && detectionTask.isRunning()) {
            detectionTask.cancel();
            updateDetectionStatus("Detection stopped", false);
            enableDetectionControls(false);
        }
    }
    
    /**
     * Toggle real-time detection mode
     */
    @FXML
    private void toggleRealTimeDetection() {
        boolean enabled = realTimeDetectionCheckbox.isSelected();
        logger.info("Real-time detection: {}", enabled ? "enabled" : "disabled");
        // TODO: Implement real-time detection logic
    }
    
    /**
     * Add mock violation for demonstration
     */
    private void addMockViolation() {
        Violation violation = new Violation();
        violation.setId(violationsTable.getItems().size() + 1);
        violation.setTimestamp(LocalDateTime.now());
        violation.setVideoSource("Current Video");
        violation.setFrameNumber((int) (Math.random() * 1000));
        violation.setDetectionConfidence(0.7 + Math.random() * 0.3);
        violation.setLicensePlate("MH" + String.format("%02d", (int) (Math.random() * 99)) + 
                                 "AB" + String.format("%04d", (int) (Math.random() * 9999)));
        violation.setStatus("DETECTED");
        
        violationsTable.getItems().add(violation);
        updateStatistics();
    }
    
    /**
     * Update UI controls
     */
    private void enableVideoControls(boolean enable) {
        playButton.setDisable(!enable);
        pauseButton.setDisable(!enable);
        stopButton.setDisable(!enable);
        timeSlider.setDisable(!enable);
    }
    
    private void enableDetectionControls(boolean detecting) {
        startDetectionButton.setDisable(detecting);
        stopDetectionButton.setDisable(!detecting);
        detectionProgressBar.setVisible(detecting);
        if (!detecting) {
            detectionProgressBar.setProgress(0);
        }
    }
    
    private void updateDetectionStatus(String status, boolean processing) {
        detectionStatusLabel.setText(status);
        // Change color based on status
        if (processing) {
            detectionStatusLabel.setStyle("-fx-text-fill: orange;");
        } else if (status.contains("completed")) {
            detectionStatusLabel.setStyle("-fx-text-fill: green;");
        } else if (status.contains("failed") || status.contains("error")) {
            detectionStatusLabel.setStyle("-fx-text-fill: red;");
        } else {
            detectionStatusLabel.setStyle("-fx-text-fill: black;");
        }
    }
    
    private void updateTimeLabel() {
        if (mediaPlayer != null) {
            double currentSeconds = mediaPlayer.getCurrentTime().toSeconds();
            double totalSeconds = mediaPlayer.getTotalDuration().toSeconds();
            timeLabel.setText(String.format("%02d:%02d / %02d:%02d", 
                (int) currentSeconds / 60, (int) currentSeconds % 60,
                (int) totalSeconds / 60, (int) totalSeconds % 60));
        }
    }
    
    private void updateStatistics() {
        totalViolationsLabel.setText(String.valueOf(violationsTable.getItems().size()));
        detectionAccuracyLabel.setText("85.7%"); // Mock value
        processingSpeedLabel.setText("12.5 FPS"); // Mock value
    }
    
    /**
     * Show alert dialog
     */
    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.ERROR);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
    
    /**
     * Exit application
     */
    @FXML
    private void exitApplication() {
        logger.info("Exiting application...");
        Platform.exit();
    }
}