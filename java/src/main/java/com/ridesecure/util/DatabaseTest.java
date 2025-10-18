package com.ridesecure.util;

import com.ridesecure.config.EnvConfig;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseTest {
    public static void main(String[] args) {
        System.out.println("Testing Supabase Database Connection...");
        EnvConfig.printConfig();

        try {
            // Load PostgreSQL JDBC driver
            Class.forName("org.postgresql.Driver");
            System.out.println("✓ PostgreSQL JDBC driver loaded successfully");

            // Get connection details
            String url = EnvConfig.getDatabaseUrl();
            String user = EnvConfig.getDatabaseUser();
            String password = EnvConfig.getDatabasePassword();

            System.out.println("\nTrying to connect to:");
            System.out.println("URL: " + url);
            System.out.println("User: " + user);

            // Test connection
            try (Connection conn = DriverManager.getConnection(url, user, password)) {
                System.out.println("\n✓ Successfully connected to Supabase!");
                System.out.println("Database product: " + conn.getMetaData().getDatabaseProductName());
                System.out.println("Database version: " + conn.getMetaData().getDatabaseProductVersion());
            }

        } catch (ClassNotFoundException e) {
            System.err.println("\n❌ PostgreSQL JDBC driver not found!");
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        } catch (SQLException e) {
            System.err.println("\n❌ Database connection failed!");
            System.err.println("Error: " + e.getMessage());
            System.err.println("SQLState: " + e.getSQLState());
            System.exit(1);
        }
    }
}