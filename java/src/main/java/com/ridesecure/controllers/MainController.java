package com.ridesecure.controllers;

import com.ridesecure.models.Violation;
import com.ridesecure.services.APIService;
import com.ridesecure.services.DatabaseService;
import javafx.application.Platform;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.control.cell.PropertyValueFactory;
import javafx.scene.layout.StackPane;
import javafx.stage.FileChooser;

import java.awt.Desktop;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.ResourceBundle;

/**
 * Main Detection Page Controller
 * 
 * Clean and simple:
 * 1. User selects video file
 * 2. Sends to Python API
 * 3. Displays violations in table
 * 4. Saves to database
 */
public class MainController implements Initializable {
    
    @FXML private Label videoPathLabel;
    @FXML private Button selectVideoButton;
    @FXML private Button startDetectionButton;
    @FXML private Button saveToDBButton;
    @FXML private ProgressBar progressBar;
    @FXML private Label statusLabel;
    
    @FXML private TableView<Violation> violationsTable;
    @FXML private TableColumn<Violation, String> timestampColumn;
    @FXML private TableColumn<Violation, Integer> frameNumberColumn;
    @FXML private TableColumn<Violation, Double> confidenceColumn;
    
    private File selectedVideoFile;
    private String annotatedVideoPath;
    private ObservableList<Violation> violations;
    private APIService apiService;
    private DatabaseService databaseService;
    
    @Override
    public void initialize(URL location, ResourceBundle resources) {
        // Initialize services
        apiService = new APIService();
        databaseService = new DatabaseService();
        
        // Initialize table
        violations = FXCollections.observableArrayList();
        violationsTable.setItems(violations);
        
        // Setup table columns
        timestampColumn.setCellValueFactory(new PropertyValueFactory<>("timestampFormatted"));
        frameNumberColumn.setCellValueFactory(new PropertyValueFactory<>("frameNumber"));
        confidenceColumn.setCellValueFactory(new PropertyValueFactory<>("confidence"));
        
        // Format confidence as percentage
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
        
        // Initially disable buttons
        startDetectionButton.setDisable(true);
        saveToDBButton.setDisable(true);
        
        updateStatus("Ready. Please select a video file.");
    }
    
    @FXML
    private void handleSelectVideo() {
        FileChooser fileChooser = new FileChooser();
        fileChooser.setTitle("Select Video File");
        fileChooser.getExtensionFilters().add(
            new FileChooser.ExtensionFilter("Video Files", "*.mp4", "*.avi", "*.mov", "*.mkv")
        );
        
        File file = fileChooser.showOpenDialog(selectVideoButton.getScene().getWindow());
        if (file != null && file.exists()) {
            selectedVideoFile = file;
            videoPathLabel.setText(file.getName());
            startDetectionButton.setDisable(false);
            updateStatus("Video loaded: " + file.getName());
            System.out.println("✅ Selected video: " + file.getAbsolutePath());
        }
    }
    
    @FXML
    private void handleStartDetection() {
        if (selectedVideoFile == null) {
            showAlert(Alert.AlertType.WARNING, "No Video", "Please select a video file first.");
            return;
        }
        
        // Clear previous results
        violations.clear();
        
        // Disable buttons during processing
        selectVideoButton.setDisable(true);
        startDetectionButton.setDisable(true);
        progressBar.setProgress(ProgressBar.INDETERMINATE_PROGRESS);
        updateStatus("Sending video to Python ML backend...");
        
        System.out.println("🚀 Starting detection on: " + selectedVideoFile.getName());
        
        // Call Python API in background thread
        new Thread(() -> {
            try {
                // Send ENTIRE video to Python API
                APIService.ProcessingResult result = apiService.processVideo(selectedVideoFile);
                
                System.out.println("✅ Received " + result.violations.size() + " violations from Python API");
                System.out.println("✅ Annotated video path: " + result.annotatedVideoPath);
                
                // Update UI on JavaFX thread
                Platform.runLater(() -> {
                    violations.addAll(result.violations);
                    annotatedVideoPath = result.annotatedVideoPath;
                    progressBar.setProgress(1.0);
                    
                    String message = "Detection complete! Found " + result.violations.size() + " violations.";
                    if (!result.violations.isEmpty()) {
                        message += " (Saved to database automatically)";
                    }
                    updateStatus(message);
                    
                    selectVideoButton.setDisable(false);
                    startDetectionButton.setDisable(false);
                    // No need for Save button - Python already saved to DB!
                    saveToDBButton.setDisable(true);
                    
                    // Load annotated video in player
                    if (annotatedVideoPath != null) {
                        loadAnnotatedVideo(annotatedVideoPath);
                    }
                    
                    if (violations.isEmpty()) {
                        showAlert(Alert.AlertType.INFORMATION, "No Violations", 
                                 "No helmet violations detected in this video.");
                    } else {
                        showAlert(Alert.AlertType.INFORMATION, "Detection Complete", 
                                 "Found " + result.violations.size() + " violation(s).\n\n" +
                                 "✅ Automatically saved to Supabase database by Python!\n" +
                                 "📹 Annotated video is ready to play!");
                    }
                });
                
            } catch (Exception e) {
                System.err.println("❌ Detection failed: " + e.getMessage());
                e.printStackTrace();
                
                Platform.runLater(() -> {
                    progressBar.setProgress(0);
                    updateStatus("Detection failed. Is Python API running?");
                    selectVideoButton.setDisable(false);
                    startDetectionButton.setDisable(false);
                    
                    showAlert(Alert.AlertType.ERROR, "Detection Failed", 
                             "Failed to process video. Error: " + e.getMessage() +
                             "\n\nMake sure Python API is running:\ncd e:\\ride-secure\nuv run -- uvicorn src.api:app --reload");
                });
            }
        }).start();
    }
    
