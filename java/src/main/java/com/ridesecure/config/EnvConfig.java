package com.ridesecure.config;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

/**
 * Environment configuration reader for RideSecure
 * Reads configuration from .env file
 */
public class EnvConfig {
    
    private static final Map<String, String> envVars = new HashMap<>();
    private static boolean loaded = false;
    
    static {
        loadEnvFile();
    }
    
    private static void loadEnvFile() {
        if (loaded) return;
        
        // Try different locations for .env file
        String[] envPaths = {".env", "../.env", "../../.env"};
        boolean foundEnv = false;
        
        for (String envPath : envPaths) {
            try (BufferedReader reader = new BufferedReader(new FileReader(envPath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                
                // Skip empty lines and comments
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                
                // Parse key=value pairs
                int equalIndex = line.indexOf('=');
                if (equalIndex > 0) {
                    String key = line.substring(0, equalIndex).trim();
                    String value = line.substring(equalIndex + 1).trim();
                    envVars.put(key, value);
                }
            }
            
                loaded = true;
                foundEnv = true;
                System.out.println("✅ Environment configuration loaded from: " + envPath);
                break;
                
            } catch (IOException e) {
                // Continue to next path
            }
        }
        
        if (!foundEnv) {
            System.err.println("❌ Warning: Could not find .env file in any location");
            System.err.println("   Searched: .env, ../.env, ../../.env");
            System.err.println("   Using default configuration values");
        }
    }
    
    /**
     * Get environment variable value
     */
    public static String get(String key) {
        return envVars.get(key);
    }
    
    /**
     * Get environment variable with default value
     */
    public static String get(String key, String defaultValue) {
        return envVars.getOrDefault(key, defaultValue);
    }
    
    /**
     * Get database connection URL
     */
    public static String getDatabaseUrl() {
        String host = get("DB_HOST");
        String port = get("DB_PORT", "5432");
        String dbName = get("DB_NAME", "postgres");
        
        if (host == null) {
            throw new RuntimeException("DB_HOST not configured in .env file");
        }
        
        return String.format("jdbc:postgresql://%s:%s/%s", host, port, dbName);
    }
    
    /**
     * Get database username
     */
    public static String getDatabaseUser() {
        return get("DB_USER", "postgres");
    }
    
    /**
     * Get database password
     */
    public static String getDatabasePassword() {
        String password = get("DB_PASSWORD");
        if (password == null || password.equals("YOUR_DATABASE_PASSWORD_HERE")) {
            throw new RuntimeException("Database password not configured in .env file. Please update DB_PASSWORD.");
        }
        return password;
    }
    
    /**
     * Get Supabase URL
     */
    public static String getSupabaseUrl() {
        return get("SUPABASE_URL");
    }
    
    /**
     * Get Supabase API Key
     */
    public static String getSupabaseKey() {
        return get("SUPABASE_ANON_KEY");
    }
    
    /**
     * Check if debug mode is enabled
     */
    public static boolean isDebugMode() {
        return "true".equalsIgnoreCase(get("DEBUG", "false"));
    }
    
    /**
     * Print all loaded configuration (for debugging)
     */
    public static void printConfig() {
        System.out.println("📋 RideSecure Configuration:");
        System.out.println("   App Name: " + get("APP_NAME", "RideSecure"));
        System.out.println("   Version: " + get("APP_VERSION", "1.0.0"));
        System.out.println("   Debug Mode: " + isDebugMode());
        System.out.println("   Supabase URL: " + getSupabaseUrl());
        System.out.println("   Database Host: " + get("DB_HOST"));
        System.out.println("   Database User: " + getDatabaseUser());
        System.out.println("   Database Password: " + (get("DB_PASSWORD") != null ? "***configured***" : "❌ NOT SET"));
    }
}