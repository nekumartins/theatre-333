"""
MySQL Database Setup Script for Theatre Booking System

This script:
1. Creates the MySQL database if it doesn't exist
2. Creates all tables from SQLAlchemy models
3. Seeds initial data (genres, roles, venues, seats, etc.)

Prerequisites:
- MySQL Server installed and running
- PyMySQL installed (pip install pymysql)

Usage:
    python setup_mysql.py

Configuration:
    Edit the .env file to set your MySQL credentials:
    DATABASE_URL=mysql+pymysql://username:password@localhost:3306/theatre_booking
"""

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from datetime import date, time, timedelta
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")

# Parse database URL to extract components
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/theatre_booking")

def parse_mysql_url(url):
    """Parse MySQL URL to extract connection components"""
    # Remove the driver prefix
    url = url.replace("mysql+pymysql://", "")
    
    # Split user:password@host:port/database
    if "@" in url:
        auth, rest = url.split("@", 1)
        if ":" in auth:
            user, password = auth.split(":", 1)
        else:
            user, password = auth, ""
    else:
        user, password = "root", ""
        rest = url
    
    if "/" in rest:
        host_port, database = rest.rsplit("/", 1)
    else:
        host_port, database = rest, "theatre_booking"
    
    if ":" in host_port:
        host, port = host_port.split(":")
        port = int(port)
    else:
        host, port = host_port, 3306
    
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database
    }


def create_database():
    """Create the MySQL database if it doesn't exist"""
    config = parse_mysql_url(DATABASE_URL)
    
    print(f"🔌 Connecting to MySQL server at {config['host']}:{config['port']}...")
    
    try:
        # Connect without specifying database
        connection = pymysql.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{config['database']}' created or already exists")
        
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        print("\n⚠️  Make sure:")
        print("   1. MySQL Server is running")
        print("   2. Your credentials in .env are correct")
        print("   3. The MySQL user has CREATE DATABASE privileges")
        return False


def create_tables():
    """Create all tables using SQLAlchemy models"""
    print("\n📦 Creating tables...")
    
    # Import after database is created
    from app.database import engine, Base
    from app import models  # This imports all models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully")


