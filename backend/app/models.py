from sqlalchemy import Column, Integer, String, Text, Date, Time, DECIMAL, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Genre(Base):
    __tablename__ = "genre"
    
    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    genre_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    shows = relationship("Show", back_populates="genre")


class User(Base):
    __tablename__ = "user"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    date_of_birth = Column(Date)
    address_line1 = Column(String(100))
    address_line2 = Column(String(100))
    city = Column(String(50))
    postal_code = Column(String(20))
    country = Column(String(50))
    registration_date = Column(Date, nullable=False)
    email_verified = Column(Boolean, default=False)
    account_status = Column(String(20), default="Active")
    is_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bookings = relationship("Booking", back_populates="user")


class Show(Base):
    __tablename__ = "show_table"
    
    show_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    genre_id = Column(Integer, ForeignKey("genre.genre_id"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    language = Column(String(50))
    age_rating = Column(String(10))
    poster_url = Column(String(255))
    producer = Column(String(100))
    director = Column(String(100))
    show_status = Column(String(20), default="Active")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    genre = relationship("Genre", back_populates="shows")
    performances = relationship("Performance", back_populates="show")


class Venue(Base):
    __tablename__ = "venue"
    
    venue_id = Column(Integer, primary_key=True, autoincrement=True)
    venue_name = Column(String(100), nullable=False)
    address_line1 = Column(String(100), nullable=False)
    address_line2 = Column(String(100))
    city = Column(String(50), nullable=False)
    postal_code = Column(String(20))
    country = Column(String(50), nullable=False)
    total_capacity = Column(Integer, nullable=False)
    phone = Column(String(20))
    facilities = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    seats = relationship("Seat", back_populates="venue")
    performances = relationship("Performance", back_populates="venue")


class Seat(Base):
    __tablename__ = "seat"
    
    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    venue_id = Column(Integer, ForeignKey("venue.venue_id"), nullable=False)
    row_number = Column(String(10), nullable=False)
    seat_number = Column(String(10), nullable=False)
    section = Column(String(50))
    seat_category = Column(String(20), nullable=False)
    is_accessible = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    venue = relationship("Venue", back_populates="seats")
    booking_details = relationship("BookingDetail", back_populates="seat")


class SeatCategoryPricing(Base):
    __tablename__ = "seat_category_pricing"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), unique=True, nullable=False)
    base_price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(Text)


class Performance(Base):
    __tablename__ = "performance"
    
    performance_id = Column(Integer, primary_key=True, autoincrement=True)
    show_id = Column(Integer, ForeignKey("show_table.show_id"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.venue_id"), nullable=False)
    performance_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    performance_status = Column(String(20), default="Scheduled")
    special_notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    show = relationship("Show", back_populates="performances")
    venue = relationship("Venue", back_populates="performances")
    bookings = relationship("Booking", back_populates="performance")
    pricing = relationship("PerformancePricing", back_populates="performance")


class PerformancePricing(Base):
    __tablename__ = "performance_pricing"
    
    pricing_id = Column(Integer, primary_key=True, autoincrement=True)
    performance_id = Column(Integer, ForeignKey("performance.performance_id"), nullable=False)
    seat_category = Column(String(20), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    performance = relationship("Performance", back_populates="pricing")


class Booking(Base):
    __tablename__ = "booking"
    
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    performance_id = Column(Integer, ForeignKey("performance.performance_id"), nullable=False)
    booking_reference = Column(String(20), unique=True, nullable=False)
    booking_date = Column(TIMESTAMP, server_default=func.now())
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    booking_status = Column(String(20), default="Pending")
    cancellation_date = Column(TIMESTAMP)
    refund_amount = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    performance = relationship("Performance", back_populates="bookings")
    booking_details = relationship("BookingDetail", back_populates="booking")
    payments = relationship("Payment", back_populates="booking")


class BookingDetail(Base):
    __tablename__ = "booking_detail"
    
    booking_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("booking.booking_id"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seat.seat_id"), nullable=False)
    seat_price = Column(DECIMAL(10, 2), nullable=False)
    row_number = Column(String(10), nullable=False)
    seat_number = Column(String(10), nullable=False)
    seat_category = Column(String(20), nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="booking_details")
    seat = relationship("Seat", back_populates="booking_details")


class Payment(Base):
    __tablename__ = "payment"
    
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("booking.booking_id"), nullable=False)
    payment_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_date = Column(TIMESTAMP, server_default=func.now())
    transaction_id = Column(String(100))
    payment_status = Column(String(20), default="Pending")
    gateway_response = Column(Text)
    card_last_four = Column(String(4))
    refund_date = Column(TIMESTAMP)
    refund_transaction_id = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships
    booking = relationship("Booking", back_populates="payments")
