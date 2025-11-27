# 🎭 Online Theatre Booking System - Complete Database Design & Implementation

[![GitHub](https://img.shields.io/badge/GitHub-nekumartins%2Ftheatre--333-purple)](https://github.com/nekumartins/theatre-333)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)](https://fastapi.tiangolo.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)](https://mysql.com)

## Project Overview
A fully functional **Online Theatre Booking System** with complete database design documentation and working web application. This project demonstrates Systems Analysis and Design principles from business requirements through production-ready implementation.

### 🌐 Live Features
- ✅ User registration & JWT authentication
- ✅ Browse shows & performances
- ✅ Interactive seat selection (491 seats)
- ✅ Complete booking workflow
- ✅ Payment processing
- ✅ E-Ticket generation with QR codes
- ✅ Admin panel for management
- ✅ Role-based access control (RBAC)

---

## 📚 Documentation Structure

### 1. [Business Information Requirements](01_BUSINESS_REQUIREMENTS.md)
Comprehensive analysis of business processes, stakeholders, and data requirements including:
- Major business processes (user registration, show management, booking, payment)
- Actors and stakeholders identification
- Data objects and entities
- Detailed data requirements and business rules
- Non-functional requirements

### 2. [Conceptual Data Model (ERD)](02_CONCEPTUAL_MODEL_ERD.md)
Entity-Relationship Diagram specifications using Oracle ERDish / Crow's Foot notation:
- 13 entities with complete attribute definitions (including ROLE and AUDIT_LOG for RBAC)
- Primary and foreign key specifications
- Relationship definitions with cardinality and optionality
- Business rules reflected in the ERD
- **SVG ERD diagram included**: `presentation/erd_diagram.svg`

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
FastAPI and HTML/Tailwind integration:
- Project structure and technology stack
- Database connection setup
- SQLAlchemy models and schemas
- 15+ API endpoints with code examples
- Frontend templates with Tailwind CSS
- Essential SQL queries with explanations
- Security best practices

### 6. [Presentation Materials](presentation/)
- `index.html` - Interactive HTML presentation (15 slides)
- `Theatre_Booking_System.pptx` - PowerPoint presentation
- `erd_diagram.svg` - Crow's Foot ERD diagram

## 🎯 Key Features

### Database Design
- **13 normalized tables** (3NF compliance)
- **Role-Based Access Control (RBAC)** with granular permissions
- **Audit logging** for admin/staff actions
- **Dynamic pricing** support per performance
- **Seat management** with 5 categories (VIP, Premium, Standard, Economy, Accessible)
- **Booking workflow** with payment tracking
- **User management** with JWT authentication & RBAC

### Core Entities (13 Tables)
| Entity | Description |
|--------|-------------|
| **ROLES** | RBAC roles with granular permissions |
| **USERS** | Customer accounts with authentication & role assignment |
| **AUDIT_LOGS** | System audit trail for admin actions |
| **GENRES** | Show categorization |
| **SHOWS** | Theatre productions |
| **VENUES** | Theatre locations |
| **SEATS** | Venue seating (491 seats per venue) |
| **SEAT_CATEGORY_PRICING** | Pricing tiers with base prices |
| **PERFORMANCES** | Scheduled show instances |
| **PERFORMANCE_PRICING** | Dynamic pricing per performance |
| **BOOKINGS** | Customer reservations |
| **BOOKING_DETAILS** | Individual seat assignments |
| **PAYMENTS** | Transaction records |

---

## 🚀 Quick Start

### Prerequisites
- MySQL 8.0+
- Python 3.9+
- pip (Python package manager)

### Database Setup
```bash
# 1. Create MySQL database
mysql -u root -p -e "CREATE DATABASE theatre_booking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 2. Update database credentials in backend/app/database.py
# DATABASE_URL = "mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/theatre_booking"
```

### Application Setup
```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv data333
.\data333\Scripts\Activate.ps1   # Windows PowerShell
# source data333/bin/activate    # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database with sample data
python init_db.py

# 5. Run the server
python -m uvicorn app.main:app --reload --port 8000
```

### Access the Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8000/admin (requires admin account)

---

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login (returns JWT) |
| GET | `/api/profile/me` | Get current user profile |
| PUT | `/api/profile/me` | Update user profile |

### Shows & Performances
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shows` | List all shows |
| GET | `/api/shows/{id}` | Get show details |
| GET | `/api/performances/show/{show_id}` | Get performances for show |
| GET | `/api/performances/{id}/seats` | Get available seats |

### Bookings & Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings` | Create booking |
| GET | `/api/bookings/my-bookings` | User's booking history |
| GET | `/api/bookings/{id}` | Get booking details |
| POST | `/api/payments` | Process payment |

### Sample Queries

**Get Available Performances:**
```sql
SELECT p.*, s.title, v.name as venue_name
FROM performances p
JOIN shows s ON p.show_id = s.show_id
JOIN venues v ON s.venue_id = v.venue_id
WHERE p.performance_date >= CURDATE()
  AND p.available_seats > 0
  AND p.is_active = TRUE;
```

**User Booking History:**
```sql
SELECT b.booking_reference, s.title, p.performance_date, b.total_amount, b.status
FROM bookings b
JOIN performances p ON b.performance_id = p.performance_id
JOIN shows s ON p.show_id = s.show_id
WHERE b.user_id = ?
ORDER BY b.booking_date DESC;
```

---

## 🔒 Security Features
- ✅ Bcrypt password hashing
- ✅ JWT authentication with expiration
- ✅ Role-based access control (Admin/User)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ Input validation (Pydantic schemas)
- ✅ CORS configuration
- ✅ Protected API routes

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend Framework** | FastAPI (Python 3.9+) |
| **Database** | MySQL 8.0 |
| **ORM** | SQLAlchemy 2.0 |
| **Migrations** | Alembic |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt (passlib) |
| **Frontend** | HTML5, Tailwind CSS, JavaScript |
| **Templating** | Jinja2 |

---

## 📦 Project Structure
```
theatre-333/
├── 01_BUSINESS_REQUIREMENTS.md     # Business analysis
├── 02_CONCEPTUAL_MODEL_ERD.md      # ERD specification
├── 03_LOGICAL_MODEL.md             # Logical schema + normalization
├── 04_PHYSICAL_MODEL_SQL.md        # MySQL implementation
├── 05_APPLICATION_IMPLEMENTATION.md # Integration guide
├── README.md                       # This file
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application
│   │   ├── database.py             # MySQL connection
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── crud.py                 # Database operations
│   │   ├── auth.py                 # JWT authentication
│   │   ├── utils.py                # Utility functions
│   │   └── routers/
│   │       ├── users.py
│   │       ├── shows.py
│   │       ├── performances.py
│   │       ├── bookings.py
│   │       └── payments.py
│   ├── alembic/                    # Database migrations
│   ├── init_db.py                  # Database initialization
│   └── requirements.txt
│
├── frontend/
│   ├── static/
│   │   ├── css/styles.css
│   │   └── js/app.js
│   └── templates/
│       ├── base.html               # Base template
│       ├── index.html              # Home page
│       ├── shows.html              # Browse shows
│       ├── show_detail.html        # Show details
│       ├── seat_selection.html     # Interactive seat map
│       ├── payment.html            # Payment page
│       ├── confirmation.html       # Booking confirmation
│       ├── ticket.html             # E-Ticket with QR
│       ├── my_bookings.html        # Booking history
│       ├── admin.html              # Admin panel
│       ├── login.html              # Login page
│       └── register.html           # Registration page
│
└── presentation/
    ├── index.html                  # HTML presentation
    ├── Theatre_Booking_System.pptx # PowerPoint slides
    └── erd_diagram.svg             # Crow's Foot ERD
```

---

## 🎯 Implemented Use Cases

| # | Use Case | Status |
|---|----------|--------|
| 1 | User Registration & Login | ✅ Complete |
| 2 | Browse Shows & Performances | ✅ Complete |
| 3 | Interactive Seat Selection | ✅ Complete |
| 4 | Booking Creation | ✅ Complete |
| 5 | Payment Processing | ✅ Complete |
| 6 | E-Ticket Generation (QR Code) | ✅ Complete |
| 7 | Booking History | ✅ Complete |
| 8 | Booking Cancellation | ✅ Complete |
| 9 | Admin Show Management | ✅ Complete |
| 10 | Admin User Management | ✅ Complete |
| 11 | Profile Management | ✅ Complete |

---

## 🎓 Academic Compliance

This project meets university-level requirements for **CSC 333 - Database Systems**:

| Requirement | Documentation |
|-------------|---------------|
| ✅ Business analysis | `01_BUSINESS_REQUIREMENTS.md` |
| ✅ Conceptual modeling (ERD) | `02_CONCEPTUAL_MODEL_ERD.md` + `erd_diagram.svg` |
| ✅ Logical modeling | `03_LOGICAL_MODEL.md` |
| ✅ Normalization (3NF) | `03_LOGICAL_MODEL.md` |
| ✅ Physical modeling (MySQL) | `04_PHYSICAL_MODEL_SQL.md` |
| ✅ Application integration | `05_APPLICATION_IMPLEMENTATION.md` |
| ✅ Working implementation | `backend/` + `frontend/` |

---

## 🔄 Future Enhancements

- [ ] Mobile application (React Native/Flutter)
- [ ] Email/SMS notifications
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Seat hold timeout mechanism
- [ ] Promotional codes and discounts
- [ ] Integration with payment gateways (Stripe, PayPal)

---

## 👨‍💻 Author

**Chukwuneku Akpotohwo**  
Email: akpotohwoo@gmail.com  
GitHub: [nekumartins/theatre-333](https://github.com/nekumartins/theatre-333)

---

## 📄 License

This is an academic project developed for educational purposes.

---

**Version**: 2.0  
**Date**: November 27, 2025  
**Course**: CSC 333 - Database Systems  
**Database**: MySQL 8.0  
**Framework**: FastAPI + HTML/Tailwind CSS
