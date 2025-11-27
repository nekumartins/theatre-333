# Online Theatre Booking System - Conceptual Data Model (ERD)

## Entity-Relationship Diagram Specification
**Notation**: Oracle ERDish / Crow's Foot notation  
**Tool Compatibility**: Visio, Draw.io, Lucidchart  
**Database**: MySQL 8.0  
**Implementation**: SQLAlchemy ORM with FastAPI

### 📊 ERD Diagram
The complete ERD diagram is available as an SVG file:
- **Location**: `presentation/erd_diagram.svg`
- **Features**: Crow's Foot notation, all entities, relationships with cardinality

---

## 1. Entities and Attributes

### 1.1 USER
**Definition**: Registered customer who can browse shows and make bookings.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **user_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| first_name | VARCHAR(50) | NOT NULL | User's first name |
| last_name | VARCHAR(50) | NOT NULL | User's last name |
| email | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | User's email address |
| phone | VARCHAR(20) | | Contact phone number |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt encrypted password |
| date_of_birth | DATE | | User's date of birth |
| address_line1 | VARCHAR(100) | | Primary address |
| address_line2 | VARCHAR(100) | | Secondary address (optional) |
| city | VARCHAR(50) | | City of residence |
| postal_code | VARCHAR(20) | | Postal/ZIP code |
| country | VARCHAR(50) | | Country of residence |
| registration_date | DATE | NOT NULL | Date user registered |
| email_verified | BOOLEAN | DEFAULT FALSE | Email verification flag |
| account_status | VARCHAR(20) | DEFAULT 'Active' | Active, Suspended, Deactivated |
| is_admin | BOOLEAN | DEFAULT FALSE | Legacy admin flag |
| role_id | INT | FK → ROLE | RBAC role assignment |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: user_id  
**Foreign Keys**: role_id → ROLE

---

### 1.2 ROLE (RBAC)
**Definition**: Role-based access control - defines user roles and their permissions.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **role_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| role_name | VARCHAR(50) | UNIQUE, NOT NULL | Admin, Manager, Staff, Customer |
| description | TEXT | | Role description |
| can_manage_shows | BOOLEAN | DEFAULT FALSE | Permission to manage shows |
| can_manage_venues | BOOLEAN | DEFAULT FALSE | Permission to manage venues |
| can_manage_performances | BOOLEAN | DEFAULT FALSE | Permission to manage performances |
| can_manage_bookings | BOOLEAN | DEFAULT FALSE | Permission to manage bookings |
| can_view_analytics | BOOLEAN | DEFAULT FALSE | Permission to view analytics |
| can_manage_users | BOOLEAN | DEFAULT FALSE | Permission to manage users |
| can_manage_pricing | BOOLEAN | DEFAULT FALSE | Permission to manage pricing |
| can_issue_refunds | BOOLEAN | DEFAULT FALSE | Permission to issue refunds |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: role_id

---

### 1.3 AUDIT_LOG
**Definition**: Audit trail for tracking admin/staff actions for compliance and debugging.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **log_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| user_id | INT | FK → USER, NOT NULL | User who performed action |
| action | VARCHAR(100) | NOT NULL | Action type (CREATE_SHOW, UPDATE_BOOKING, etc.) |
| entity_type | VARCHAR(50) | NOT NULL | Entity type (Show, Booking, User) |
| entity_id | INT | | ID of affected entity |
| old_values | JSON | | Previous state for updates |
| new_values | JSON | | New state |
| ip_address | VARCHAR(45) | | Client IP address |
| user_agent | VARCHAR(255) | | Browser/client user agent |
| timestamp | TIMESTAMP | DEFAULT NOW() | Action timestamp |

**Primary Key**: log_id  
**Foreign Keys**: user_id → USER

---

### 1.4 GENRE
**Definition**: Category or type of theatrical performance.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **genre_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| genre_name | VARCHAR(50) | UNIQUE, NOT NULL | Genre name (Drama, Comedy, Musical) |
| description | TEXT | | Description of the genre |

