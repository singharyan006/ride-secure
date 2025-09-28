package com.ridesecure;

import com.ridesecure.model.Violation;
import com.ridesecure.service.DatabaseService;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import javax.swing.table.*;
import java.util.List;
import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Simplified RideSecure Desktop Application using Swing
 * 
 * This version works without external dependencies like JavaFX or Maven.
 * Provides basic UI for video loading and detection simulation.
 */
public class RideSecureSwingApp extends JFrame {
    
    private static final String APP_TITLE = "RideSecure - Helmet Detection System";
    
    // UI Components
    private JPanel videoPanel;
    private JLabel videoLabel;
    private JButton openVideoButton;
    private JButton playButton;
    private JButton pauseButton;
    private JButton stopButton;
    private JSlider timeSlider;
    private JLabel timeLabel;
    
    // Detection Controls
    private JButton startDetectionButton;
    private JButton stopDetectionButton;
    private JCheckBox realTimeCheckbox;
    private JProgressBar progressBar;
    private JLabel statusLabel;
    
    // Results
    private JTable violationsTable;
    private DefaultTableModel tableModel;
    private JLabel totalViolationsLabel;
    private JLabel accuracyLabel;
    private JLabel speedLabel;
    
    // Data
    private File currentVideoFile;
    private boolean isDetectionRunning = false;
    private javax.swing.Timer detectionTimer;
    private DatabaseService databaseService;
    
    public RideSecureSwingApp() {
        super(APP_TITLE);
        
        // Initialize database service
        try {
            databaseService = DatabaseService.getInstance();
            System.out.println("Database service initialized successfully");
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, 
                "Failed to initialize database: " + e.getMessage(), 
                "Database Error", 
                JOptionPane.ERROR_MESSAGE);
            System.exit(1);
        }
        
        initializeComponents();
        setupLayout();
        setupEventHandlers();
        loadExistingViolations();
        
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(1200, 800);
        setLocationRelativeTo(null);
        
