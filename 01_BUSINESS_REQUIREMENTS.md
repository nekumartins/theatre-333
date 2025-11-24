# Online Theatre Booking System - Business Information Requirements

## 1. System Overview
The Online Theatre Booking System is a web-based platform that enables customers to browse theatre shows, select seats, make bookings, and process payments online. It also provides administrative functions for managing shows, venues, and bookings.

---

## 2. Major Business Processes

### 2.1 User Registration and Authentication
- New customers register with personal details
- Existing users log in to access booking features
- Users can update their profile information
- Password recovery and reset functionality

### 2.2 Show Management (Admin)
- Theatre administrators add new shows/performances
- Define show details (title, description, genre, duration, age rating)
- Schedule multiple performances for each show
- Set pricing tiers for different seat categories
- Update or cancel shows as needed

### 2.3 Venue and Seat Management (Admin)
- Define theatre venues with seating capacity
- Configure seating layout (rows, seat numbers, sections)
- Categorize seats (VIP, Premium, Standard, etc.)
- Set pricing for each seat category
- Mark seats as available, booked, or unavailable

### 2.4 Performance Scheduling
- Schedule specific date and time for performances
- Associate performances with shows and venues
- Set ticket availability for each performance
- Manage seat inventory per performance

### 2.5 Ticket Browsing and Search
- Customers browse available shows
- Filter by date, genre, venue, price range
- View show details and available performances
- Check seat availability for specific performances

### 2.6 Seat Selection and Reservation
- Visual seat map display for performance
- Customers select preferred seats
- Temporary seat hold during booking process (time-limited)
- Real-time seat availability updates

### 2.7 Booking Creation
- Customer initiates booking for selected seats
- System calculates total price (including taxes/fees)
- Booking status: Pending, Confirmed, Cancelled
- Generate unique booking reference number

### 2.8 Payment Processing
- Customer provides payment details
- Process payment through payment gateway
- Record payment transaction details
- Update booking status upon successful payment
- Handle payment failures and refunds

### 2.9 Ticket Generation and Delivery
- Generate e-tickets upon successful payment
- Send booking confirmation via email
- Provide QR code or barcode for ticket validation
- Allow customers to download/print tickets

### 2.10 Booking Management
- Customers view their booking history
- Cancel bookings (within cancellation policy)
- Request refunds for cancelled bookings
- Modify bookings (subject to availability)

### 2.11 Reporting and Analytics (Admin)
- Sales reports by show, venue, date range
- Occupancy rates and revenue analysis
- Customer booking patterns
- Popular shows and peak times

---

## 3. Actors/Stakeholders

### 3.1 Primary Actors
- **Customer/User**: Browses shows, makes bookings, manages account
- **Guest**: Browses shows without registration (limited access)
- **System Administrator**: Manages shows, venues, performances, pricing
- **Box Office Staff**: Assists with bookings, handles customer inquiries
- **Finance Manager**: Reviews payment reports, processes refunds

### 3.2 External Systems
- **Payment Gateway**: Processes credit/debit card transactions
- **Email Service**: Sends confirmation and notification emails
- **SMS Service**: Sends booking confirmations and reminders

---

## 4. Data Objects and Entities

### 4.1 User Management
- **User/Customer**
  - User ID, Name, Email, Phone, Password, Address, Registration Date
  - Account Status (Active, Suspended, Deleted)

### 4.2 Theatre Content
- **Show**
  - Show ID, Title, Description, Genre, Duration, Language, Age Rating
  - Poster Image, Producer, Director
  
- **Performance**
  - Performance ID, Show ID, Venue ID, Performance Date, Start Time
  - Status (Scheduled, Ongoing, Completed, Cancelled)

### 4.3 Venue and Seating
- **Venue**
  - Venue ID, Name, Address, City, Capacity, Contact Details
  - Facilities Information
  
- **Seat**
  - Seat ID, Venue ID, Row Number, Seat Number, Section
  - Category (VIP, Premium, Standard, Balcony)
  
- **Seat Category Pricing**
  - Category, Base Price, Description

### 4.4 Booking and Transactions
- **Booking**
  - Booking ID, User ID, Performance ID, Booking Date/Time
  - Total Amount, Status (Pending, Confirmed, Cancelled)
  - Booking Reference Number
  