**Primary Key**: genre_id

---

### 1.5 SHOW
**Definition**: A theatrical production or performance title that can be scheduled multiple times.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **show_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| title | VARCHAR(200) | NOT NULL | Name of the show |
| description | TEXT | | Detailed description |
| genre_id | INT | FK → GENRE, NOT NULL | Genre category |
| duration_minutes | INT | NOT NULL | Length of show in minutes |
| language | VARCHAR(50) | | Language of performance |
| age_rating | VARCHAR(10) | | Minimum age requirement |
| poster_url | VARCHAR(255) | | URL to promotional poster |
| producer | VARCHAR(100) | | Name of producer |
| director | VARCHAR(100) | | Name of director |
| show_status | VARCHAR(20) | DEFAULT 'Active' | Active, Coming Soon, Archived |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: show_id  
**Foreign Keys**: genre_id → GENRE

---

### 1.6 VENUE
**Definition**: Physical location where performances take place.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **venue_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| venue_name | VARCHAR(100) | NOT NULL | Name of the theatre/venue |
| address_line1 | VARCHAR(100) | NOT NULL | Primary address |
| address_line2 | VARCHAR(100) | | Secondary address |
| city | VARCHAR(50) | NOT NULL | City location |
| postal_code | VARCHAR(20) | | Postal/ZIP code |
| country | VARCHAR(50) | NOT NULL | Country |
| total_capacity | INT | NOT NULL | Maximum seating capacity |
| phone | VARCHAR(20) | | Contact phone number |
| facilities | TEXT | | Facilities description |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: venue_id

---

### 1.7 SEAT
**Definition**: Individual seat in a venue with specific location and category.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **seat_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| venue_id | INT | FK → VENUE, NOT NULL | Parent venue |
| row_number | VARCHAR(10) | NOT NULL | Row identifier (A, B, C) |
| seat_number | VARCHAR(10) | NOT NULL | Seat number within row |
| section | VARCHAR(50) | | Section (Orchestra, Balcony) |
| seat_category | VARCHAR(20) | NOT NULL | VIP, Premium, Standard |
| is_accessible | BOOLEAN | DEFAULT FALSE | Wheelchair accessibility |
| is_active | BOOLEAN | DEFAULT TRUE | Seat availability |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Primary Key**: seat_id  
**Foreign Keys**: venue_id → VENUE  
**Composite Unique Key**: (venue_id, row_number, seat_number)

---

### 1.8 SEAT_CATEGORY_PRICING
**Definition**: Base pricing information for different seat categories.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **category_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| category_name | VARCHAR(50) | UNIQUE, NOT NULL | VIP, Premium, Standard, Economy |
| base_price | DECIMAL(10,2) | NOT NULL | Default price for category |
| description | TEXT | | Category features description |

**Primary Key**: category_id

---

### 1.9 PERFORMANCE
**Definition**: A specific scheduled instance of a show at a venue on a particular date and time.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **performance_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| show_id | INT | FK → SHOW, NOT NULL | Associated show |
| venue_id | INT | FK → VENUE, NOT NULL | Performance venue |
| performance_date | DATE | NOT NULL | Date of performance |
| start_time | TIME | NOT NULL | Start time |
| end_time | TIME | | Expected end time |
| total_seats | INT | NOT NULL | Total seats available |
| available_seats | INT | NOT NULL | Current available seats |
| performance_status | VARCHAR(20) | DEFAULT 'Scheduled' | Scheduled, Ongoing, Completed, Cancelled |
| special_notes | TEXT | | Additional information |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: performance_id  
**Foreign Keys**: show_id → SHOW, venue_id → VENUE

---

### 1.10 PERFORMANCE_PRICING
**Definition**: Dynamic pricing for seat categories specific to each performance.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **pricing_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| performance_id | INT | FK → PERFORMANCE, NOT NULL | Associated performance |
| seat_category | VARCHAR(20) | NOT NULL | VIP, Premium, Standard |
| price | DECIMAL(10,2) | NOT NULL | Price for this category |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Primary Key**: pricing_id  
**Foreign Keys**: performance_id → PERFORMANCE  
**Composite Unique Key**: (performance_id, seat_category)