        updateStatus("Ready - Load a video to begin");
    }
    
    private void initializeComponents() {
        // Video components
        videoPanel = new JPanel();
        videoPanel.setBackground(Color.BLACK);
        videoPanel.setBorder(BorderFactory.createTitledBorder("Video Display"));
        videoPanel.setPreferredSize(new Dimension(640, 480));
        
        videoLabel = new JLabel("No video loaded", SwingConstants.CENTER);
        videoLabel.setForeground(Color.WHITE);
        videoLabel.setFont(new Font("Arial", Font.BOLD, 16));
        
        // Video controls
        openVideoButton = new JButton("📂 Open Video");
        playButton = new JButton("▶ Play");
        pauseButton = new JButton("⏸ Pause");
        stopButton = new JButton("⏹ Stop");
        timeSlider = new JSlider(0, 100, 0);
        timeLabel = new JLabel("00:00 / 00:00");
        
        // Initially disable video controls
        playButton.setEnabled(false);
        pauseButton.setEnabled(false);
        stopButton.setEnabled(false);
        timeSlider.setEnabled(false);
        
        // Detection controls
        startDetectionButton = new JButton("🔍 Start Detection");
        startDetectionButton.setBackground(new Color(76, 175, 80));
        startDetectionButton.setForeground(Color.WHITE);
        startDetectionButton.setEnabled(false);
        
        stopDetectionButton = new JButton("⏹ Stop Detection");
        stopDetectionButton.setBackground(new Color(244, 67, 54));
        stopDetectionButton.setForeground(Color.WHITE);
        stopDetectionButton.setEnabled(false);
        
        realTimeCheckbox = new JCheckBox("Real-time Detection");
        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);
        statusLabel = new JLabel("Ready");
        
        // Results table
        String[] columnNames = {"ID", "Time", "License Plate", "Confidence", "Status"};
        tableModel = new DefaultTableModel(columnNames, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        violationsTable = new JTable(tableModel);
        violationsTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        
        // Statistics labels
        totalViolationsLabel = new JLabel("0");
        accuracyLabel = new JLabel("--");
        speedLabel = new JLabel("--");
    }
    
    private void setupLayout() {
        setLayout(new BorderLayout());
        
        // Menu bar
        JMenuBar menuBar = new JMenuBar();
        JMenu fileMenu = new JMenu("File");
        JMenuItem openVideoItem = new JMenuItem("Open Video...");
        JMenuItem exitItem = new JMenuItem("Exit");
        
        openVideoItem.addActionListener(e -> openVideoFile());
        exitItem.addActionListener(e -> System.exit(0));
        
        fileMenu.add(openVideoItem);
        fileMenu.addSeparator();
        fileMenu.add(exitItem);
        menuBar.add(fileMenu);
        
        JMenu helpMenu = new JMenu("Help");
        JMenuItem aboutItem = new JMenuItem("About");
        aboutItem.addActionListener(e -> showAbout());
        helpMenu.add(aboutItem);
        menuBar.add(helpMenu);
        
        setJMenuBar(menuBar);
        
        // Main content
        JSplitPane mainSplitPane = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
        
        // Left panel - Video and controls
        JPanel leftPanel = new JPanel(new BorderLayout());
        leftPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 5));
        
        // Video area
        videoPanel.setLayout(new BorderLayout());
        videoPanel.add(videoLabel, BorderLayout.CENTER);
        leftPanel.add(videoPanel, BorderLayout.CENTER);
        
        // Video controls
        JPanel videoControlsPanel = new JPanel(new FlowLayout());
        videoControlsPanel.add(openVideoButton);
        videoControlsPanel.add(new JSeparator(SwingConstants.VERTICAL));
        videoControlsPanel.add(playButton);
        videoControlsPanel.add(pauseButton);
        videoControlsPanel.add(stopButton);
        
        JPanel timePanel = new JPanel(new BorderLayout());
        timePanel.add(timeSlider, BorderLayout.CENTER);
        timePanel.add(timeLabel, BorderLayout.EAST);
        
        JPanel controlsContainer = new JPanel(new BorderLayout());
        controlsContainer.add(videoControlsPanel, BorderLayout.NORTH);
        controlsContainer.add(timePanel, BorderLayout.SOUTH);
        
        leftPanel.add(controlsContainer, BorderLayout.SOUTH);
        
        // Detection controls
        JPanel detectionPanel = new JPanel(new GridBagLayout());
        detectionPanel.setBorder(BorderFactory.createTitledBorder("Detection Controls"));
        
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        
        gbc.gridx = 0; gbc.gridy = 0;
        detectionPanel.add(startDetectionButton, gbc);
        gbc.gridx = 1;
        detectionPanel.add(stopDetectionButton, gbc);
        gbc.gridx = 2;
        detectionPanel.add(realTimeCheckbox, gbc);
        
        gbc.gridx = 0; gbc.gridy = 1; gbc.gridwidth = 3; gbc.fill = GridBagConstraints.HORIZONTAL;
        detectionPanel.add(progressBar, gbc);
        
        gbc.gridy = 2;
        detectionPanel.add(statusLabel, gbc);
        
        JPanel leftContainer = new JPanel(new BorderLayout());
        leftContainer.add(leftPanel, BorderLayout.CENTER);
        leftContainer.add(detectionPanel, BorderLayout.SOUTH);
        
        // Right panel - Results and statistics
        JPanel rightPanel = new JPanel(new BorderLayout());
        rightPanel.setBorder(BorderFactory.createEmptyBorder(10, 5, 10, 10));
        
        // Statistics panel
        JPanel statsPanel = new JPanel(new GridBagLayout());
        statsPanel.setBorder(BorderFactory.createTitledBorder("Detection Statistics"));
        
        gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.anchor = GridBagConstraints.WEST;
        
        gbc.gridx = 0; gbc.gridy = 0;
        statsPanel.add(new JLabel("Total Violations:"), gbc);
        gbc.gridx = 1;
        statsPanel.add(totalViolationsLabel, gbc);
        
        gbc.gridx = 0; gbc.gridy = 1;
        statsPanel.add(new JLabel("Detection Accuracy:"), gbc);
        gbc.gridx = 1;
        statsPanel.add(accuracyLabel, gbc);
        
        gbc.gridx = 0; gbc.gridy = 2;
        statsPanel.add(new JLabel("Processing Speed:"), gbc);
        gbc.gridx = 1;
        statsPanel.add(speedLabel, gbc);
        
        rightPanel.add(statsPanel, BorderLayout.NORTH);
        
        // Violations table
        JScrollPane tableScrollPane = new JScrollPane(violationsTable);
        tableScrollPane.setBorder(BorderFactory.createTitledBorder("Detected Violations"));
        rightPanel.add(tableScrollPane, BorderLayout.CENTER);
        
        // Action buttons
        JPanel actionsPanel = new JPanel(new FlowLayout());
        JButton exportButton = new JButton("📊 Export Report");
        JButton clearButton = new JButton("🗑️ Clear Results");
        JButton settingsButton = new JButton("⚙️ Settings");
        
        exportButton.addActionListener(e -> exportReport());
        clearButton.addActionListener(e -> clearResults());
        settingsButton.addActionListener(e -> showSettings());
        
        actionsPanel.add(exportButton);
        actionsPanel.add(clearButton);
        actionsPanel.add(settingsButton);
        
        rightPanel.add(actionsPanel, BorderLayout.SOUTH);
        
        // Add panels to split pane
        mainSplitPane.setLeftComponent(leftContainer);
        mainSplitPane.setRightComponent(rightPanel);
        mainSplitPane.setDividerLocation(650);
        
        add(mainSplitPane, BorderLayout.CENTER);
        
        // Status bar
        JPanel statusBar = new JPanel(new BorderLayout());
        statusBar.setBorder(BorderFactory.createLoweredBevelBorder());
        statusBar.add(new JLabel(" Ready"), BorderLayout.WEST);
        statusBar.add(new JLabel("RideSecure v1.0.0 "), BorderLayout.EAST);
        
        add(statusBar, BorderLayout.SOUTH);
    }
    
    private void setupEventHandlers() {
        openVideoButton.addActionListener(e -> openVideoFile());
        playButton.addActionListener(e -> playVideo());
        pauseButton.addActionListener(e -> pauseVideo());
        stopButton.addActionListener(e -> stopVideo());
        
        startDetectionButton.addActionListener(e -> startDetection());
        stopDetectionButton.addActionListener(e -> stopDetection());
        
        timeSlider.addChangeListener(e -> {
            if (!timeSlider.getValueIsAdjusting()) {
                updateTimeLabel();
            }
        });
    }
    
    private void openVideoFile() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setFileFilter(new javax.swing.filechooser.FileFilter() {
            @Override
            public boolean accept(File file) {
                if (file.isDirectory()) return true;
                String name = file.getName().toLowerCase();
                return name.endsWith(".mp4") || name.endsWith(".avi") || 
                       name.endsWith(".mov") || name.endsWith(".mkv");
            }
            
            @Override
            public String getDescription() {
                return "Video Files (*.mp4, *.avi, *.mov, *.mkv)";
            }
        });
        
        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            currentVideoFile = fileChooser.getSelectedFile();
            loadVideo();
        }
    }
    
    private void loadVideo() {
        if (currentVideoFile != null) {
            videoLabel.setText("Video: " + currentVideoFile.getName());
            playButton.setEnabled(true);
            pauseButton.setEnabled(true);
            stopButton.setEnabled(true);
            timeSlider.setEnabled(true);
            startDetectionButton.setEnabled(true);
            
            updateStatus("Video loaded: " + currentVideoFile.getName());
        }
    }
    
    private void playVideo() {
        updateStatus("Playing video...");
        // TODO: Implement actual video playback
    }
    
    private void pauseVideo() {
        updateStatus("Video paused");
        // TODO: Implement video pause
    }
    
    private void stopVideo() {
        timeSlider.setValue(0);
        updateStatus("Video stopped");
        // TODO: Implement video stop
    }
    
    private void startDetection() {
        if (currentVideoFile == null) {
            JOptionPane.showMessageDialog(this, "Please load a video file first", 
                                        "No Video", JOptionPane.WARNING_MESSAGE);
            return;
        }
        
        isDetectionRunning = true;
        startDetectionButton.setEnabled(false);
        stopDetectionButton.setEnabled(true);
        progressBar.setValue(0);
        
        updateStatus("Starting helmet detection...");
        
        // Simulate detection process
        detectionTimer = new javax.swing.Timer(100, new ActionListener() {
            int progress = 0;
            int violationCount = 0;
            
            @Override
            public void actionPerformed(ActionEvent e) {
                progress++;
                progressBar.setValue(progress);
                
                updateStatus("Processing frame " + progress + "/100");
                
                // Simulate finding violations occasionally
                if (progress % 20 == 0 && progress > 0) {
                    addMockViolation(++violationCount);
                }
                
                if (progress >= 100) {
                    detectionTimer.stop();
                    finishDetection();
                }
            }
        });
        
        detectionTimer.start();
    }
    
    private void stopDetection() {
        if (detectionTimer != null && detectionTimer.isRunning()) {
            detectionTimer.stop();
        }
        finishDetection();
        updateStatus("Detection stopped by user");
    }
    
    private void finishDetection() {
        isDetectionRunning = false;
        startDetectionButton.setEnabled(true);
        stopDetectionButton.setEnabled(false);
        progressBar.setValue(100);
        
        updateStatus("Detection completed");
        updateStatistics();
    }
    
    private void addMockViolation(int id) {
        // Create a real violation object
        Violation violation = new Violation();
        violation.setTimestamp(LocalDateTime.now());
        violation.setVideoSource(currentVideoFile != null ? currentVideoFile.getName() : "sample_video.mp4");
        violation.setFrameNumber(id * 125 + (int)(Math.random() * 100)); // Mock frame number
        
        double detectionConfidence = 70 + Math.random() * 30;
        violation.setDetectionConfidence(detectionConfidence / 100.0); // Store as decimal
        
        String licensePlate = "MH" + String.format("%02d", (int)(Math.random() * 99)) + 
                             "AB" + String.format("%04d", (int)(Math.random() * 9999));
        violation.setLicensePlate(licensePlate);
        violation.setPlateConfidence(0.8 + Math.random() * 0.2); // Mock plate confidence
        
        violation.setViolationType("NO_HELMET");
        violation.setStatus("DETECTED");
        violation.setLocationInfo("Traffic Junction " + (int)(Math.random() * 10 + 1));
        
        // Save to database
        if (databaseService.saveViolation(violation)) {
            // Add to table display
            String timestamp = violation.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
            String confidence = String.format("%.1f%%", detectionConfidence);
            
            Object[] rowData = {violation.getId(), timestamp, licensePlate, confidence, violation.getStatus()};
            tableModel.addRow(rowData);
            
            // Scroll to latest row
            int lastRow = violationsTable.getRowCount() - 1;
            violationsTable.scrollRectToVisible(violationsTable.getCellRect(lastRow, 0, true));
            
            System.out.println("Violation saved: ID=" + violation.getId() + ", Plate=" + licensePlate);
        } else {
            System.err.println("Failed to save violation to database");
        }
    }
    
    private void updateStatistics() {
        if (databaseService != null) {
            DatabaseService.ViolationStats stats = databaseService.getViolationStats();
            totalViolationsLabel.setText(String.valueOf(stats.getTotalViolations()));
            accuracyLabel.setText(String.format("%.1f%%", stats.getAverageConfidence() * 100));
        } else {
            totalViolationsLabel.setText(String.valueOf(tableModel.getRowCount()));
            accuracyLabel.setText("85.7%"); // Mock value
        }
        speedLabel.setText("12.5 FPS"); // Mock value
    }
    
    private void loadExistingViolations() {
        if (databaseService == null) return;
        
        try {
            List<Violation> violations = databaseService.getAllViolations();
            tableModel.setRowCount(0); // Clear existing data
            
            for (Violation violation : violations) {
                String timestamp = violation.getTimestamp().format(DateTimeFormatter.ofPattern("HH:mm:ss"));
                String confidence = String.format("%.1f%%", violation.getDetectionConfidence() * 100);
                
                Object[] rowData = {
                    violation.getId(), 
                    timestamp, 
                    violation.getLicensePlate(), 
                    confidence, 
                    violation.getStatus()
                };
                tableModel.addRow(rowData);
            }
            
            updateStatistics();
            System.out.println("Loaded " + violations.size() + " existing violations from database");
            
        } catch (Exception e) {
            System.err.println("Failed to load existing violations: " + e.getMessage());
        }
    }
    
    private void updateTimeLabel() {
        int value = timeSlider.getValue();
        int minutes = value / 60;
        int seconds = value % 60;
        timeLabel.setText(String.format("%02d:%02d / 05:00", minutes, seconds));
    }
    
    private void updateStatus(String status) {
        statusLabel.setText(status);
    }
    
    private void exportReport() {
        JOptionPane.showMessageDialog(this, "Export functionality will be implemented", 
                                    "Export Report", JOptionPane.INFORMATION_MESSAGE);
    }
    
    private void clearResults() {
        String[] options = {"Clear Table Only", "Clear Table & Database", "Cancel"};
        int option = JOptionPane.showOptionDialog(this,
            "Choose what to clear:",
            "Clear Results",
            JOptionPane.YES_NO_CANCEL_OPTION,
            JOptionPane.QUESTION_MESSAGE,
            null,
            options,
            options[0]);
            
        if (option == 0) { // Clear table only
            tableModel.setRowCount(0);
            updateStatus("Table cleared");
        } else if (option == 1) { // Clear table and database
            int confirm = JOptionPane.showConfirmDialog(this,
                "This will permanently delete ALL violations from the database!\nAre you sure?",
                "Confirm Database Clear",
                JOptionPane.YES_NO_OPTION,
                JOptionPane.WARNING_MESSAGE);
                
            if (confirm == JOptionPane.YES_OPTION) {
                // Clear database (we'll implement this method)
                clearDatabase();
                tableModel.setRowCount(0);
                updateStatistics();
                updateStatus("Database and table cleared");
            }
        }
    }
    
    private void clearDatabase() {
        // For now, we'll delete all violations one by one
        // In a real implementation, you might want a more efficient bulk delete
        try {
            List<Violation> violations = databaseService.getAllViolations();
            for (Violation violation : violations) {
                databaseService.deleteViolation(violation.getId());
            }
            System.out.println("Cleared " + violations.size() + " violations from database");
        } catch (Exception e) {
            System.err.println("Failed to clear database: " + e.getMessage());
            JOptionPane.showMessageDialog(this, 
                "Failed to clear database: " + e.getMessage(), 
                "Database Error", 
                JOptionPane.ERROR_MESSAGE);
        }
    }
    
    private void showSettings() {
        JOptionPane.showMessageDialog(this, "Settings dialog will be implemented", 
                                    "Settings", JOptionPane.INFORMATION_MESSAGE);
    }
    
    private void showAbout() {
        String aboutText = """
            RideSecure - Helmet Detection System
            Version 1.0.0
            
            A hybrid Java + Python application for automated
            motorcycle helmet compliance monitoring and
            license plate recognition.
            
            Built with Java Swing for maximum compatibility.
            """;
            
        JOptionPane.showMessageDialog(this, aboutText, "About RideSecure", 
                                    JOptionPane.INFORMATION_MESSAGE);
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                // Use default look and feel for compatibility
                new RideSecureSwingApp().setVisible(true);
                System.out.println("RideSecure Desktop Application started successfully!");
            }
        });
    }
}