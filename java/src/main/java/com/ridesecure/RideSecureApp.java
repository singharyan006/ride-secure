package com.ridesecure;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

/**
 * Main JavaFX Application Entry Point
 * 
 * Simple and clean - just loads the landing page
 */
public class RideSecureApp extends Application {
    
    private static Stage primaryStage;
    
    @Override
    public void start(Stage stage) throws Exception {
        primaryStage = stage;
        
        // Load landing page
        Parent root = FXMLLoader.load(getClass().getResource("/fxml/Landing.fxml"));
        
        Scene scene = new Scene(root, 1200, 800);
        scene.getStylesheets().add(getClass().getResource("/css/landing.css").toExternalForm());
        
        stage.setTitle("RideSecure - Helmet Violation Detection");
        stage.setScene(scene);
        stage.setResizable(false);
        stage.show();
    }
    
    public static Stage getPrimaryStage() {
        return primaryStage;
    }
    
    public static void main(String[] args) {
        launch(args);
    }
}
