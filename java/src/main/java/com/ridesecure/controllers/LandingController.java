package com.ridesecure.controllers;

import com.ridesecure.RideSecureApp;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

/**
 * Landing Page Controller
 * 
 * Simple welcome screen with a single "Get Started" button
 */
public class LandingController {
    
    @FXML
    private void handleGetStarted() {
        try {
            // Navigate to main detection page
            Parent root = FXMLLoader.load(getClass().getResource("/fxml/Main.fxml"));
            Scene scene = new Scene(root, 1400, 900);
            scene.getStylesheets().add(getClass().getResource("/css/main.css").toExternalForm());
            
            Stage stage = RideSecureApp.getPrimaryStage();
            stage.setScene(scene);
            stage.setTitle("RideSecure - Detection Dashboard");
            
        } catch (Exception e) {
            e.printStackTrace();
            System.err.println("Failed to load main page: " + e.getMessage());
        }
    }
}