---

### 1.11 BOOKING
**Definition**: A customer's reservation for one or more seats at a specific performance.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **booking_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| user_id | INT | FK → USER, NOT NULL | Booking customer |
| performance_id | INT | FK → PERFORMANCE, NOT NULL | Associated performance |
| booking_reference | VARCHAR(20) | UNIQUE, NOT NULL | Alphanumeric reference code |
| booking_date | TIMESTAMP | DEFAULT NOW() | Booking creation time |
| total_amount | DECIMAL(10,2) | NOT NULL | Total price for all seats |
| booking_status | VARCHAR(20) | DEFAULT 'Pending' | Pending, Confirmed, Cancelled, Expired |
| payment_deadline | TIMESTAMP | | 15-minute payment deadline |
| cancellation_date | TIMESTAMP | | Cancellation date if applicable |
| refund_amount | DECIMAL(10,2) | | Amount refunded if applicable |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |
| updated_at | TIMESTAMP | ON UPDATE NOW() | Last update timestamp |

**Primary Key**: booking_id  
**Foreign Keys**: user_id → USER, performance_id → PERFORMANCE  
**Unique Key**: booking_reference

---

### 1.12 BOOKING_DETAIL
**Definition**: Individual seat assignments within a booking.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **booking_detail_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| booking_id | INT | FK → BOOKING, NOT NULL | Parent booking |
| seat_id | INT | FK → SEAT, NOT NULL | Reserved seat |
| seat_price | DECIMAL(10,2) | NOT NULL | Price paid for seat |
| row_number | VARCHAR(10) | NOT NULL | Row (denormalized) |
| seat_number | VARCHAR(10) | NOT NULL | Seat number (denormalized) |
| seat_category | VARCHAR(20) | NOT NULL | Category (denormalized) |

**Primary Key**: booking_detail_id  
**Foreign Keys**: booking_id → BOOKING, seat_id → SEAT  
**Composite Unique Key**: (booking_id, seat_id)

---

### 1.13 PAYMENT
**Definition**: Financial transaction record for a booking.

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| **payment_id** | INT | PK, AUTO_INCREMENT | Unique identifier |
| booking_id | INT | FK → BOOKING, NOT NULL | Associated booking |
| payment_amount | DECIMAL(10,2) | NOT NULL | Amount paid |
| payment_method | VARCHAR(50) | NOT NULL | Credit Card, Debit Card, PayPal, Bank Transfer |
| payment_date | TIMESTAMP | DEFAULT NOW() | Payment timestamp |
| transaction_id | VARCHAR(100) | | Gateway transaction reference |
| payment_status | VARCHAR(20) | DEFAULT 'Pending' | Pending, Completed, Failed, Refunded |
| gateway_response | TEXT | | Payment gateway response |
| card_last_four | VARCHAR(4) | | Last 4 digits of card |
| refund_date | TIMESTAMP | | Refund date if applicable |
| refund_transaction_id | VARCHAR(100) | | Refund transaction reference |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**Primary Key**: payment_id  
**Foreign Keys**: booking_id → BOOKING

---

## 2. Relationships

### 2.1 ROLE to USER
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One role can be assigned to many users; each user has one role
- **Optionality**: ROLE: Optional | USER: Optional
- **Foreign Key**: USER.role_id → ROLE.role_id
- **ERD Notation**: ROLE —|————o<— USER

### 2.2 USER to AUDIT_LOG
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One user can have many audit log entries
- **Foreign Key**: AUDIT_LOG.user_id → USER.user_id
- **ERD Notation**: USER —|————<— AUDIT_LOG

### 2.3 USER to BOOKING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One user can make many bookings
- **Foreign Key**: BOOKING.user_id → USER.user_id
- **ERD Notation**: USER —|————o<— BOOKING

