package com.ridesecure;

import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.stage.Stage;

public class RideSecureFXApp extends Application {
    
    private static Stage primaryStage;
    
    @Override
    public void start(Stage stage) throws Exception {
        primaryStage = stage;
        
        // Start with the landing page
        showLandingPage();
        
        primaryStage.setTitle("RideSecure - Smart Helmet Detection System");
        primaryStage.setMinWidth(900);
        primaryStage.setMinHeight(600);
        primaryStage.show();
    }
    
    public static void showLandingPage() throws Exception {
        FXMLLoader loader = new FXMLLoader(RideSecureFXApp.class.getResource("/fxml/LandingPage.fxml"));
        Parent root = loader.load();
        
        Scene scene = new Scene(root, 1000, 700);
        scene.getStylesheets().add(RideSecureFXApp.class.getResource("/css/landing.css").toExternalForm());
        
        primaryStage.setScene(scene);
    }
    
    public static void showMainApplication() throws Exception {
        FXMLLoader loader = new FXMLLoader(RideSecureFXApp.class.getResource("/fxml/RideSecureMain.fxml"));
        Parent root = loader.load();
        
        Scene scene = new Scene(root, 1200, 800);
        scene.getStylesheets().add(RideSecureFXApp.class.getResource("/css/styles.css").toExternalForm());
        
        primaryStage.setScene(scene);
        primaryStage.centerOnScreen();
    }
    
    public static Stage getPrimaryStage() {
        return primaryStage;
    }
    
    public static void main(String[] args) {
        launch(args);
    }
}