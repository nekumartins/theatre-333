# Online Theatre Booking System - Complete Database Design Documentation

## Project Overview
This repository contains comprehensive documentation for an **Online Theatre Booking System** database design project. The documentation follows academic standards for Systems Analysis and Design, covering all phases from business requirements through application implementation.

## 📚 Documentation Structure

### 1. [Business Information Requirements](01_BUSINESS_REQUIREMENTS.md)
Comprehensive analysis of business processes, stakeholders, and data requirements including:
- Major business processes (user registration, show management, booking, payment)
- Actors and stakeholders identification
- Data objects and entities
- Detailed data requirements and business rules
- Non-functional requirements

### 2. [Conceptual Data Model (ERD)](02_CONCEPTUAL_MODEL_ERD.md)
Entity-Relationship Diagram specifications using Oracle ERDish notation:
- 11 entities with complete attribute definitions
- Primary and foreign key specifications
- Relationship definitions with cardinality and optionality
- Business rules reflected in the ERD
- Drawing instructions for Visio/Draw.io

### 3. [Logical Data Model](03_LOGICAL_MODEL.md)
Relational schema with normalization analysis:
- Complete relational tables with data types
- Functional dependencies for all tables
- Normalization process (1NF, 2NF, 3NF)
- Referential integrity constraints
- Business logic and domain constraints

### 4. [Physical Model & SQL Scripts](04_PHYSICAL_MODEL_SQL.md)
MySQL implementation with complete SQL code:
- MySQL-compliant CREATE TABLE statements
- Foreign key constraint definitions
- Sample INSERT statements for testing
- Verification queries
- Data type recommendations

### 5. [Application Implementation Guide](05_APPLICATION_IMPLEMENTATION.md)
FastAPI and HTML/Tailwind integration guidance:
- Project structure and technology stack
- Database connection setup
- SQLAlchemy models and schemas
- Key API endpoints with code examples
- Frontend templates with Tailwind CSS
- Essential SQL queries with explanations
- Security best practices

## 🎯 Key Features

### Database Design
- **11 normalized tables** (3NF compliance)
- **Dynamic pricing** support per performance
- **Seat management** with venue layouts
- **Booking workflow** with payment tracking
- **User management** with authentication

### Core Entities
1. **USER** - Customer accounts and authentication
2. **GENRE** - Show categorization
3. **SHOW** - Theatre productions
4. **VENUE** - Theatre locations
5. **SEAT** - Venue seating configuration
6. **PERFORMANCE** - Scheduled show instances
7. **PERFORMANCE_PRICING** - Dynamic pricing per performance
8. **BOOKING** - Customer reservations
9. **BOOKING_DETAIL** - Individual seat assignments
10. **PAYMENT** - Transaction records
11. **SEAT_CATEGORY_PRICING** - Base pricing reference

## 🚀 Quick Start

### Prerequisites
- MySQL 8.0+
- Python 3.9+
- FastAPI framework
- Node.js (for Tailwind CSS)

### Database Setup
```bash
# Create database
mysql -u root -p < 04_PHYSICAL_MODEL_SQL.md

# Run the SQL commands from section 2 and 3 of the physical model document
```

### Application Setup
```bash
# Install Python dependencies
pip install fastapi sqlalchemy pymysql python-dotenv passlib python-jose

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the FastAPI application
uvicorn app.main:app --reload
```

## 📊 Sample Queries

### Get Available Performances
```sql
SELECT p.*, s.title, v.venue_name
FROM performance p
JOIN show_table s ON p.show_id = s.show_id
JOIN venue v ON p.venue_id = v.venue_id
WHERE p.performance_date >= CURDATE()
  AND p.available_seats > 0;
```

### User Booking History
```sql
SELECT b.booking_reference, s.title, p.performance_date, b.total_amount
FROM booking b
JOIN performance p ON b.performance_id = p.performance_id
JOIN show_table s ON p.show_id = s.show_id
WHERE b.user_id = ?
ORDER BY b.booking_date DESC;
```

## 🔒 Security Features
- Bcrypt password hashing
- JWT authentication
- SQL injection prevention (parameterized queries)
- PCI DSS compliance for payments
- HTTPS enforcement

## 📈 Business Rules Implemented

1. **Seat Uniqueness**: Each seat can only be booked once per performance
2. **Booking Expiration**: Pending bookings expire after 15 minutes
3. **Cancellation Policy**: Bookings can be cancelled 24 hours before performance
4. **Dynamic Pricing**: Prices vary by performance and seat category
5. **Seat Availability**: Real-time tracking of available seats

## 🎓 Academic Compliance

This project meets university-level requirements for:
- ✅ Business analysis and requirements gathering
- ✅ Conceptual modeling (ERD with Oracle notation)
- ✅ Logical modeling (relational schema + normalization)
- ✅ Physical modeling (MySQL implementation)
- ✅ Application integration (FastAPI + HTML/Tailwind)

## 📝 Documentation Standards

All documentation follows:
- Clear section numbering
- Consistent terminology
- Academic writing style
- Complete code examples
- Practical implementation guidance

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- MySQL (Database)
- JWT (Authentication)

**Frontend:**
- HTML5
- Tailwind CSS
- JavaScript (Vanilla/Alpine.js)

## 📦 Project Structure
```
theatre-booking/
├── 01_BUSINESS_REQUIREMENTS.md
├── 02_CONCEPTUAL_MODEL_ERD.md
├── 03_LOGICAL_MODEL.md
├── 04_PHYSICAL_MODEL_SQL.md
├── 05_APPLICATION_IMPLEMENTATION.md
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── routers/
│   └── requirements.txt
└── frontend/
    ├── templates/
    └── static/
```

## 🎯 Use Cases Supported

1. **User Registration & Authentication**
2. **Browse Shows & Performances**
3. **Seat Selection & Booking**
4. **Payment Processing**
5. **Booking Management**
6. **Admin Reporting**
7. **Revenue Analytics**

## 📊 Reports Available

1. Daily Sales Report
2. Performance Occupancy Analysis
3. User Booking History
4. Revenue by Show/Venue
5. Seat Category Performance

## 🔄 Future Enhancements

- Mobile application (React Native/Flutter)
- Email/SMS notifications
- Advanced analytics dashboard
- Multi-language support
- Seat hold timeout mechanism
- Promotional codes and discounts

## 📞 Support & Contact

For questions or clarifications about this project:
- Review the detailed documentation in each markdown file
- Check the code examples in the Application Implementation guide
- Refer to the SQL scripts for database setup

## 📄 License

This is an academic project developed for educational purposes.

---

**Version**: 1.0  
**Date**: November 24, 2025  
**Purpose**: University Systems Analysis and Design Project  
**Database**: MySQL 8.0+  
**Framework**: FastAPI + HTML/Tailwind CSS
