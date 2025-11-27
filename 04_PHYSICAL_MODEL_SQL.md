# Online Theatre Booking System - Physical Model & SQL Implementation

## MySQL Database Implementation Guide

---

## 1. Data Type Recommendations (MySQL Standards)

### 1.1 Numeric Types
- **Primary Keys**: `INT UNSIGNED AUTO_INCREMENT` (supports up to 4.2 billion records)
- **Prices**: `DECIMAL(10,2)` (10 digits total, 2 decimal places)
- **Counters/Quantities**: `INT UNSIGNED`
- **Boolean Flags**: `TINYINT(1)` or `BOOLEAN`

### 1.2 String Types
- **Short Strings** (names, codes): `VARCHAR(n)`
- **Long Text** (descriptions): `TEXT`
- **Fixed-Length** (status codes): `VARCHAR(20)`
- **Email**: `VARCHAR(100)`
- **URLs**: `VARCHAR(255)`
- **JSON Data**: `JSON` (for audit log old/new values)

### 1.3 Date/Time Types
- **Date Only**: `DATE`
- **Time Only**: `TIME`
- **Date and Time**: `DATETIME` (preferred) or `TIMESTAMP`
- **Auto-timestamps**: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

### 1.4 Character Set
- Use `utf8mb4` for full Unicode support (including emojis)
- Collation: `utf8mb4_unicode_ci`

---

## 2. SQL CREATE TABLE Statements

### 2.1 Create Database
```sql
-- Create database with UTF-8 support
CREATE DATABASE IF NOT EXISTS theatre_booking
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE theatre_booking;
```

---

### 2.2 ROLE Table (RBAC Support)
```sql
CREATE TABLE role (
    role_id INT UNSIGNED AUTO_INCREMENT,
    role_name VARCHAR(50) NOT NULL,
    description TEXT,
    can_manage_shows BOOLEAN DEFAULT FALSE,
    can_manage_venues BOOLEAN DEFAULT FALSE,
    can_manage_performances BOOLEAN DEFAULT FALSE,
    can_manage_bookings BOOLEAN DEFAULT FALSE,
    can_view_analytics BOOLEAN DEFAULT FALSE,
    can_manage_users BOOLEAN DEFAULT FALSE,
    can_manage_pricing BOOLEAN DEFAULT FALSE,
    can_issue_refunds BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id),
    UNIQUE KEY uk_role_name (role_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default roles
INSERT INTO role (role_name, description, can_manage_shows, can_manage_venues, can_manage_performances, can_manage_bookings, can_view_analytics, can_manage_users, can_manage_pricing, can_issue_refunds) VALUES
('Admin', 'Full system administrator with all permissions', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE),
('Manager', 'Theatre manager with show and booking management', TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE),
('Staff', 'Theatre staff with limited booking access', FALSE, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, FALSE),
('Customer', 'Regular customer with no administrative access', FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE);
```

---