    @FXML
    private void handleSaveToDB() {
        if (violations.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "No Data", "No violations to save.");
            return;
        }
        
        saveToDBButton.setDisable(true);
        updateStatus("Saving to database...");
        
        new Thread(() -> {
            int savedCount = 0;
            for (Violation violation : violations) {
                try {
                    databaseService.saveViolation(violation);
                    savedCount++;
                } catch (Exception e) {
                    System.err.println("❌ Failed to save violation: " + e.getMessage());
                }
            }
            
            int finalSavedCount = savedCount;
            Platform.runLater(() -> {
                updateStatus("Saved " + finalSavedCount + " violations to database.");
                saveToDBButton.setDisable(false);
                
                if (finalSavedCount > 0) {
                    showAlert(Alert.AlertType.INFORMATION, "Success", 
                             "Saved " + finalSavedCount + " violation(s) to Supabase database.");
                } else {
                    showAlert(Alert.AlertType.ERROR, "Failed", 
                             "Could not save violations to database. Check connection.");
                }
            });
        }).start();
    }
    
    private void updateStatus(String message) {
        if (statusLabel != null) {
            statusLabel.setText(message);
        }
    }
    
    private void showAlert(Alert.AlertType type, String title, String message) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
    
    /**
     * Open annotated video in system default media player
     */
    private void loadAnnotatedVideo(String videoPath) {
        try {
            File videoFile = new File(videoPath);
            
            // Check if file exists
            if (!videoFile.exists()) {
                System.err.println("❌ Annotated video file not found: " + videoPath);
                updateStatus("Annotated video file not found: " + videoPath);
                showAlert(Alert.AlertType.ERROR, "Video Not Found", 
                         "The annotated video file was not found:\n" + videoPath);
                return;
            }
            
            System.out.println("📹 Opening video in system player: " + videoPath);
            System.out.println("📹 File size: " + (videoFile.length() / 1024) + " KB");
            
            // Check if Desktop is supported
            if (!Desktop.isDesktopSupported()) {
                System.err.println("❌ Desktop API not supported on this platform");
                updateStatus("Cannot open video: Desktop API not supported");
                showAlert(Alert.AlertType.ERROR, "Not Supported", 
                         "Cannot open video automatically on this system.\n\n" +
                         "Please open manually:\n" + videoPath);
                return;
            }
            
            Desktop desktop = Desktop.getDesktop();
            
            // Check if OPEN action is supported
            if (!desktop.isSupported(Desktop.Action.OPEN)) {
                System.err.println("❌ Desktop OPEN action not supported");
                updateStatus("Cannot open video automatically");
                showAlert(Alert.AlertType.WARNING, "Cannot Open", 
                         "Cannot open video automatically.\n\n" +
                         "Please open manually:\n" + videoPath);
                return;
            }
            
            // Open video in default system player (VLC, Windows Media Player, etc.)
            desktop.open(videoFile);
            
            updateStatus("✅ Opened annotated video in system player");
            System.out.println("✅ Successfully opened video in system default player");
            
            // Show info to user
            showAlert(Alert.AlertType.INFORMATION, "Video Opened", 
                     "The annotated video has been opened in your default media player.\n\n" +
                     "� Video: " + videoFile.getName() + "\n" +
                     "� Location: " + videoFile.getParent() + "\n\n" +
                     "You should see:\n" +
                     "• RED boxes around riders WITHOUT helmets\n" +
                     "• GREEN boxes around riders WITH helmets\n" +
                     "• Track IDs and head regions marked");
            
        } catch (IOException e) {
            System.err.println("❌ Failed to open video: " + e.getMessage());
            e.printStackTrace();
            updateStatus("Failed to open video: " + e.getMessage());
            showAlert(Alert.AlertType.ERROR, "Error Opening Video", 
                     "Failed to open the video file:\n" + e.getMessage() +
                     "\n\nVideo location:\n" + videoPath);
        } catch (Exception e) {
            System.err.println("❌ Unexpected error: " + e.getMessage());
            e.printStackTrace();
            updateStatus("Unexpected error: " + e.getMessage());
        }
    }
}