### 2.4 GENRE to SHOW
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: Many shows can belong to one genre
- **Foreign Key**: SHOW.genre_id → GENRE.genre_id
- **ERD Notation**: GENRE —|————o<— SHOW

### 2.5 SHOW to PERFORMANCE
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One show can have many performances
- **Foreign Key**: PERFORMANCE.show_id → SHOW.show_id
- **ERD Notation**: SHOW —|————o<— PERFORMANCE

### 2.6 VENUE to PERFORMANCE
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One venue can host many performances
- **Foreign Key**: PERFORMANCE.venue_id → VENUE.venue_id
- **ERD Notation**: VENUE —|————o<— PERFORMANCE

### 2.7 VENUE to SEAT
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One venue has many seats
- **Foreign Key**: SEAT.venue_id → VENUE.venue_id
- **ERD Notation**: VENUE —|————<— SEAT

### 2.8 PERFORMANCE to BOOKING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One performance can have many bookings
- **Foreign Key**: BOOKING.performance_id → PERFORMANCE.performance_id
- **ERD Notation**: PERFORMANCE —|————o<— BOOKING

### 2.9 PERFORMANCE to PERFORMANCE_PRICING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One performance has multiple pricing tiers
- **Foreign Key**: PERFORMANCE_PRICING.performance_id → PERFORMANCE.performance_id
- **ERD Notation**: PERFORMANCE —|————<— PERFORMANCE_PRICING

### 2.10 BOOKING to BOOKING_DETAIL
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One booking contains many seat details
- **Foreign Key**: BOOKING_DETAIL.booking_id → BOOKING.booking_id
- **ERD Notation**: BOOKING —|————<— BOOKING_DETAIL

### 2.11 SEAT to BOOKING_DETAIL
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One seat can appear in many booking details
- **Foreign Key**: BOOKING_DETAIL.seat_id → SEAT.seat_id
- **ERD Notation**: SEAT —|————o<— BOOKING_DETAIL

### 2.12 BOOKING to PAYMENT
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One booking can have multiple payment attempts
- **Foreign Key**: PAYMENT.booking_id → BOOKING.booking_id
- **ERD Notation**: BOOKING —|————o<— PAYMENT

---

## 3. ERD Summary Diagram (Text Representation)

```
┌─────────────┐
│    ROLE     │
│  (PK: id)   │
└──────┬──────┘
       │ 1:N
       ▼
┌─────────────┐         ┌─────────────┐
│    USER     │────1:N──►│  AUDIT_LOG  │
│  (PK: id)   │         │  (PK: id)   │
└──────┬──────┘         └─────────────┘
       │ 1:N
       ▼
┌─────────────┐
│   BOOKING   │────1:N────┐
│  (PK: id)   │           │
└──────┬──────┘           ▼
       │ 1:N       ┌─────────────┐
       │           │   PAYMENT   │
       ▼           │  (PK: id)   │
┌───────────────┐  └─────────────┘
│BOOKING_DETAIL │
│   (PK: id)    │
└───────┬───────┘
        │ N:1
        ▼
┌─────────────┐         ┌─────────────┐
│    SEAT     │◄───N:1──│    VENUE    │
│  (PK: id)   │         │  (PK: id)   │
└─────────────┘         └──────┬──────┘
                               │ 1:N
┌─────────────┐                ▼
│   GENRE     │         ┌─────────────────┐
│  (PK: id)   │         │  PERFORMANCE    │◄──N:1──┐
└──────┬──────┘         │   (PK: id)      │        │
       │ 1:N            └────────┬────────┘        │
       ▼                         │ 1:N             │
┌─────────────┐                  ▼                 │
│    SHOW     │──────────►┌───────────────────┐   │
│  (PK: id)   │   1:N     │ PERFORMANCE_      │   │
└─────────────┘           │   PRICING         │   │
                          │   (PK: id)        │   │
                          └───────────────────┘   │
                                                  │
                          ┌──────────────────────┘
                          │
                   ┌──────┴──────┐
                   │   BOOKING   │
                   │  (PK: id)   │
                   └─────────────┘
```

