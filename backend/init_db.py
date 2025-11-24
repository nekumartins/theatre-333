"""
Database initialization script for Theatre Booking System
Creates tables and populates sample data
"""
from app.database import engine, Base, SessionLocal
from app.models import Genre, User, Show, Venue, Seat, Performance, SeatCategoryPricing, PerformancePricing, Booking, BookingDetail, Payment
from app.auth import get_password_hash
from datetime import date, time, datetime, timedelta
from decimal import Decimal

def hash_password(password: str) -> str:
    """Hash password using passlib (consistent with auth.py)"""
    return get_password_hash(password)

def init_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")
    
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Genre).count() > 0:
            print("Database already populated. Skipping data insertion.")
            return
        
        print("\nPopulating sample data...")
        
        # 1. Insert Genres
        print("→ Inserting genres...")
        genres = [
            Genre(genre_name="Drama", description="Serious narrative performances"),
            Genre(genre_name="Comedy", description="Light-hearted and humorous shows"),
            Genre(genre_name="Musical", description="Shows featuring songs and dance"),
            Genre(genre_name="Thriller", description="Suspenseful and intense performances"),
            Genre(genre_name="Classic", description="Timeless theatrical masterpieces")
        ]
        db.add_all(genres)
        db.flush()
        
        # 2. Insert Users
        print("→ Inserting users...")
        today_date = date.today()
        users = [
            User(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone="+1234567890",
                password_hash=hash_password("password123"),
                registration_date=today_date,
                account_status="Active"
            ),
            User(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="+1234567891",
                password_hash=hash_password("password123"),
                registration_date=today_date,
                account_status="Active"
            ),
            User(
                first_name="Admin",
                last_name="User",
                email="admin@theatre.com",
                phone="+1234567892",
                password_hash=hash_password("password123"),
                registration_date=today_date,
                account_status="Active"
            )
        ]
        db.add_all(users)
        db.flush()
        
        # 3. Insert Venue
        print("→ Inserting venue...")
        venue = Venue(
            venue_name="Grand Theatre",
            address_line1="123 Theatre Street",
            city="London",
            postal_code="SW1A 1AA",
            country="United Kingdom",
            total_capacity=500
        )
        db.add(venue)
        db.flush()
        
        # 4. Insert Shows
        print("→ Inserting shows...")
        shows = [
            Show(
                title="Hamlet",
                description="Shakespeare's tragic masterpiece about revenge and madness",
                genre_id=genres[0].genre_id,  # Drama
                duration_minutes=180,
                show_status="Active",
                poster_url="https://example.com/hamlet.jpg"
            ),
            Show(
                title="Les Misérables",
                description="Epic musical about love, sacrifice, and redemption",
                genre_id=genres[2].genre_id,  # Musical
                duration_minutes=165,
                show_status="Active",
                poster_url="https://example.com/lesmis.jpg"
            ),
            Show(
                title="The Comedy of Errors",
                description="Shakespeare's hilarious tale of mistaken identity",
                genre_id=genres[1].genre_id,  # Comedy
                duration_minutes=120,
                show_status="Active",
                poster_url="https://example.com/comedy.jpg"
            ),
            Show(
                title="Macbeth",
                description="Dark tragedy of ambition and murder",
                genre_id=genres[3].genre_id,  # Thriller
                duration_minutes=150,
                show_status="Active",
                poster_url="https://example.com/macbeth.jpg"
            )
        ]
        db.add_all(shows)
        db.flush()
        
        # 5. Insert Seats (Grand Theatre layout: 20 rows, 25 seats per row)
        print("→ Inserting seats (this may take a moment)...")
        seats = []
        seat_categories = [
            ("VIP", "A", "B", 30),           # Rows A-B: VIP (30 seats)
            ("Premium", "C", "E", 75),       # Rows C-E: Premium (75 seats)
            ("Standard", "F", "L", 160),     # Rows F-L: Standard (160 seats)
            ("Economy", "M", "T", 235)       # Rows M-T: Economy (235 seats)
        ]
        
        seat_id_counter = 1
        for category, start_row, end_row, total_in_category in seat_categories:
            rows = [chr(i) for i in range(ord(start_row), ord(end_row) + 1)]
            seats_per_row = total_in_category // len(rows)
            
            for row in rows:
                for seat_num in range(1, seats_per_row + 1):
                    seats.append(Seat(
                        seat_id=seat_id_counter,
                        venue_id=venue.venue_id,
                        row_number=row,
                        seat_number=str(seat_num),
                        section="Main Hall",
                        seat_category=category,
                        is_accessible=(seat_num <= 2),  # First 2 seats per row accessible
                        is_active=True
                    ))
                    seat_id_counter += 1
        
        db.add_all(seats)
        db.flush()
        print(f"  ✓ Created {len(seats)} seats")
        
        # 6. Insert Performances
        print("→ Inserting performances...")
        today = date.today()
        performances = [
            # Hamlet performances
            Performance(
                show_id=shows[0].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=7),
                start_time=time(19, 30),
                total_seats=500,
                available_seats=500,
                performance_status="Scheduled"
            ),
            Performance(
                show_id=shows[0].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=8),
                start_time=time(19, 30),
                total_seats=500,
                available_seats=500,
                performance_status="Scheduled"
            ),
            # Les Misérables performances
            Performance(
                show_id=shows[1].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=14),
                start_time=time(19, 0),
                total_seats=500,
                available_seats=500,
                performance_status="Scheduled"
            ),
            Performance(
                show_id=shows[1].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=15),
                start_time=time(14, 0),
                total_seats=500,
                available_seats=498,  # 2 seats booked
                performance_status="Scheduled"
            ),
            # Comedy of Errors
            Performance(
                show_id=shows[2].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=21),
                start_time=time(20, 0),
                total_seats=500,
                available_seats=500,
                performance_status="Scheduled"
            ),
            # Macbeth performances
            Performance(
                show_id=shows[3].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=28),
                start_time=time(19, 30),
                total_seats=500,
                available_seats=500,
                performance_status="Scheduled"
            ),
            Performance(
                show_id=shows[3].show_id,
                venue_id=venue.venue_id,
                performance_date=today + timedelta(days=29),
                start_time=time(19, 30),
                total_seats=500,
                available_seats=497,  # 3 seats booked
                performance_status="Scheduled"
            )
        ]
        db.add_all(performances)
        db.flush()
        
        # 7. Insert Performance Pricing
        print("→ Inserting performance pricing...")
        pricing = []
        price_map = {
            "VIP": Decimal("75.00"),
            "Premium": Decimal("50.00"),
            "Standard": Decimal("30.00"),
            "Economy": Decimal("20.00")
        }
        
        for perf in performances:
            for category, price in price_map.items():
                pricing.append(PerformancePricing(
                    performance_id=perf.performance_id,
                    seat_category=category,
                    price=price
                ))
        
        db.add_all(pricing)
        db.flush()
        
        # 8. Insert Sample Bookings
        print("→ Inserting sample bookings...")
        
        # Booking 1: User 1 books 2 Premium seats for Les Mis
        booking1 = Booking(
            user_id=users[0].user_id,
            performance_id=performances[3].performance_id,  # Les Mis matinee
            booking_reference="BK20251124001",
            total_amount=Decimal("100.00"),
            booking_status="Confirmed"
        )
        db.add(booking1)
        db.flush()
        
        # Get 2 premium seats
        premium_seats = [s for s in seats if s.seat_category == "Premium"][:2]
        for seat in premium_seats:
            db.add(BookingDetail(
                booking_id=booking1.booking_id,
                seat_id=seat.seat_id,
                seat_price=Decimal("50.00"),
                row_number=seat.row_number,
                seat_number=seat.seat_number,
                seat_category=seat.seat_category
            ))
        
        # Payment for booking 1
        db.add(Payment(
            booking_id=booking1.booking_id,
            payment_amount=Decimal("100.00"),
            payment_method="Credit Card",
            payment_status="Completed",
            transaction_id="TXN1001",
            payment_date=datetime.now()
        ))
        
        # Booking 2: User 2 books 3 Standard seats for Macbeth
        booking2 = Booking(
            user_id=users[1].user_id,
            performance_id=performances[6].performance_id,  # Macbeth second night
            booking_reference="BK20251124002",
            total_amount=Decimal("90.00"),
            booking_status="Confirmed"
        )
        db.add(booking2)
        db.flush()
        
        # Get 3 standard seats
        standard_seats = [s for s in seats if s.seat_category == "Standard"][:3]
        for seat in standard_seats:
            db.add(BookingDetail(
                booking_id=booking2.booking_id,
                seat_id=seat.seat_id,
                seat_price=Decimal("30.00"),
                row_number=seat.row_number,
                seat_number=seat.seat_number,
                seat_category=seat.seat_category
            ))
        
        # Payment for booking 2
        db.add(Payment(
            booking_id=booking2.booking_id,
            payment_amount=Decimal("90.00"),
            payment_method="Debit Card",
            payment_status="Completed",
            transaction_id="TXN1002",
            payment_date=datetime.now()
        ))
        
        db.commit()
        
        print("\n✓ Database initialized successfully!")
        print(f"\nSummary:")
        print(f"  • {len(genres)} genres")
        print(f"  • {len(users)} users")
        print(f"  • 1 venue (Grand Theatre)")
        print(f"  • {len(shows)} shows")
        print(f"  • {len(seats)} seats")
        print(f"  • {len(performances)} performances")
        print(f"  • 2 sample bookings with payments")
        print(f"\nTest credentials:")
        print(f"  Email: john.doe@example.com")
        print(f"  Email: jane.smith@example.com")
        print(f"  Email: admin@theatre.com")
        print(f"  Password (all users): password123")
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error initializing database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