- **Booking Detail**
  - Booking ID, Seat ID, Seat Price, Row, Seat Number
  
- **Payment**
  - Payment ID, Booking ID, Amount, Payment Date/Time
  - Payment Method (Credit Card, Debit Card, Digital Wallet)
  - Transaction ID, Payment Status (Pending, Completed, Failed, Refunded)
  - Payment Gateway Response

### 4.5 Supporting Data
- **Genre**
  - Genre ID, Name, Description
  
- **Pricing Tier**
  - Performance ID, Seat Category, Price (allows dynamic pricing)

---

## 5. Detailed Data Requirements

### 5.1 User Registration
- Capture full name (first, last)
- Valid email address (unique identifier)
- Phone number with country code
- Secure password (hashed storage)
- Optional: Date of birth, gender, mailing address
- Timestamp of registration
- Email verification status

### 5.2 Show Information
- Unique show identifier
- Title (maximum 200 characters)
- Detailed description (up to 2000 characters)
- Genre classification (single or multiple)
- Duration in minutes
- Language of performance
- Age rating/restriction
- Cast and crew information
- Promotional materials (images, trailers)
- Show status (Active, Archived, Coming Soon)

### 5.3 Performance Details
- Unique performance identifier
- Link to parent show
- Venue assignment
- Specific date and time
- End time (calculated or stored)
- Total available seats
- Seats remaining (dynamic)
- Special notes (e.g., "With live orchestra")
- Performance status

### 5.4 Seat and Venue Data
- Unique seat identifier per venue
- Physical location (row, number, section)
- Seat category with pricing implications
- Accessibility features (wheelchair accessible, companion seats)
- Venue capacity and layout information
- Venue amenities (parking, restaurants)

### 5.5 Booking Information
- Unique booking reference (alphanumeric)
- User making the booking
- Associated performance
- Timestamp of booking creation
- List of seats booked (one or multiple)
- Individual and total pricing
- Applicable discounts or promotions
- Booking status workflow
- Cancellation timestamp (if applicable)
- Refund status and amount

### 5.6 Payment Data
- Secure payment transaction ID
- Link to booking
- Payment amount and currency
- Payment method details (masked card number)
- Payment gateway transaction reference
- Payment timestamp
- Success/failure status
- Error messages (if failed)
- Refund tracking information

### 5.7 Business Rules and Constraints
- A seat can only be booked once per performance
- Bookings must be completed (paid) within 15 minutes or released
- Cancellations allowed up to 24 hours before performance
- Minimum age requirements enforced for age-restricted shows
- Payment must be confirmed before ticket generation
- Refund amount calculated based on cancellation policy
- User email must be unique across the system
- Performance cannot be scheduled without a valid show and venue
- Seat pricing may vary by performance (dynamic pricing)

---

## 6. Non-Functional Requirements

### 6.1 Performance
- System should handle 1000 concurrent users
- Seat selection page loads within 2 seconds
- Payment processing completes within 5 seconds

### 6.2 Security
- All passwords must be encrypted (bcrypt/Argon2)
- Payment data must comply with PCI DSS standards
- HTTPS for all transactions
- SQL injection and XSS prevention

### 6.3 Availability
- 99.5% uptime during business hours
- Scheduled maintenance windows communicated in advance

### 6.4 Usability
- Intuitive seat selection interface
- Mobile-responsive design
- Accessibility compliance (WCAG 2.1)

### 6.5 Data Integrity
- ACID properties for booking transactions
- Automatic seat release for unpaid bookings
- Audit trail for all bookings and payments

---

## 7. Reporting Requirements

### 7.1 Administrative Reports
- Daily sales summary by show and performance
- Revenue breakdown by seat category
- Booking cancellation rates
- User registration trends

### 7.2 Operational Reports
- Current seat availability by performance
- Upcoming performances schedule
- Payment transaction log
- Failed payment analysis

### 7.3 Customer Reports
- Personal booking history
- Payment receipts
- Upcoming show reminders

---

## Document Control
- **Version**: 1.0
- **Date**: November 24, 2025
- **Project**: Online Theatre Booking System
- **Purpose**: Academic Systems Analysis and Design Project