### 2.3 GENRE Table
```sql
CREATE TABLE genre (
    genre_id INT UNSIGNED AUTO_INCREMENT,
    genre_name VARCHAR(50) NOT NULL,
    description TEXT,
    PRIMARY KEY (genre_id),
    UNIQUE KEY uk_genre_name (genre_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.4 USER Table
```sql
CREATE TABLE user (
    user_id INT UNSIGNED AUTO_INCREMENT,
    role_id INT UNSIGNED,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    registration_date DATE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    account_status VARCHAR(20) NOT NULL DEFAULT 'Active',
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uk_email (email),
    INDEX idx_email (email),
    INDEX idx_role (role_id),
    INDEX idx_account_status (account_status),
    CONSTRAINT chk_account_status CHECK (account_status IN ('Active', 'Suspended', 'Deleted')),
    CONSTRAINT chk_email_format CHECK (email LIKE '%@%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.5 AUDIT_LOG Table (Audit Trail)
```sql
CREATE TABLE audit_log (
    log_id INT UNSIGNED AUTO_INCREMENT,
    user_id INT UNSIGNED,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT UNSIGNED,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id),
    INDEX idx_user (user_id),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_action (action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.6 SHOW Table
```sql
CREATE TABLE show_table (
    show_id INT UNSIGNED AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    genre_id INT UNSIGNED NOT NULL,
    duration_minutes INT UNSIGNED NOT NULL,
    language VARCHAR(50),
    age_rating VARCHAR(10),
    poster_url VARCHAR(255),
    producer VARCHAR(100),
    director VARCHAR(100),
    show_status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (show_id),
    INDEX idx_genre (genre_id),
    INDEX idx_show_status (show_status),
    CONSTRAINT chk_show_status CHECK (show_status IN ('Active', 'Coming Soon', 'Archived')),
    CONSTRAINT chk_duration CHECK (duration_minutes > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.7 VENUE Table
```sql
CREATE TABLE venue (
    venue_id INT UNSIGNED AUTO_INCREMENT,
    venue_name VARCHAR(100) NOT NULL,
    address_line1 VARCHAR(100) NOT NULL,
    address_line2 VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20),
    country VARCHAR(50) NOT NULL,
    total_capacity INT UNSIGNED NOT NULL,
    phone VARCHAR(20),
    facilities TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (venue_id),
    UNIQUE KEY uk_venue_city (venue_name, city),
    CONSTRAINT chk_capacity CHECK (total_capacity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.8 SEAT Table
```sql
CREATE TABLE seat (
    seat_id INT UNSIGNED AUTO_INCREMENT,
    venue_id INT UNSIGNED NOT NULL,
    row_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    section VARCHAR(50),
    seat_category VARCHAR(20) NOT NULL,
    is_accessible BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (seat_id),
    UNIQUE KEY uk_seat_location (venue_id, row_number, seat_number),
    INDEX idx_venue (venue_id),
    INDEX idx_category (seat_category),
    CONSTRAINT chk_seat_category CHECK (seat_category IN ('VIP', 'Premium', 'Standard', 'Economy', 'Balcony'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.9 SEAT_CATEGORY_PRICING Table
```sql
CREATE TABLE seat_category_pricing (
    category_id INT UNSIGNED AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    description TEXT,
    PRIMARY KEY (category_id),
    UNIQUE KEY uk_category_name (category_name),
    CONSTRAINT chk_base_price CHECK (base_price > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.10 PERFORMANCE Table
```sql
CREATE TABLE performance (
    performance_id INT UNSIGNED AUTO_INCREMENT,
    show_id INT UNSIGNED NOT NULL,
    venue_id INT UNSIGNED NOT NULL,
    performance_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    total_seats INT UNSIGNED NOT NULL,
    available_seats INT UNSIGNED NOT NULL,
    performance_status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',
    special_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (performance_id),
    INDEX idx_show (show_id),
    INDEX idx_venue (venue_id),
    INDEX idx_date (performance_date),
    INDEX idx_status (performance_status),
    INDEX idx_show_date (show_id, performance_date),
    CONSTRAINT chk_performance_status CHECK (performance_status IN ('Scheduled', 'Ongoing', 'Completed', 'Cancelled')),
    CONSTRAINT chk_seats CHECK (total_seats >= available_seats AND available_seats >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.11 PERFORMANCE_PRICING Table
```sql
CREATE TABLE performance_pricing (
    pricing_id INT UNSIGNED AUTO_INCREMENT,
    performance_id INT UNSIGNED NOT NULL,
    seat_category VARCHAR(20) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pricing_id),
    UNIQUE KEY uk_perf_category (performance_id, seat_category),
    INDEX idx_performance (performance_id),
    CONSTRAINT chk_price CHECK (price > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.12 BOOKING Table
```sql
CREATE TABLE booking (
    booking_id INT UNSIGNED AUTO_INCREMENT,
    user_id INT UNSIGNED NOT NULL,
    performance_id INT UNSIGNED NOT NULL,
    booking_reference VARCHAR(20) NOT NULL,
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    booking_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    cancellation_date TIMESTAMP NULL,
    refund_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (booking_id),
    UNIQUE KEY uk_booking_reference (booking_reference),
    INDEX idx_user (user_id),
    INDEX idx_performance (performance_id),
    INDEX idx_status (booking_status),
    INDEX idx_booking_date (booking_date),
    CONSTRAINT chk_booking_status CHECK (booking_status IN ('Pending', 'Confirmed', 'Cancelled', 'Expired')),
    CONSTRAINT chk_refund CHECK (refund_amount IS NULL OR refund_amount <= total_amount)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.13 BOOKING_DETAIL Table
```sql
CREATE TABLE booking_detail (
    booking_detail_id INT UNSIGNED AUTO_INCREMENT,
    booking_id INT UNSIGNED NOT NULL,
    seat_id INT UNSIGNED NOT NULL,
    seat_price DECIMAL(10,2) NOT NULL,
    row_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_category VARCHAR(20) NOT NULL,
    PRIMARY KEY (booking_detail_id),
    UNIQUE KEY uk_booking_seat (booking_id, seat_id),
    INDEX idx_booking (booking_id),
    INDEX idx_seat (seat_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2.14 PAYMENT Table
```sql
CREATE TABLE payment (
    payment_id INT UNSIGNED AUTO_INCREMENT,
    booking_id INT UNSIGNED NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(100),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    gateway_response TEXT,
    card_last_four VARCHAR(4),
    refund_date TIMESTAMP NULL,
    refund_transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (payment_id),
    INDEX idx_booking (booking_id),
    INDEX idx_status (payment_status),
    INDEX idx_payment_date (payment_date),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('Pending', 'Completed', 'Failed', 'Refunded')),
    CONSTRAINT chk_payment_amount CHECK (payment_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 3. Foreign Key Constraints

### Apply Foreign Keys After Table Creation

```sql
-- USER Table Foreign Keys
ALTER TABLE user
ADD CONSTRAINT fk_user_role 
    FOREIGN KEY (role_id) 
    REFERENCES role(role_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- AUDIT_LOG Table Foreign Keys
ALTER TABLE audit_log
ADD CONSTRAINT fk_audit_user 
    FOREIGN KEY (user_id) 
    REFERENCES user(user_id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;

-- SHOW Table Foreign Keys
ALTER TABLE show_table
ADD CONSTRAINT fk_show_genre 
    FOREIGN KEY (genre_id) 
    REFERENCES genre(genre_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- SEAT Table Foreign Keys
ALTER TABLE seat
ADD CONSTRAINT fk_seat_venue 
    FOREIGN KEY (venue_id) 
    REFERENCES venue(venue_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- PERFORMANCE Table Foreign Keys
ALTER TABLE performance
ADD CONSTRAINT fk_performance_show 
    FOREIGN KEY (show_id) 
    REFERENCES show_table(show_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

ALTER TABLE performance
ADD CONSTRAINT fk_performance_venue 
    FOREIGN KEY (venue_id) 
    REFERENCES venue(venue_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- PERFORMANCE_PRICING Table Foreign Keys
ALTER TABLE performance_pricing
ADD CONSTRAINT fk_pricing_performance 
    FOREIGN KEY (performance_id) 
    REFERENCES performance(performance_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- BOOKING Table Foreign Keys
ALTER TABLE booking
ADD CONSTRAINT fk_booking_user 
    FOREIGN KEY (user_id) 
    REFERENCES user(user_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

ALTER TABLE booking
ADD CONSTRAINT fk_booking_performance 
    FOREIGN KEY (performance_id) 
    REFERENCES performance(performance_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- BOOKING_DETAIL Table Foreign Keys
ALTER TABLE booking_detail
ADD CONSTRAINT fk_detail_booking 
    FOREIGN KEY (booking_id) 
    REFERENCES booking(booking_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

ALTER TABLE booking_detail
ADD CONSTRAINT fk_detail_seat 
    FOREIGN KEY (seat_id) 
    REFERENCES seat(seat_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;

-- PAYMENT Table Foreign Keys
ALTER TABLE payment
ADD CONSTRAINT fk_payment_booking 
    FOREIGN KEY (booking_id) 
    REFERENCES booking(booking_id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE;
```

---

## 4. Sample Data (INSERT Statements)

### 4.1 Insert Genres
```sql
INSERT INTO genre (genre_name, description) VALUES
('Drama', 'Serious narrative performances exploring human emotions and conflicts'),
('Comedy', 'Light-hearted performances designed to entertain and amuse'),
('Musical', 'Performances combining songs, spoken dialogue, acting, and dance'),
('Tragedy', 'Serious drama typically describing conflicts and suffering'),
('Romance', 'Performances centered on love stories and relationships');
```

---

### 4.2 Insert Users with Roles
```sql
-- Insert admin user with Admin role
INSERT INTO user (role_id, first_name, last_name, email, phone, password_hash, date_of_birth, city, country, registration_date, is_admin) VALUES
(1, 'Admin', 'User', 'admin@theatre.com', '+1234567890', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Ga', '1985-01-01', 'New York', 'USA', '2024-01-01', TRUE);

-- Insert regular users with Customer role
INSERT INTO user (role_id, first_name, last_name, email, phone, password_hash, date_of_birth, city, country, registration_date, is_admin) VALUES
(4, 'John', 'Doe', 'john.doe@email.com', '+1234567891', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Gb', '1990-05-15', 'New York', 'USA', '2024-01-10', FALSE),
(4, 'Jane', 'Smith', 'jane.smith@email.com', '+1234567892', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Gc', '1985-08-22', 'Los Angeles', 'USA', '2024-02-15', FALSE),
(4, 'Michael', 'Johnson', 'michael.j@email.com', '+1234567893', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Gd', '1992-11-30', 'Chicago', 'USA', '2024-03-20', FALSE),
(4, 'Emily', 'Brown', 'emily.brown@email.com', '+1234567894', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Ge', '1988-03-12', 'London', 'UK', '2024-04-05', FALSE);

-- Insert staff user with Staff role
INSERT INTO user (role_id, first_name, last_name, email, phone, password_hash, date_of_birth, city, country, registration_date, is_admin) VALUES
(3, 'Staff', 'Member', 'staff@theatre.com', '+1234567895', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU6O3Gf', '1990-06-15', 'New York', 'USA', '2024-01-05', FALSE);
```

---

### 4.3 Insert Sample Audit Log Entry
```sql
INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, new_values, ip_address, user_agent) VALUES
(1, 'CREATE', 'SHOW', 1, NULL, '{"title": "The Phantom of Broadway", "genre_id": 3}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
(1, 'UPDATE', 'USER', 2, '{"account_status": "Active"}', '{"account_status": "Suspended"}', '192.168.1.100', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)');
```

---

### 4.4 Insert Venues
```sql
INSERT INTO venue (venue_name, address_line1, city, postal_code, country, total_capacity, phone, facilities) VALUES
('Grand Theatre', '123 Broadway Street', 'New York', '10001', 'USA', 500, '+1-555-0100', 'Wheelchair accessible, parking available, restaurant on-site'),
('Royal Playhouse', '456 West End Avenue', 'London', 'WC2E 7RQ', 'UK', 350, '+44-20-7946-0958', 'Bar, cloakroom, accessible seating'),
('City Hall Theatre', '789 Michigan Avenue', 'Chicago', '60601', 'USA', 400, '+1-555-0200', 'VIP lounge, parking garage, accessible facilities');
```

---

### 4.5 Insert Shows
```sql
INSERT INTO show_table (title, description, genre_id, duration_minutes, language, age_rating, producer, director, show_status) VALUES
('The Phantom of Broadway', 'A timeless tale of love, mystery, and music set beneath a grand opera house', 3, 150, 'English', 'PG-13', 'Andrew Lloyd Productions', 'Harold Prince', 'Active'),
('Shakespeares Hamlet', 'The classic tragedy of revenge, madness, and moral corruption in the Danish court', 4, 180, 'English', 'PG-13', 'Royal Shakespeare Co.', 'Kenneth Branagh', 'Active'),
('Laugh Out Loud', 'An evening of stand-up comedy featuring the best comedians', 2, 90, 'English', 'R', 'Comedy Central Live', 'Sarah Johnson', 'Active'),
('Romeo and Juliet', 'The greatest love story ever told', 5, 120, 'English', 'PG', 'Classic Theatre Productions', 'Baz Luhrmann', 'Coming Soon');
```

---

### 4.6 Insert Seats (Sample for Grand Theatre)
```sql
-- VIP Section (Rows A-B)
INSERT INTO seat (venue_id, row_number, seat_number, section, seat_category, is_accessible) VALUES
(1, 'A', '1', 'Orchestra', 'VIP', FALSE),
(1, 'A', '2', 'Orchestra', 'VIP', FALSE),
(1, 'A', '3', 'Orchestra', 'VIP', FALSE),
(1, 'A', '4', 'Orchestra', 'VIP', FALSE),
(1, 'B', '1', 'Orchestra', 'VIP', FALSE),
(1, 'B', '2', 'Orchestra', 'VIP', FALSE);

-- Premium Section (Rows C-E)
INSERT INTO seat (venue_id, row_number, seat_number, section, seat_category, is_accessible) VALUES
(1, 'C', '1', 'Orchestra', 'Premium', FALSE),
(1, 'C', '2', 'Orchestra', 'Premium', FALSE),
(1, 'C', '3', 'Orchestra', 'Premium', TRUE),
(1, 'D', '1', 'Orchestra', 'Premium', FALSE),
(1, 'D', '2', 'Orchestra', 'Premium', FALSE);

-- Standard Section (Rows F-J)
INSERT INTO seat (venue_id, row_number, seat_number, section, seat_category, is_accessible) VALUES
(1, 'F', '1', 'Orchestra', 'Standard', FALSE),
(1, 'F', '2', 'Orchestra', 'Standard', FALSE),
(1, 'G', '1', 'Orchestra', 'Standard', FALSE),
(1, 'G', '2', 'Orchestra', 'Standard', FALSE);

-- Balcony Section
INSERT INTO seat (venue_id, row_number, seat_number, section, seat_category, is_accessible) VALUES
(1, '1', '1', 'Balcony', 'Economy', FALSE),
(1, '1', '2', 'Balcony', 'Economy', FALSE),
(1, '1', '3', 'Balcony', 'Economy', FALSE);
```

---

### 4.7 Insert Seat Category Pricing
```sql
INSERT INTO seat_category_pricing (category_name, base_price, description) VALUES
('VIP', 150.00, 'Best seats in the house with premium amenities'),
('Premium', 100.00, 'Excellent view and comfort'),
('Standard', 60.00, 'Good quality seating'),
('Economy', 35.00, 'Affordable balcony seating'),
('Balcony', 35.00, 'Upper level seating');
```

---

### 4.8 Insert Performances
```sql
INSERT INTO performance (show_id, venue_id, performance_date, start_time, end_time, total_seats, available_seats, performance_status) VALUES
(1, 1, '2025-12-15', '19:30:00', '22:00:00', 17, 17, 'Scheduled'),
(1, 1, '2025-12-16', '19:30:00', '22:00:00', 17, 17, 'Scheduled'),
(2, 2, '2025-12-20', '18:00:00', '21:00:00', 15, 15, 'Scheduled'),
(3, 3, '2025-12-10', '20:00:00', '21:30:00', 12, 12, 'Scheduled');
```

---

### 4.9 Insert Performance Pricing
```sql
-- Performance 1: The Phantom of Broadway (2025-12-15)
INSERT INTO performance_pricing (performance_id, seat_category, price) VALUES
(1, 'VIP', 180.00),
(1, 'Premium', 120.00),
(1, 'Standard', 75.00),
(1, 'Economy', 40.00);

-- Performance 2: The Phantom of Broadway (2025-12-16)
INSERT INTO performance_pricing (performance_id, seat_category, price) VALUES
(2, 'VIP', 180.00),
(2, 'Premium', 120.00),
(2, 'Standard', 75.00),
(2, 'Economy', 40.00);

-- Performance 3: Hamlet (2025-12-20)
INSERT INTO performance_pricing (performance_id, seat_category, price) VALUES
(3, 'VIP', 200.00),
(3, 'Premium', 140.00),
(3, 'Standard', 85.00);

-- Performance 4: Comedy Show (2025-12-10)
INSERT INTO performance_pricing (performance_id, seat_category, price) VALUES
(4, 'Premium', 100.00),
(4, 'Standard', 60.00),
(4, 'Economy', 30.00);
```

---

### 4.10 Insert Sample Booking
```sql
-- Booking by John Doe for Performance 1
INSERT INTO booking (user_id, performance_id, booking_reference, total_amount, booking_status) VALUES
(2, 1, 'BK20251124001', 300.00, 'Confirmed');

-- Booking details for 2 VIP seats
INSERT INTO booking_detail (booking_id, seat_id, seat_price, row_number, seat_number, seat_category) VALUES
(1, 1, 180.00, 'A', '1', 'VIP'),
(1, 2, 120.00, 'A', '2', 'VIP');

-- Update available seats
UPDATE performance SET available_seats = available_seats - 2 WHERE performance_id = 1;
```

---

### 4.11 Insert Sample Payment
```sql
INSERT INTO payment (booking_id, payment_amount, payment_method, transaction_id, payment_status, card_last_four) VALUES
(1, 300.00, 'Credit Card', 'TXN123456789', 'Completed', '4242');
```

---

## 5. Verification Queries

### 5.1 Verify Database Structure
```sql
-- List all tables
SHOW TABLES;

-- Check table structure
DESCRIBE role;
DESCRIBE user;
DESCRIBE audit_log;
DESCRIBE booking;
DESCRIBE performance;

-- View foreign key constraints
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'theatre_booking'
AND REFERENCED_TABLE_NAME IS NOT NULL;
```

---

### 5.2 Test Data Integrity
```sql
-- Check if all bookings have valid users and performances
SELECT b.booking_id, u.email, p.performance_date
FROM booking b
JOIN user u ON b.user_id = u.user_id
JOIN performance p ON b.performance_id = p.performance_id;

-- Verify seat availability calculation
SELECT 
    p.performance_id,
    s.title AS show_title,
    p.total_seats,
    p.available_seats,
    (p.total_seats - p.available_seats) AS seats_booked
FROM performance p
JOIN show_table s ON p.show_id = s.show_id;

-- Check user roles
SELECT u.email, u.is_admin, r.role_name, r.can_manage_shows, r.can_manage_users
FROM user u
LEFT JOIN role r ON u.role_id = r.role_id;

-- View audit log entries
SELECT al.log_id, u.email AS user_email, al.action, al.entity_type, al.entity_id, al.timestamp
FROM audit_log al
LEFT JOIN user u ON al.user_id = u.user_id
ORDER BY al.timestamp DESC;
```

---

### 5.3 RBAC Permission Check Queries
```sql
-- Check if user has specific permission
SELECT 
    u.email,
    r.role_name,
    r.can_manage_shows,
    r.can_issue_refunds
FROM user u
JOIN role r ON u.role_id = r.role_id
WHERE u.user_id = ?;

-- List all users with their permissions
SELECT 
    u.user_id,
    u.email,
    u.is_admin,
    r.role_name,
    r.can_manage_shows,
    r.can_manage_venues,
    r.can_manage_performances,
    r.can_manage_bookings,
    r.can_view_analytics,
    r.can_manage_users,
    r.can_manage_pricing,
    r.can_issue_refunds
FROM user u
LEFT JOIN role r ON u.role_id = r.role_id
ORDER BY r.role_name, u.email;
```

---

## 6. Table Summary

| # | Table Name            | Purpose                              | Records Est. |
|---|----------------------|--------------------------------------|--------------|
| 1 | role                 | RBAC roles with permissions          | 4+           |
| 2 | user                 | Customer and admin accounts          | 1,000+       |
| 3 | audit_log            | System audit trail                   | 10,000+      |
| 4 | genre                | Show categories                      | 10           |
| 5 | show_table           | Theatre productions                  | 50           |
| 6 | venue                | Theatre locations                    | 5            |
| 7 | seat                 | Individual seats per venue           | 2,000+       |
| 8 | seat_category_pricing| Base pricing tiers                   | 5            |
| 9 | performance          | Scheduled show instances             | 200          |
| 10| performance_pricing  | Dynamic pricing per performance      | 800          |
| 11| booking              | Customer reservations                | 5,000+       |
| 12| booking_detail       | Individual seat assignments          | 15,000+      |
| 13| payment              | Transaction records                  | 5,000+       |

**Total Tables**: 13

---

## Document Control
- **Version**: 2.0
- **Date**: November 27, 2025
- **Database**: MySQL 8.0+
- **Total Tables**: 13 (including ROLE and AUDIT_LOG)
- **Purpose**: Academic Database Design - Physical Implementation
