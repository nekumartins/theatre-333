-- Theatre Booking System - MySQL Setup Script
-- Run this in MySQL Workbench to create the database

-- Create database
CREATE DATABASE IF NOT EXISTS theatre_booking
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use the database
USE theatre_booking;

-- Grant privileges (adjust username if needed)
-- GRANT ALL PRIVILEGES ON theatre_booking.* TO 'root'@'localhost';
-- FLUSH PRIVILEGES;

-- The tables will be created automatically when you start the FastAPI app
-- Or you can run: python init_db.py

SELECT 'Database theatre_booking created successfully!' AS Status;
