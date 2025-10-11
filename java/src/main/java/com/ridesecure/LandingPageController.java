package com.ridesecure;

import javafx.fxml.FXML;
import javafx.fxml.Initializable;
import javafx.scene.control.*;
import javafx.scene.layout.StackPane;
import javafx.scene.layout.VBox;
import javafx.animation.FadeTransition;
import javafx.util.Duration;

import java.net.URL;
import java.util.ResourceBundle;

public class LandingPageController implements Initializable {
    
    // Main UI Elements
    @FXML private Button loginButton;
    @FXML private Button signupButton;
    @FXML private Button demoButton;
    
    // Auth Overlay
    @FXML private StackPane authOverlay;
    @FXML private VBox loginForm;
    @FXML private VBox signupForm;
    
    // Login Form Fields
    @FXML private TextField loginUsername;
    @FXML private PasswordField loginPassword;
    @FXML private Button submitLoginButton;
    
    // Signup Form Fields
    @FXML private TextField signupFullName;
    @FXML private TextField signupEmail;
    @FXML private TextField signupUsername;
    @FXML private PasswordField signupPassword;
    @FXML private PasswordField signupConfirmPassword;
    @FXML private Button submitSignupButton;
    
    @Override
    public void initialize(URL url, ResourceBundle rb) {
        // Add fade-in animation when landing page loads
        fadeInAnimation();
    }
    
    private void fadeInAnimation() {
        authOverlay.setOpacity(0);
        FadeTransition fadeIn = new FadeTransition(Duration.millis(800), authOverlay.getParent());
        fadeIn.setFromValue(0.0);
        fadeIn.setToValue(1.0);
        fadeIn.play();
    }
    
    @FXML
    private void showLoginForm() {
        showAuthOverlay();
        showForm(loginForm);
        hideForm(signupForm);
        loginUsername.requestFocus();
    }
    
    @FXML
    private void showSignupForm() {
        showAuthOverlay();
        showForm(signupForm);
        hideForm(loginForm);
        signupFullName.requestFocus();
    }
    
    @FXML
    private void switchToLogin() {
        showForm(loginForm);
        hideForm(signupForm);
        clearSignupFields();
        loginUsername.requestFocus();
    }
    
    @FXML
    private void switchToSignup() {
        showForm(signupForm);
        hideForm(loginForm);
        clearLoginFields();
        signupFullName.requestFocus();
    }
    
    @FXML
    private void hideAuthForms() {
        hideAuthOverlay();
        clearLoginFields();
        clearSignupFields();
    }
    
    @FXML
    private void handleLogin() {
        String username = loginUsername.getText().trim();
        String password = loginPassword.getText();
        
        if (username.isEmpty() || password.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "Login Error", "Please fill in all fields.");
            return;
        }
        
