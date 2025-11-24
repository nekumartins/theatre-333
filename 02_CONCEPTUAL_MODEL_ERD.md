# Online Theatre Booking System - Conceptual Data Model (ERD)

## Entity-Relationship Diagram Specification
**Notation**: Oracle ERDish (Crow's Foot notation)  
**Tool Compatibility**: Visio, Draw.io, Lucidchart

---

## 1. Entities and Attributes

### 1.1 USER
**Definition**: Registered customer who can browse shows and make bookings.

**Attributes**:
- **user_id** (PK): Unique identifier for each user
- first_name: User's first name
- last_name: User's last name
- email: User's email address (unique)
- phone: Contact phone number
- password_hash: Encrypted password
- date_of_birth: User's date of birth
- address_line1: Primary address
- address_line2: Secondary address (optional)
- city: City of residence
- postal_code: Postal/ZIP code
- country: Country of residence
- registration_date: Date user registered
- email_verified: Boolean flag for email verification
- account_status: Status (Active, Suspended, Deleted)
- created_at: Timestamp of account creation
- updated_at: Timestamp of last update

**Primary Key**: user_id

---

### 1.2 SHOW
**Definition**: A theatrical production or performance title that can be scheduled multiple times.

**Attributes**:
- **show_id** (PK): Unique identifier for each show
- title: Name of the show
- description: Detailed description of the show
- genre_id: Foreign key to GENRE
- duration_minutes: Length of show in minutes
- language: Language of performance
- age_rating: Minimum age requirement
- poster_url: URL to promotional poster image
- producer: Name of producer
- director: Name of director
- show_status: Status (Active, Coming Soon, Archived)
- created_at: Timestamp of creation
- updated_at: Timestamp of last update

**Primary Key**: show_id  
**Foreign Keys**: genre_id → GENRE

---

### 1.3 GENRE
**Definition**: Category or type of theatrical performance.

**Attributes**:
- **genre_id** (PK): Unique identifier for each genre
- genre_name: Name of the genre (e.g., Drama, Comedy, Musical)
- description: Description of the genre

**Primary Key**: genre_id

---

### 1.4 VENUE
**Definition**: Physical location where performances take place.

**Attributes**:
- **venue_id** (PK): Unique identifier for each venue
- venue_name: Name of the theatre/venue
- address_line1: Primary address
- address_line2: Secondary address (optional)
- city: City location
- postal_code: Postal/ZIP code
- country: Country
- total_capacity: Maximum seating capacity
- phone: Contact phone number
- facilities: Description of facilities (parking, accessibility, etc.)
- created_at: Timestamp of creation
- updated_at: Timestamp of last update

**Primary Key**: venue_id

---

### 1.5 SEAT
**Definition**: Individual seat in a venue with specific location and category.

**Attributes**:
- **seat_id** (PK): Unique identifier for each seat
- venue_id: Foreign key to VENUE
- row_number: Row identifier (e.g., A, B, C, 1, 2, 3)
- seat_number: Seat number within the row
- section: Section of venue (e.g., Orchestra, Balcony, Mezzanine)
- seat_category: Category (VIP, Premium, Standard)
- is_accessible: Boolean for wheelchair accessibility
- is_active: Boolean for seat availability (can be deactivated)
- created_at: Timestamp of creation

**Primary Key**: seat_id  
**Foreign Keys**: venue_id → VENUE  
**Composite Unique Key**: (venue_id, row_number, seat_number)

---

### 1.6 SEAT_CATEGORY_PRICING
**Definition**: Base pricing information for different seat categories.

**Attributes**:
- **category_id** (PK): Unique identifier for pricing category
- category_name: Name (VIP, Premium, Standard, Economy)
- base_price: Default price for this category
- description: Description of category features

**Primary Key**: category_id

---

### 1.7 PERFORMANCE
**Definition**: A specific scheduled instance of a show at a venue on a particular date and time.

**Attributes**:
- **performance_id** (PK): Unique identifier for each performance
- show_id: Foreign key to SHOW
- venue_id: Foreign key to VENUE
- performance_date: Date of performance
- start_time: Start time of performance
- end_time: Expected end time
- total_seats: Total seats available
- available_seats: Current number of available seats
- performance_status: Status (Scheduled, Ongoing, Completed, Cancelled)
- special_notes: Additional information (e.g., "Live orchestra")
- created_at: Timestamp of creation
- updated_at: Timestamp of last update

**Primary Key**: performance_id  
**Foreign Keys**: 
- show_id → SHOW
- venue_id → VENUE

---

### 1.8 PERFORMANCE_PRICING
**Definition**: Dynamic pricing for seat categories specific to each performance.

**Attributes**:
- **pricing_id** (PK): Unique identifier for pricing rule
- performance_id: Foreign key to PERFORMANCE
- seat_category: Category name (VIP, Premium, Standard)
- price: Price for this category in this performance
- created_at: Timestamp of creation

**Primary Key**: pricing_id  
**Foreign Keys**: performance_id → PERFORMANCE  
**Composite Unique Key**: (performance_id, seat_category)

---

### 1.9 BOOKING
**Definition**: A customer's reservation for one or more seats at a specific performance.

**Attributes**:
- **booking_id** (PK): Unique identifier for each booking
- user_id: Foreign key to USER
- performance_id: Foreign key to PERFORMANCE
- booking_reference: Unique alphanumeric reference code
- booking_date: Timestamp when booking was created
- total_amount: Total price for all seats
- booking_status: Status (Pending, Confirmed, Cancelled, Expired)
- cancellation_date: Date of cancellation (if applicable)
- refund_amount: Amount refunded (if applicable)
- created_at: Timestamp of creation
- updated_at: Timestamp of last update

**Primary Key**: booking_id  
**Foreign Keys**: 
- user_id → USER
- performance_id → PERFORMANCE  
**Unique Key**: booking_reference

---

### 1.10 BOOKING_DETAIL
**Definition**: Individual seat assignments within a booking.

**Attributes**:
- **booking_detail_id** (PK): Unique identifier for each booking detail
- booking_id: Foreign key to BOOKING
- seat_id: Foreign key to SEAT
- seat_price: Price paid for this seat
- row_number: Row of the seat (denormalized for reporting)
- seat_number: Seat number (denormalized for reporting)
- seat_category: Category (denormalized for reporting)

**Primary Key**: booking_detail_id  
**Foreign Keys**: 
- booking_id → BOOKING
- seat_id → SEAT  
**Composite Unique Key**: (booking_id, seat_id)  
*Note: A seat can appear in multiple bookings but only once per performance (enforced by business logic)*

---

### 1.11 PAYMENT
**Definition**: Financial transaction record for a booking.

**Attributes**:
- **payment_id** (PK): Unique identifier for each payment
- booking_id: Foreign key to BOOKING
- payment_amount: Amount paid
- payment_method: Method (Credit Card, Debit Card, Digital Wallet)
- payment_date: Timestamp of payment
- transaction_id: External payment gateway transaction reference
- payment_status: Status (Pending, Completed, Failed, Refunded)
- gateway_response: Response message from payment gateway
- card_last_four: Last 4 digits of card (if applicable)
- refund_date: Date of refund (if applicable)
- refund_transaction_id: Refund transaction reference
- created_at: Timestamp of creation

**Primary Key**: payment_id  
**Foreign Keys**: booking_id → BOOKING

---

## 2. Relationships

### 2.1 USER to BOOKING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One user can make many bookings; each booking belongs to one user
- **Optionality**: 
  - USER: Optional (user may exist without bookings)
  - BOOKING: Mandatory (every booking must have a user)
- **Foreign Key**: BOOKING.user_id → USER.user_id
- **ERD Notation**: USER —|————<— BOOKING

---

### 2.2 SHOW to GENRE
- **Relationship Type**: Many-to-One
- **Cardinality**: N:1
- **Description**: Many shows can belong to one genre; each show has one genre
- **Optionality**: 
  - SHOW: Mandatory (every show must have a genre)
  - GENRE: Optional (genre can exist without shows)
- **Foreign Key**: SHOW.genre_id → GENRE.genre_id
- **ERD Notation**: SHOW >————|— GENRE

---

### 2.3 SHOW to PERFORMANCE
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One show can have many performances; each performance is of one show
- **Optionality**: 
  - SHOW: Optional (show can exist without scheduled performances)
  - PERFORMANCE: Mandatory (every performance must be associated with a show)
- **Foreign Key**: PERFORMANCE.show_id → SHOW.show_id
- **ERD Notation**: SHOW —|————<— PERFORMANCE

---

### 2.4 VENUE to PERFORMANCE
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One venue can host many performances; each performance is at one venue
- **Optionality**: 
  - VENUE: Optional (venue can exist without scheduled performances)
  - PERFORMANCE: Mandatory (every performance must have a venue)
- **Foreign Key**: PERFORMANCE.venue_id → VENUE.venue_id
- **ERD Notation**: VENUE —|————<— PERFORMANCE

---

### 2.5 VENUE to SEAT
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One venue has many seats; each seat belongs to one venue
- **Optionality**: 
  - VENUE: Mandatory (venue must have at least one seat)
  - SEAT: Mandatory (every seat must belong to a venue)
- **Foreign Key**: SEAT.venue_id → VENUE.venue_id
- **ERD Notation**: VENUE —|————<— SEAT

---

### 2.6 PERFORMANCE to BOOKING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One performance can have many bookings; each booking is for one performance
- **Optionality**: 
  - PERFORMANCE: Optional (performance can exist without bookings)
  - BOOKING: Mandatory (every booking must be for a performance)
- **Foreign Key**: BOOKING.performance_id → PERFORMANCE.performance_id
- **ERD Notation**: PERFORMANCE —|————<— BOOKING

---

### 2.7 PERFORMANCE to PERFORMANCE_PRICING
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One performance has multiple pricing tiers; each pricing rule is for one performance
- **Optionality**: 
  - PERFORMANCE: Mandatory (must have at least one pricing tier)
  - PERFORMANCE_PRICING: Mandatory (every pricing rule must belong to a performance)
- **Foreign Key**: PERFORMANCE_PRICING.performance_id → PERFORMANCE.performance_id
- **ERD Notation**: PERFORMANCE —|————<— PERFORMANCE_PRICING

---

### 2.8 BOOKING to BOOKING_DETAIL
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One booking contains many booking details (seats); each detail belongs to one booking
- **Optionality**: 
  - BOOKING: Mandatory (booking must have at least one seat)
  - BOOKING_DETAIL: Mandatory (every booking detail must belong to a booking)
- **Foreign Key**: BOOKING_DETAIL.booking_id → BOOKING.booking_id
- **ERD Notation**: BOOKING —|————<— BOOKING_DETAIL

---

### 2.9 SEAT to BOOKING_DETAIL
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One seat can appear in many booking details (different performances); each detail references one seat
- **Optionality**: 
  - SEAT: Optional (seat can exist without bookings)
  - BOOKING_DETAIL: Mandatory (every booking detail must reference a seat)
- **Foreign Key**: BOOKING_DETAIL.seat_id → SEAT.seat_id
- **ERD Notation**: SEAT —|————<— BOOKING_DETAIL

---

### 2.10 BOOKING to PAYMENT
- **Relationship Type**: One-to-Many
- **Cardinality**: 1:N
- **Description**: One booking can have multiple payment attempts; each payment is for one booking
- **Optionality**: 
  - BOOKING: Optional (booking can exist with pending payment)
  - PAYMENT: Mandatory (every payment must be associated with a booking)
- **Foreign Key**: PAYMENT.booking_id → BOOKING.booking_id
- **ERD Notation**: BOOKING —|————<— PAYMENT

---

## 3. ERD Summary Diagram (Text Representation)

```
┌─────────────┐
│   GENRE     │
│  (PK: id)   │
└─────────────┘
       |
       | 1
       |
       | N
┌─────────────┐              ┌──────────────┐
│    SHOW     │              │    VENUE     │
│  (PK: id)   │              │   (PK: id)   │
└─────────────┘              └──────────────┘
       |                             |
       | 1                           | 1
       |                             |
       | N                           | N
┌─────────────────┐           ┌──────────────┐
│  PERFORMANCE    │<──N───1───│    SEAT      │
│   (PK: id)      │           │   (PK: id)   │
└─────────────────┘           └──────────────┘
       |                             |
       | 1                           | 1
       |                             |
       | N                           | N
┌───────────────────┐         ┌──────────────────┐
│ PERFORMANCE_      │         │ BOOKING_DETAIL   │
│   PRICING         │         │    (PK: id)      │
│   (PK: id)        │         └──────────────────┘
└───────────────────┘                 |
                                      | N
                                      |
                                      | 1
       ┌──────────────┐        ┌─────────────┐
       │    USER      │        │   BOOKING   │
       │  (PK: id)    │───1───>│  (PK: id)   │
       └──────────────┘    N   └─────────────┘
                                      |
                                      | 1
                                      |
                                      | N
                               ┌─────────────┐
                               │   PAYMENT   │
                               │  (PK: id)   │
                               └─────────────┘

┌──────────────────────┐
│ SEAT_CATEGORY_       │
│   PRICING            │
│   (PK: id)           │
│   (Reference table)  │
└──────────────────────┘
```

---

## 4. Business Rules Reflected in ERD

1. **Unique User Email**: Each user must have a unique email address (enforced by unique constraint)

2. **Show-Performance Relationship**: A show can be performed multiple times, but each performance is tied to exactly one show

3. **Venue-Seat Relationship**: Seats are permanently associated with venues; seat layout is venue-specific

4. **Performance Capacity**: Total seats for a performance is determined by the venue's seat count

5. **Booking-Seat Association**: Each booking can include multiple seats, but each seat in a booking is recorded separately in BOOKING_DETAIL

6. **Seat Uniqueness per Performance**: A seat can only be booked once per performance (enforced through application logic and database constraints)

7. **Dynamic Pricing**: Prices can vary by performance through PERFORMANCE_PRICING table

8. **Payment Tracking**: Multiple payment attempts are tracked for each booking (for retries and refunds)

9. **Genre Classification**: Shows are categorized by a single genre for simplicity

10. **Booking Reference**: Each booking has a unique alphanumeric reference for customer lookup

---

## 5. Additional Constraints and Indexes

### 5.1 Unique Constraints
- USER.email (unique)
- BOOKING.booking_reference (unique)
- SEAT(venue_id, row_number, seat_number) (composite unique)
- PERFORMANCE_PRICING(performance_id, seat_category) (composite unique)
- BOOKING_DETAIL(booking_id, seat_id) (composite unique)

### 5.2 Check Constraints
- USER.account_status IN ('Active', 'Suspended', 'Deleted')
- SHOW.show_status IN ('Active', 'Coming Soon', 'Archived')
- PERFORMANCE.performance_status IN ('Scheduled', 'Ongoing', 'Completed', 'Cancelled')
- BOOKING.booking_status IN ('Pending', 'Confirmed', 'Cancelled', 'Expired')
- PAYMENT.payment_status IN ('Pending', 'Completed', 'Failed', 'Refunded')
- SEAT_CATEGORY_PRICING.base_price > 0
- PERFORMANCE_PRICING.price > 0
- PERFORMANCE.total_seats >= PERFORMANCE.available_seats

### 5.3 Recommended Indexes
- INDEX on USER(email)
- INDEX on BOOKING(user_id)
- INDEX on BOOKING(performance_id)
- INDEX on BOOKING(booking_reference)
- INDEX on BOOKING_DETAIL(booking_id)
- INDEX on BOOKING_DETAIL(seat_id)
- INDEX on PERFORMANCE(show_id, performance_date)
- INDEX on PERFORMANCE(venue_id, performance_date)
- INDEX on PAYMENT(booking_id)
- INDEX on SEAT(venue_id)

---

## 6. Drawing Instructions for ERD Tools

### For Visio/Draw.io:

1. **Create Entities** as rectangles with rounded corners
2. **Label** each entity with its name at the top
3. **List attributes** inside each entity box
4. **Mark Primary Keys** with (PK) or underline
5. **Mark Foreign Keys** with (FK)
6. **Draw relationship lines** using Crow's Foot notation:
   - **One**: Single line with perpendicular bar (|)
   - **Many**: Crow's foot symbol (<)
   - **Optional**: Circle (O) on the line
   - **Mandatory**: Perpendicular bar (|) on the line

### Example Relationship Notation:
```
USER —|————<— BOOKING
     (1)    (N)
  Mandatory  Mandatory

SHOW —|————O<— PERFORMANCE
     (1)      (N)
  Optional   Mandatory
```

---

## Document Control
- **Version**: 1.0
- **Date**: November 24, 2025
- **Compliance**: Oracle ERDish / Crow's Foot Notation
- **Purpose**: Academic Database Design - Conceptual Model
