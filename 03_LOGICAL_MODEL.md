# Online Theatre Booking System - Logical Data Model

## Relational Schema with Functional Dependencies and Normalization

---

## 1. Relational Tables (Schema)

### 1.1 USER
```
USER(
    user_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    date_of_birth DATE,
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    registration_date DATE,
    email_verified BOOLEAN,
    account_status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Primary Key**: user_id  
**Unique Keys**: email  
**Data Types Justification**:
- `user_id`: INT for efficient indexing and joins
- `email`: VARCHAR(100) to accommodate long email addresses
- `password_hash`: VARCHAR(255) for bcrypt/Argon2 hashes
- `account_status`: VARCHAR(20) for enumerated values
- Timestamps for audit trail

---

### 1.2 GENRE
```
GENRE(
    genre_id INT,
    genre_name VARCHAR(50),
    description TEXT
)
```

**Primary Key**: genre_id  
**Unique Keys**: genre_name

---

### 1.3 SHOW
```
SHOW(
    show_id INT,
    title VARCHAR(200),
    description TEXT,
    genre_id INT,
    duration_minutes INT,
    language VARCHAR(50),
    age_rating VARCHAR(10),
    poster_url VARCHAR(255),
    producer VARCHAR(100),
    director VARCHAR(100),
    show_status VARCHAR(20),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Primary Key**: show_id  
**Foreign Keys**: 
- genre_id REFERENCES GENRE(genre_id)

---

### 1.4 VENUE
```
VENUE(
    venue_id INT,
    venue_name VARCHAR(100),
    address_line1 VARCHAR(100),
    address_line2 VARCHAR(100),
    city VARCHAR(50),
    postal_code VARCHAR(20),
    country VARCHAR(50),
    total_capacity INT,
    phone VARCHAR(20),
    facilities TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Primary Key**: venue_id  
**Unique Keys**: (venue_name, city) - assuming unique venue names per city

---

### 1.5 SEAT
```
SEAT(
    seat_id INT,
    venue_id INT,
    row_number VARCHAR(10),
    seat_number VARCHAR(10),
    section VARCHAR(50),
    seat_category VARCHAR(20),
    is_accessible BOOLEAN,
    is_active BOOLEAN,
    created_at TIMESTAMP
)
```

**Primary Key**: seat_id  
**Foreign Keys**: 
- venue_id REFERENCES VENUE(venue_id)  
**Unique Keys**: (venue_id, row_number, seat_number)

---

### 1.6 SEAT_CATEGORY_PRICING
```
SEAT_CATEGORY_PRICING(
    category_id INT,
    category_name VARCHAR(50),
    base_price DECIMAL(10,2),
    description TEXT
)
```

**Primary Key**: category_id  
**Unique Keys**: category_name

---

### 1.7 PERFORMANCE
```
PERFORMANCE(
    performance_id INT,
    show_id INT,
    venue_id INT,
    performance_date DATE,
    start_time TIME,
    end_time TIME,
    total_seats INT,
    available_seats INT,
    performance_status VARCHAR(20),
    special_notes TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Primary Key**: performance_id  
**Foreign Keys**: 
- show_id REFERENCES SHOW(show_id)
- venue_id REFERENCES VENUE(venue_id)

---

### 1.8 PERFORMANCE_PRICING
```
PERFORMANCE_PRICING(
    pricing_id INT,
    performance_id INT,
    seat_category VARCHAR(20),
    price DECIMAL(10,2),
    created_at TIMESTAMP
)
```

**Primary Key**: pricing_id  
**Foreign Keys**: 
- performance_id REFERENCES PERFORMANCE(performance_id)  
**Unique Keys**: (performance_id, seat_category)

---

### 1.9 BOOKING
```
BOOKING(
    booking_id INT,
    user_id INT,
    performance_id INT,
    booking_reference VARCHAR(20),
    booking_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    booking_status VARCHAR(20),
    cancellation_date TIMESTAMP,
    refund_amount DECIMAL(10,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)
```

**Primary Key**: booking_id  
**Foreign Keys**: 
- user_id REFERENCES USER(user_id)
- performance_id REFERENCES PERFORMANCE(performance_id)  
**Unique Keys**: booking_reference

---

### 1.10 BOOKING_DETAIL
```
BOOKING_DETAIL(
    booking_detail_id INT,
    booking_id INT,
    seat_id INT,
    seat_price DECIMAL(10,2),
    row_number VARCHAR(10),
    seat_number VARCHAR(10),
    seat_category VARCHAR(20)
)
```

**Primary Key**: booking_detail_id  
**Foreign Keys**: 
- booking_id REFERENCES BOOKING(booking_id)
- seat_id REFERENCES SEAT(seat_id)  
**Unique Keys**: (booking_id, seat_id)

---

### 1.11 PAYMENT
```
PAYMENT(
    payment_id INT,
    booking_id INT,
    payment_amount DECIMAL(10,2),
    payment_method VARCHAR(50),
    payment_date TIMESTAMP,
    transaction_id VARCHAR(100),
    payment_status VARCHAR(20),
    gateway_response TEXT,
    card_last_four VARCHAR(4),
    refund_date TIMESTAMP,
    refund_transaction_id VARCHAR(100),
    created_at TIMESTAMP
)
```

**Primary Key**: payment_id  
**Foreign Keys**: 
- booking_id REFERENCES BOOKING(booking_id)

---

## 2. Functional Dependencies

### 2.1 USER Table
```
FD1: user_id → first_name, last_name, email, phone, password_hash, date_of_birth, 
              address_line1, address_line2, city, postal_code, country, 
              registration_date, email_verified, account_status, created_at, updated_at

FD2: email → user_id (since email is unique)
```

**Analysis**: 
- All non-key attributes are fully functionally dependent on user_id
- No partial or transitive dependencies
- **Already in 3NF**

---

### 2.2 GENRE Table
```
FD1: genre_id → genre_name, description
FD2: genre_name → genre_id (since genre_name is unique)
```

**Analysis**: 
- Simple table with single candidate key
- **Already in 3NF**

---

### 2.3 SHOW Table
```
FD1: show_id → title, description, genre_id, duration_minutes, language, 
              age_rating, poster_url, producer, director, show_status, 
              created_at, updated_at

FD2: genre_id → genre_name, description (from GENRE table)
```

**Analysis**: 
- All attributes depend on show_id
- genre_id is a foreign key, no transitive dependency stored locally
- **Already in 3NF**

---

### 2.4 VENUE Table
```
FD1: venue_id → venue_name, address_line1, address_line2, city, postal_code, 
               country, total_capacity, phone, facilities, created_at, updated_at

FD2: (venue_name, city) → venue_id (composite unique key)
```

**Analysis**: 
- All attributes depend on venue_id
- No transitive dependencies
- **Already in 3NF**

---

### 2.5 SEAT Table
```
FD1: seat_id → venue_id, row_number, seat_number, section, seat_category, 
              is_accessible, is_active, created_at

FD2: (venue_id, row_number, seat_number) → seat_id
```

**Analysis**: 
- seat_id is the primary key
- Composite key (venue_id, row_number, seat_number) also uniquely identifies seats
- seat_category is descriptive attribute, not causing transitive dependency
- **Already in 3NF**

---

### 2.6 SEAT_CATEGORY_PRICING Table
```
FD1: category_id → category_name, base_price, description
FD2: category_name → category_id
```

**Analysis**: 
- Reference table for pricing categories
- **Already in 3NF**

---

### 2.7 PERFORMANCE Table
```
FD1: performance_id → show_id, venue_id, performance_date, start_time, end_time, 
                     total_seats, available_seats, performance_status, 
                     special_notes, created_at, updated_at

FD2: show_id → title, genre_id, duration_minutes... (from SHOW)
FD3: venue_id → venue_name, capacity... (from VENUE)
```

**Analysis**: 
- All attributes depend on performance_id
- Foreign keys reference other tables without storing redundant data
- total_seats is derived from venue but stored for performance-specific capacity
- **Already in 3NF**

---

### 2.8 PERFORMANCE_PRICING Table
```
FD1: pricing_id → performance_id, seat_category, price, created_at
FD2: (performance_id, seat_category) → pricing_id, price
```

**Analysis**: 
- Enables dynamic pricing per performance
- Composite unique key (performance_id, seat_category)
- **Already in 3NF**

---

### 2.9 BOOKING Table
```
FD1: booking_id → user_id, performance_id, booking_reference, booking_date, 
                 total_amount, booking_status, cancellation_date, 
                 refund_amount, created_at, updated_at

FD2: booking_reference → booking_id (unique reference)
```

**Analysis**: 
- All attributes depend on booking_id
- No transitive dependencies
- **Already in 3NF**

---

### 2.10 BOOKING_DETAIL Table
```
FD1: booking_detail_id → booking_id, seat_id, seat_price, row_number, 
                        seat_number, seat_category

FD2: (booking_id, seat_id) → booking_detail_id, seat_price

FD3: seat_id → venue_id, row_number, seat_number, seat_category (from SEAT)
```

**Analysis**: 
- **Denormalization Discussion**: row_number, seat_number, and seat_category are denormalized for reporting efficiency
- These attributes are functionally dependent on seat_id (from SEAT table)
- **Justification**: Storing these values prevents JOIN operations in reporting queries
- Trade-off: Slight redundancy for significant performance gain
- **Modified 3NF with intentional denormalization for optimization**

**Alternative (Strict 3NF)**:
If we remove denormalized fields:
```
BOOKING_DETAIL(
    booking_detail_id,
    booking_id,
    seat_id,
    seat_price
)
```
This would be in strict 3NF, but requires JOIN with SEAT for every booking detail query.

**Recommendation**: Keep denormalized version for practical applications.

---

### 2.11 PAYMENT Table
```
FD1: payment_id → booking_id, payment_amount, payment_method, payment_date, 
                 transaction_id, payment_status, gateway_response, 
                 card_last_four, refund_date, refund_transaction_id, created_at
```

**Analysis**: 
- All attributes depend on payment_id
- Multiple payment records can exist per booking (for retries/refunds)
- **Already in 3NF**

---

## 3. Normalization Process

### 3.1 First Normal Form (1NF)
**Requirement**: All attributes must contain atomic values; no repeating groups.

**Verification**:
- ✅ USER: All attributes are atomic (no multi-valued attributes)
- ✅ SHOW: All attributes are atomic
- ✅ BOOKING: All attributes are atomic
- ✅ BOOKING_DETAIL: Separate table created to eliminate repeating groups of seats in a booking
- ✅ PAYMENT: Separate table for multiple payment attempts

**Conclusion**: All tables are in 1NF.

---

### 3.2 Second Normal Form (2NF)
**Requirement**: Must be in 1NF and no partial dependencies (all non-key attributes must depend on the entire primary key, relevant for composite keys).

**Analysis**:

**Tables with Single-Attribute Primary Keys**:
- USER, GENRE, SHOW, VENUE, SEAT, PERFORMANCE, BOOKING, PAYMENT, BOOKING_DETAIL, PERFORMANCE_PRICING
- No partial dependencies possible (single-attribute PK)
- ✅ All satisfy 2NF

**Tables with Composite Unique Keys** (alternative keys):
- SEAT (venue_id, row_number, seat_number) → all other attributes
  - No partial dependency; all attributes depend on entire composite key
  - ✅ Satisfies 2NF

**Conclusion**: All tables are in 2NF.

---

### 3.3 Third Normal Form (3NF)
**Requirement**: Must be in 2NF and no transitive dependencies (non-key attributes should not depend on other non-key attributes).

**Analysis**:

**USER Table**:
- No transitive dependencies
- city → postal_code? No, multiple cities can have overlapping postal codes in different countries
- ✅ 3NF

**SHOW Table**:
- genre_id is a foreign key; genre details are stored in GENRE table
- No genre information duplicated in SHOW
- ✅ 3NF

**VENUE Table**:
- city → country? Possibly, but we store both for clarity and flexibility
- Not a strict dependency (some city names exist in multiple countries)
- ✅ 3NF

**SEAT Table**:
- seat_category is descriptive, not causing transitive dependency
- venue_id → total_capacity is stored in VENUE, not SEAT
- ✅ 3NF

**PERFORMANCE Table**:
- show_id → show details stored in SHOW table
- venue_id → venue details stored in VENUE table
- No transitive dependencies within PERFORMANCE
- ✅ 3NF

**BOOKING_DETAIL Table**:
- **Intentional Denormalization**: row_number, seat_number, seat_category depend on seat_id
- Stored redundantly for query performance
- **Trade-off Accepted**: Slight deviation from strict 3NF for practical benefits
- ⚠️ Modified 3NF (with justification)

**All Other Tables**:
- ✅ No transitive dependencies detected
- ✅ 3NF

**Conclusion**: All tables are in 3NF (with one intentional denormalization in BOOKING_DETAIL for performance optimization).

---

## 4. Normalization Summary

| Table                  | 1NF | 2NF | 3NF | Notes                                      |
|------------------------|-----|-----|-----|--------------------------------------------|
| USER                   | ✅  | ✅  | ✅  | Fully normalized                           |
| GENRE                  | ✅  | ✅  | ✅  | Fully normalized                           |
| SHOW                   | ✅  | ✅  | ✅  | Fully normalized                           |
| VENUE                  | ✅  | ✅  | ✅  | Fully normalized                           |
| SEAT                   | ✅  | ✅  | ✅  | Fully normalized                           |
| SEAT_CATEGORY_PRICING  | ✅  | ✅  | ✅  | Fully normalized                           |
| PERFORMANCE            | ✅  | ✅  | ✅  | Fully normalized                           |
| PERFORMANCE_PRICING    | ✅  | ✅  | ✅  | Fully normalized                           |
| BOOKING                | ✅  | ✅  | ✅  | Fully normalized                           |
| BOOKING_DETAIL         | ✅  | ✅  | ⚠️  | Denormalized for performance (acceptable)  |
| PAYMENT                | ✅  | ✅  | ✅  | Fully normalized                           |

---

## 5. Referential Integrity Constraints

### 5.1 Foreign Key Constraints

```
SHOW.genre_id → GENRE.genre_id
    ON DELETE RESTRICT (cannot delete genre if shows exist)
    ON UPDATE CASCADE

SEAT.venue_id → VENUE.venue_id
    ON DELETE RESTRICT (cannot delete venue if seats exist)
    ON UPDATE CASCADE

PERFORMANCE.show_id → SHOW.show_id
    ON DELETE RESTRICT (cannot delete show if performances exist)
    ON UPDATE CASCADE

PERFORMANCE.venue_id → VENUE.venue_id
    ON DELETE RESTRICT (cannot delete venue if performances scheduled)
    ON UPDATE CASCADE

PERFORMANCE_PRICING.performance_id → PERFORMANCE.performance_id
    ON DELETE CASCADE (delete pricing when performance is deleted)
    ON UPDATE CASCADE

BOOKING.user_id → USER.user_id
    ON DELETE RESTRICT (cannot delete user with bookings)
    ON UPDATE CASCADE

BOOKING.performance_id → PERFORMANCE.performance_id
    ON DELETE RESTRICT (cannot delete performance with bookings)
    ON UPDATE CASCADE

BOOKING_DETAIL.booking_id → BOOKING.booking_id
    ON DELETE CASCADE (delete booking details when booking is deleted)
    ON UPDATE CASCADE

BOOKING_DETAIL.seat_id → SEAT.seat_id
    ON DELETE RESTRICT (cannot delete seat if in booking)
    ON UPDATE CASCADE

PAYMENT.booking_id → BOOKING.booking_id
    ON DELETE RESTRICT (cannot delete booking with payment records)
    ON UPDATE CASCADE
```

---

## 6. Business Logic and Constraints

### 6.1 Domain Constraints
```sql
-- USER
CHECK (email LIKE '%@%')
CHECK (account_status IN ('Active', 'Suspended', 'Deleted'))

-- SHOW
CHECK (duration_minutes > 0)
CHECK (show_status IN ('Active', 'Coming Soon', 'Archived'))

-- VENUE
CHECK (total_capacity > 0)

-- SEAT
CHECK (seat_category IN ('VIP', 'Premium', 'Standard', 'Economy', 'Balcony'))

-- PERFORMANCE
CHECK (performance_date >= CURRENT_DATE)
CHECK (total_seats >= available_seats)
CHECK (available_seats >= 0)
CHECK (performance_status IN ('Scheduled', 'Ongoing', 'Completed', 'Cancelled'))

-- PERFORMANCE_PRICING
CHECK (price > 0)

-- BOOKING
CHECK (total_amount >= 0)
CHECK (booking_status IN ('Pending', 'Confirmed', 'Cancelled', 'Expired'))
CHECK (refund_amount <= total_amount)

-- PAYMENT
CHECK (payment_amount > 0)
CHECK (payment_status IN ('Pending', 'Completed', 'Failed', 'Refunded'))
```

### 6.2 Complex Business Rules (Enforced via Triggers/Application Logic)

1. **Seat Availability**: 
   - A seat can only be booked once per performance
   - Requires checking existing BOOKING_DETAIL records for the same (seat_id, performance_id)

2. **Booking Expiration**:
   - Bookings with status 'Pending' must be paid within 15 minutes
   - Trigger/scheduled job to update status to 'Expired' and release seats

3. **Available Seats Update**:
   - When booking is confirmed, decrement PERFORMANCE.available_seats
   - When booking is cancelled, increment PERFORMANCE.available_seats

4. **Payment-Booking Status Sync**:
   - When PAYMENT.payment_status = 'Completed', update BOOKING.booking_status = 'Confirmed'

5. **Cancellation Policy**:
   - Bookings can only be cancelled if performance_date - CURRENT_DATE >= 1

---

## 7. Query Optimization Considerations

### 7.1 Recommended Indexes

```sql
-- USER
CREATE INDEX idx_user_email ON USER(email);
CREATE INDEX idx_user_account_status ON USER(account_status);

-- SHOW
CREATE INDEX idx_show_genre ON SHOW(genre_id);
CREATE INDEX idx_show_status ON SHOW(show_status);

-- SEAT
CREATE INDEX idx_seat_venue ON SEAT(venue_id);
CREATE INDEX idx_seat_category ON SEAT(seat_category);

-- PERFORMANCE
CREATE INDEX idx_performance_show ON PERFORMANCE(show_id);
CREATE INDEX idx_performance_venue ON PERFORMANCE(venue_id);
CREATE INDEX idx_performance_date ON PERFORMANCE(performance_date);
CREATE INDEX idx_performance_status ON PERFORMANCE(performance_status);
CREATE COMPOSITE INDEX idx_perf_show_date ON PERFORMANCE(show_id, performance_date);

-- BOOKING
CREATE INDEX idx_booking_user ON BOOKING(user_id);
CREATE INDEX idx_booking_performance ON BOOKING(performance_id);
CREATE INDEX idx_booking_reference ON BOOKING(booking_reference);
CREATE INDEX idx_booking_status ON BOOKING(booking_status);
CREATE INDEX idx_booking_date ON BOOKING(booking_date);

-- BOOKING_DETAIL
CREATE INDEX idx_booking_detail_booking ON BOOKING_DETAIL(booking_id);
CREATE INDEX idx_booking_detail_seat ON BOOKING_DETAIL(seat_id);

-- PAYMENT
CREATE INDEX idx_payment_booking ON PAYMENT(booking_id);
CREATE INDEX idx_payment_status ON PAYMENT(payment_status);
CREATE INDEX idx_payment_date ON PAYMENT(payment_date);
```

---

## Document Control
- **Version**: 1.0
- **Date**: November 24, 2025
- **Normalization Level**: 3NF (with one documented denormalization)
- **Purpose**: Academic Database Design - Logical Model