---

## 4. Business Rules Reflected in ERD

1. **Unique User Email**: Each user must have a unique email address
2. **Role-Based Access Control (RBAC)**: Users can be assigned roles with granular permissions
3. **Audit Trail**: All administrative actions are logged in AUDIT_LOG
4. **Show-Performance Relationship**: A show can be performed multiple times
5. **Venue-Seat Relationship**: Seats are permanently associated with venues
6. **Performance Capacity**: Total seats determined by venue's seat count
7. **Booking-Seat Association**: Each booking can include multiple seats
8. **Seat Uniqueness per Performance**: A seat can only be booked once per performance
9. **Dynamic Pricing**: Prices can vary by performance through PERFORMANCE_PRICING
10. **Payment Tracking**: Multiple payment attempts tracked for retries and refunds
11. **Payment Deadline**: Bookings have a 15-minute payment deadline
12. **Booking Reference**: Each booking has a unique alphanumeric reference

---

## 5. Additional Constraints and Indexes

### 5.1 Unique Constraints
- USER.email
- ROLE.role_name
- GENRE.genre_name
- BOOKING.booking_reference
- SEAT_CATEGORY_PRICING.category_name
- SEAT(venue_id, row_number, seat_number)
- PERFORMANCE_PRICING(performance_id, seat_category)
- BOOKING_DETAIL(booking_id, seat_id)

### 5.2 Check Constraints
- USER.account_status IN ('Active', 'Suspended', 'Deactivated')
- SHOW.show_status IN ('Active', 'Coming Soon', 'Archived')
- PERFORMANCE.performance_status IN ('Scheduled', 'Ongoing', 'Completed', 'Cancelled')
- BOOKING.booking_status IN ('Pending', 'Confirmed', 'Cancelled', 'Expired')
- PAYMENT.payment_status IN ('Pending', 'Completed', 'Failed', 'Refunded')

### 5.3 Recommended Indexes
- USER(email), USER(role_id)
- AUDIT_LOG(user_id), AUDIT_LOG(timestamp)
- BOOKING(user_id), BOOKING(performance_id), BOOKING(booking_reference)
- BOOKING_DETAIL(booking_id), BOOKING_DETAIL(seat_id)
- PERFORMANCE(show_id, performance_date), PERFORMANCE(venue_id, performance_date)
- PAYMENT(booking_id), SEAT(venue_id)

---

## 6. Entity Count Summary

| Entity | Description | Key Relationships |
|--------|-------------|-------------------|
| ROLE | User roles with permissions | 1:N with USER |
| USER | Registered customers | 1:N with BOOKING, AUDIT_LOG |
| AUDIT_LOG | Action audit trail | N:1 with USER |
| GENRE | Show categories | 1:N with SHOW |
| SHOW | Theatre productions | 1:N with PERFORMANCE |
| VENUE | Physical locations | 1:N with SEAT, PERFORMANCE |
| SEAT | Individual seats | 1:N with BOOKING_DETAIL |
| SEAT_CATEGORY_PRICING | Base pricing | Reference table |
| PERFORMANCE | Scheduled instances | 1:N with BOOKING, PRICING |
| PERFORMANCE_PRICING | Dynamic pricing | N:1 with PERFORMANCE |
| BOOKING | Customer reservations | 1:N with BOOKING_DETAIL, PAYMENT |
| BOOKING_DETAIL | Seat assignments | N:1 with BOOKING, SEAT |
| PAYMENT | Financial transactions | N:1 with BOOKING |

**Total Entities**: 13

---

## Document Control
- **Version**: 2.0
- **Date**: November 27, 2025
- **Database**: MySQL 8.0
- **ORM**: SQLAlchemy
- **Compliance**: Oracle ERDish / Crow's Foot Notation
- **Purpose**: Academic Database Design - Conceptual Model