def seed_data():
    """Seed initial data into the database"""
    print("\n🌱 Seeding initial data...")
    
    from app.database import SessionLocal
    from app.models import (
        Genre, Role, Venue, Seat, Show, Performance, 
        PerformancePricing, SeatCategoryPricing, User
    )
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_genres = db.query(Genre).count()
        if existing_genres > 0:
            print("⚠️  Data already exists, skipping seed...")
            return
        
        # 1. Seed Genres
        genres = [
            Genre(genre_name="Musical", description="Broadway-style musical productions with singing and dancing"),
            Genre(genre_name="Drama", description="Serious theatrical works exploring human emotions and conflicts"),
            Genre(genre_name="Comedy", description="Light-hearted performances designed to amuse and entertain"),
            Genre(genre_name="Opera", description="Classical musical drama combining singing and orchestral music"),
            Genre(genre_name="Ballet", description="Classical dance performances with orchestral accompaniment"),
            Genre(genre_name="Children's Theatre", description="Family-friendly shows suitable for young audiences"),
        ]
        db.add_all(genres)
        db.commit()
        print("  ✓ Genres seeded")
        
        # 2. Seed Roles
        roles = [
            Role(
                role_name="Super Admin",
                description="Full system access with all permissions",
                can_manage_shows=True, can_manage_venues=True, can_manage_performances=True,
                can_manage_bookings=True, can_view_analytics=True, can_manage_users=True,
                can_manage_pricing=True, can_issue_refunds=True
            ),
            Role(
                role_name="Manager",
                description="Can manage shows, performances, and view analytics",
                can_manage_shows=True, can_manage_venues=True, can_manage_performances=True,
                can_manage_bookings=True, can_view_analytics=True, can_manage_users=False,
                can_manage_pricing=True, can_issue_refunds=True
            ),
            Role(
                role_name="Staff",
                description="Can manage bookings and issue refunds",
                can_manage_shows=False, can_manage_venues=False, can_manage_performances=False,
                can_manage_bookings=True, can_view_analytics=False, can_manage_users=False,
                can_manage_pricing=False, can_issue_refunds=True
            ),
            Role(
                role_name="Analyst",
                description="View-only access to analytics and reports",
                can_manage_shows=False, can_manage_venues=False, can_manage_performances=False,
                can_manage_bookings=False, can_view_analytics=True, can_manage_users=False,
                can_manage_pricing=False, can_issue_refunds=False
            ),
        ]
        db.add_all(roles)
        db.commit()
        print("  ✓ Roles seeded")
        
        # 3. Seed Seat Category Pricing
        seat_pricing = [
            SeatCategoryPricing(category_name="VIP", base_price=Decimal("150.00"), description="Premium front-row seating"),
            SeatCategoryPricing(category_name="Premium", base_price=Decimal("100.00"), description="Excellent center seating"),
            SeatCategoryPricing(category_name="Standard", base_price=Decimal("60.00"), description="Good view seating"),
            SeatCategoryPricing(category_name="Economy", base_price=Decimal("35.00"), description="Budget-friendly seating"),
        ]
        db.add_all(seat_pricing)
        db.commit()
        print("  ✓ Seat category pricing seeded")
        
        # 4. Seed Venue
        venue = Venue(
            venue_name="Royal Theatre London",
            address_line1="123 Theatre Lane",
            address_line2="West End",
            city="London",
            postal_code="WC2H 0DA",
            country="United Kingdom",
            total_capacity=200,
            phone="+44 20 7123 4567",
            facilities="Wheelchair access, Hearing loop, Bar, Restaurant, Cloakroom"
        )
        db.add(venue)
        db.commit()
        print("  ✓ Venue seeded")
        
        # 5. Seed Seats (200 seats: 10 rows x 20 seats)
        seat_categories = {
            "A": "VIP", "B": "VIP",
            "C": "Premium", "D": "Premium", "E": "Premium",
            "F": "Standard", "G": "Standard", "H": "Standard",
            "I": "Economy", "J": "Economy"
        }
        
        seats = []
        for row in "ABCDEFGHIJ":
            for num in range(1, 21):
                seats.append(Seat(
                    venue_id=venue.venue_id,
                    row_number=row,
                    seat_number=str(num),
                    section="Main Hall",
                    seat_category=seat_categories[row],
                    is_accessible=(num in [1, 20]),  # Aisle seats are accessible
                    is_active=True
                ))
        db.add_all(seats)
        db.commit()
        print("  ✓ 200 seats seeded")
        
        # 6. Seed Shows
        shows = [
            Show(
                title="The Phantom of the Opera",
                description="The longest-running show in Broadway history tells the story of a masked figure who lurks beneath the Paris Opera House.",
                genre_id=1,  # Musical
                duration_minutes=150,
                language="English",
                age_rating="PG",
                poster_url="/static/images/phantom.jpg",
                producer="Cameron Mackintosh",
                director="Harold Prince",
                show_status="Active"
            ),
            Show(
                title="Hamlet",
                description="Shakespeare's timeless tragedy of the Prince of Denmark and his quest for revenge.",
                genre_id=2,  # Drama
                duration_minutes=180,
                language="English",
                age_rating="12A",
                poster_url="/static/images/hamlet.jpg",
                producer="Royal Shakespeare Company",
                director="Gregory Doran",
                show_status="Active"
            ),
            Show(
                title="The Comedy of Errors",
                description="A hilarious tale of mistaken identities and comic mishaps.",
                genre_id=3,  # Comedy
                duration_minutes=120,
                language="English",
                age_rating="PG",
                poster_url="/static/images/comedy.jpg",
                producer="National Theatre",
                director="Simon Godwin",
                show_status="Active"
            ),
            Show(
                title="Swan Lake",
                description="Tchaikovsky's beloved ballet about a princess turned into a swan by an evil sorcerer's curse.",
                genre_id=5,  # Ballet
                duration_minutes=165,
                language="Non-verbal",
                age_rating="U",
                poster_url="/static/images/swan-lake.jpg",
                producer="Royal Ballet",
                director="Liam Scarlett",
                show_status="Active"
            ),
        ]
        db.add_all(shows)
        db.commit()
        print("  ✓ Shows seeded")
        
        # 7. Seed Performances (upcoming dates)
        today = date.today()
        performances = []
        pricing_list = []
        
        for show in shows:
            for i in range(3):  # 3 performances per show
                perf_date = today + timedelta(days=7 + (i * 3))
                perf = Performance(
                    show_id=show.show_id,
                    venue_id=venue.venue_id,
                    performance_date=perf_date,
                    start_time=time(19, 30) if i % 2 == 0 else time(14, 30),
                    end_time=time(22, 0) if i % 2 == 0 else time(17, 0),
                    total_seats=200,
                    available_seats=200,
                    performance_status="Scheduled"
                )
                performances.append(perf)
        
        db.add_all(performances)
        db.commit()
        
        # Add pricing for each performance
        price_by_category = {
            "VIP": Decimal("150.00"),
            "Premium": Decimal("100.00"),
            "Standard": Decimal("60.00"),
            "Economy": Decimal("35.00")
        }
        
        for perf in performances:
            for category, price in price_by_category.items():
                pricing_list.append(PerformancePricing(
                    performance_id=perf.performance_id,
                    seat_category=category,
                    price=price
                ))
        
        db.add_all(pricing_list)
        db.commit()
        print("  ✓ Performances and pricing seeded")
        
        # 8. Create admin user
        admin_role = db.query(Role).filter(Role.role_name == "Super Admin").first()
        admin = User(
            first_name="Admin",
            last_name="User",
            email="admin@theatre.com",
            phone="+44 20 7123 4567",
            password_hash=pwd_context.hash("admin123"),
            registration_date=date.today(),
            email_verified=True,
            account_status="Active",
            is_admin=True,
            role_id=admin_role.role_id if admin_role else None
        )
        db.add(admin)
        db.commit()
        print("  ✓ Admin user created (email: admin@theatre.com, password: admin123)")
        
        print("\n✅ All seed data inserted successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


def main():
    print("=" * 60)
    print("🎭 Theatre Booking System - MySQL Setup")
    print("=" * 60)
    print(f"\nDatabase URL: {DATABASE_URL.replace(parse_mysql_url(DATABASE_URL)['password'], '***') if parse_mysql_url(DATABASE_URL)['password'] else DATABASE_URL}")
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    create_tables()
    
    # Step 3: Seed data
    seed_data()
    
    print("\n" + "=" * 60)
    print("🎉 MySQL setup complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("  1. Open MySQL Workbench and connect to 'theatre_booking'")
    print("  2. Run: python -m uvicorn app.main:app --reload")
    print("  3. Access the app at http://localhost:8000")


if __name__ == "__main__":
    main()
