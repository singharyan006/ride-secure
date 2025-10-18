package com.ridesecure.service;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.util.concurrent.CompletableFuture;

public class DetectionService {
    private final String pythonScript;
    private Process currentProcess;

    public DetectionService() {
        // Path to the Python script relative to project root
        this.pythonScript = new File("../python/src/detect_helmets.py").getAbsolutePath();
    }

    public CompletableFuture<Boolean> detectHelmet(String imagePath) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                ProcessBuilder processBuilder = new ProcessBuilder("python", pythonScript, imagePath);
                processBuilder.redirectErrorStream(true);
                
                currentProcess = processBuilder.start();
                
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(currentProcess.getInputStream()))) {
                    String line;
                    StringBuilder output = new StringBuilder();
                    
                    while ((line = reader.readLine()) != null) {
                        output.append(line).append("\n");
                    }
                    
                    int exitCode = currentProcess.waitFor();
                    System.out.println("Python script output: " + output.toString());
                    
                    // Parse the output to determine if helmet was detected
                    return output.toString().contains("Helmet detected");
                }
            } catch (Exception e) {
                e.printStackTrace();
                return false;
            }
        });
    }

    public void stopDetection() {
        if (currentProcess != null && currentProcess.isAlive()) {
            currentProcess.destroy();
        }
    }
}