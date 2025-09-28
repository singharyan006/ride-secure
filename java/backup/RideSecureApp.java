package com.ridesecure;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.stage.Stage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;

/**
 * RideSecure Desktop Application - Main Entry Point
 * 
 * JavaFX application for helmet detection and license plate recognition
 * from video files. Coordinates video processing, ML inference, and 
 * violation database logging.
 * 
 * @author RideSecure Team
 * @version 1.0.0
 */
public class RideSecureApp extends Application {
    
    private static final Logger logger = LoggerFactory.getLogger(RideSecureApp.class);
    private static final String APP_TITLE = "RideSecure - Helmet Detection System";
    private static final String MAIN_FXML = "/fxml/main-view.fxml";
    private static final String APP_ICON = "/images/app-icon.png";
    private static final String STYLESHEET = "/css/styles.css";
    
    @Override
    public void start(Stage primaryStage) {
        logger.info("Starting RideSecure Desktop Application...");
        
        try {
            // Load main UI layout
            FXMLLoader fxmlLoader = new FXMLLoader(getClass().getResource(MAIN_FXML));
            Scene scene = new Scene(fxmlLoader.load());
            
            // Apply stylesheet
            String stylesheet = getClass().getResource(STYLESHEET).toExternalForm();
            scene.getStylesheets().add(stylesheet);
            
            // Configure primary stage
            primaryStage.setTitle(APP_TITLE);
            primaryStage.setScene(scene);
            primaryStage.setMinWidth(1000);
            primaryStage.setMinHeight(700);
            
            // Set application icon (optional - will work without icon file)
            try {
                Image icon = new Image(getClass().getResourceAsStream(APP_ICON));
                primaryStage.getIcons().add(icon);
            } catch (Exception e) {
                logger.warn("Could not load application icon: {}", e.getMessage());
            }
            
            // Center window on screen
            primaryStage.centerOnScreen();
            
            // Show application
            primaryStage.show();
            
            logger.info("RideSecure application started successfully");
            
        } catch (IOException e) {
            logger.error("Failed to load FXML file: {}", MAIN_FXML, e);
            showErrorAndExit("Failed to load application UI", e);
        } catch (Exception e) {
            logger.error("Unexpected error during application startup", e);
            showErrorAndExit("Application startup failed", e);
        }
    }
    
    @Override
    public void stop() {
        logger.info("Shutting down RideSecure application...");
        // Cleanup resources here if needed
        // Close database connections, stop video processing, etc.
    }
    
    /**
     * Display error message and exit application
     */
    private void showErrorAndExit(String message, Exception e) {
        System.err.println("FATAL ERROR: " + message);
        System.err.println("Cause: " + e.getMessage());
        e.printStackTrace();
        System.exit(1);
    }
    
    /**
     * Application entry point
     */
    public static void main(String[] args) {
        logger.info("Launching RideSecure with arguments: {}", java.util.Arrays.toString(args));
        launch(args);
    }
}