        // Simulate authentication (in real app, this would call an API)
        if (authenticateUser(username, password)) {
            launchMainApplication();
        } else {
            showAlert(Alert.AlertType.ERROR, "Login Failed", "Invalid username or password.");
            loginPassword.clear();
            loginPassword.requestFocus();
        }
    }
    
    @FXML
    private void handleSignup() {
        String fullName = signupFullName.getText().trim();
        String email = signupEmail.getText().trim();
        String username = signupUsername.getText().trim();
        String password = signupPassword.getText();
        String confirmPassword = signupConfirmPassword.getText();
        
        // Validation
        if (fullName.isEmpty() || email.isEmpty() || username.isEmpty() || 
            password.isEmpty() || confirmPassword.isEmpty()) {
            showAlert(Alert.AlertType.WARNING, "Signup Error", "Please fill in all fields.");
            return;
        }
        
        if (!isValidEmail(email)) {
            showAlert(Alert.AlertType.WARNING, "Invalid Email", "Please enter a valid email address.");
            signupEmail.requestFocus();
            return;
        }
        
        if (!password.equals(confirmPassword)) {
            showAlert(Alert.AlertType.WARNING, "Password Mismatch", "Passwords do not match.");
            signupConfirmPassword.clear();
            signupConfirmPassword.requestFocus();
            return;
        }
        
        if (password.length() < 6) {
            showAlert(Alert.AlertType.WARNING, "Weak Password", "Password must be at least 6 characters long.");
            signupPassword.requestFocus();
            return;
        }
        
        // Simulate user registration (in real app, this would call an API)
        if (registerUser(fullName, email, username, password)) {
            showAlert(Alert.AlertType.INFORMATION, "Account Created", 
                     "Welcome to RideSecure, " + fullName + "! Your account has been created successfully.");
            launchMainApplication();
        } else {
            showAlert(Alert.AlertType.ERROR, "Signup Failed", "Username or email already exists.");
        }
    }
    
    @FXML
    private void launchDemo() {
        Alert confirmation = new Alert(Alert.AlertType.CONFIRMATION);
        confirmation.setTitle("Demo Mode");
        confirmation.setHeaderText("Launch RideSecure Demo");
        confirmation.setContentText("Demo mode provides full access to all features with sample data. Continue?");
        
        confirmation.showAndWait().ifPresent(response -> {
            if (response == ButtonType.OK) {
                launchMainApplication();
            }
        });
    }
    
    private void launchMainApplication() {
        try {
            RideSecureFXApp.showMainApplication();
        } catch (Exception e) {
            showAlert(Alert.AlertType.ERROR, "Application Error", 
                     "Failed to launch main application: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private void showAuthOverlay() {
        authOverlay.setVisible(true);
        FadeTransition fadeIn = new FadeTransition(Duration.millis(300), authOverlay);
        fadeIn.setFromValue(0.0);
        fadeIn.setToValue(1.0);
        fadeIn.play();
    }
    
    private void hideAuthOverlay() {
        FadeTransition fadeOut = new FadeTransition(Duration.millis(300), authOverlay);
        fadeOut.setFromValue(1.0);
        fadeOut.setToValue(0.0);
        fadeOut.setOnFinished(e -> authOverlay.setVisible(false));
        fadeOut.play();
    }
    
    private void showForm(VBox form) {
        form.setVisible(true);
        FadeTransition fadeIn = new FadeTransition(Duration.millis(200), form);
        fadeIn.setFromValue(0.0);
        fadeIn.setToValue(1.0);
        fadeIn.play();
    }
    
    private void hideForm(VBox form) {
        FadeTransition fadeOut = new FadeTransition(Duration.millis(200), form);
        fadeOut.setFromValue(1.0);
        fadeOut.setToValue(0.0);
        fadeOut.setOnFinished(e -> form.setVisible(false));
        fadeOut.play();
    }
    
    private void clearLoginFields() {
        loginUsername.clear();
        loginPassword.clear();
    }
    
    private void clearSignupFields() {
        signupFullName.clear();
        signupEmail.clear();
        signupUsername.clear();
        signupPassword.clear();
        signupConfirmPassword.clear();
    }
    
    private boolean authenticateUser(String username, String password) {
        // Simulate authentication - in real app, this would call your auth service
        // For demo purposes, accept common test credentials
        return (username.equalsIgnoreCase("admin") && password.equals("admin")) ||
               (username.equalsIgnoreCase("demo") && password.equals("demo")) ||
               (username.contains("@") && password.length() >= 6); // Basic email + password check
    }
    
    private boolean registerUser(String fullName, String email, String username, String password) {
        // Simulate user registration - in real app, this would call your registration API
        // For demo purposes, accept all valid registrations except some reserved usernames
        String[] reservedNames = {"admin", "root", "system", "test"};
        for (String reserved : reservedNames) {
            if (username.equalsIgnoreCase(reserved)) {
                return false;
            }
        }
        return true;
    }
    
    private boolean isValidEmail(String email) {
        return email.contains("@") && email.contains(".") && email.length() > 5;
    }
    
    private void showAlert(Alert.AlertType type, String title, String message) {
        Alert alert = new Alert(type);
        alert.setTitle(title);
        alert.setHeaderText(null);
        alert.setContentText(message);
        alert.showAndWait();
    }
}