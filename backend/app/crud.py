# Database CRUD Operations
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date, datetime
from typing import List, Optional
import models, schemas


# ============================================
# USER OPERATIONS
# ============================================

def get_user_by_email(db: Session, email: str):
    """Get user by email address"""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    """Create a new user"""
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        city=user.city,
        country=user.country
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============================================
# SHOW OPERATIONS
# ============================================

def get_shows(db: Session, genre_id: Optional[int] = None, status: str = "Active"):
    """Get all shows with optional genre filter"""
    query = db.query(models.Show).filter(models.Show.show_status == status)
    if genre_id:
        query = query.filter(models.Show.genre_id == genre_id)
    return query.all()


def get_show_by_id(db: Session, show_id: int):
    """Get show by ID"""
    return db.query(models.Show).filter(models.Show.show_id == show_id).first()


def get_genres(db: Session):
    """Get all genres"""
    return db.query(models.Genre).all()


# ============================================
# PERFORMANCE OPERATIONS
# ============================================

def get_performances_by_show(db: Session, show_id: int):
    """Get all upcoming performances for a show"""
    return db.query(models.Performance).filter(
        models.Performance.show_id == show_id,
        models.Performance.performance_date >= date.today(),
        models.Performance.performance_status == "Scheduled"
    ).order_by(models.Performance.performance_date, models.Performance.start_time).all()


def get_performance_by_id(db: Session, performance_id: int):
    """Get performance by ID"""
    return db.query(models.Performance).filter(
        models.Performance.performance_id == performance_id
    ).first()


def get_performance_pricing(db: Session, performance_id: int):
    """Get pricing for a performance"""
    return db.query(models.PerformancePricing).filter(
        models.PerformancePricing.performance_id == performance_id
    ).all()


# ============================================
# SEAT OPERATIONS
# ============================================

def get_seats_by_venue(db: Session, venue_id: int):
    """Get all active seats for a venue"""
    return db.query(models.Seat).filter(
        models.Seat.venue_id == venue_id,
        models.Seat.is_active == True
    ).order_by(models.Seat.row_number, models.Seat.seat_number).all()


def get_booked_seats(db: Session, performance_id: int):
    """Get all booked seat IDs for a performance"""
    booked = db.query(models.BookingDetail.seat_id).join(
        models.Booking
    ).filter(
        models.Booking.performance_id == performance_id,
        models.Booking.booking_status.in_(["Pending", "Confirmed"])
    ).all()
    return [seat[0] for seat in booked]


# ============================================
# BOOKING OPERATIONS
# ============================================

def create_booking(db: Session, booking_data: schemas.BookingCreate, booking_reference: str, total_amount: float):
    """Create a new booking"""
    db_booking = models.Booking(
        user_id=booking_data.user_id,
        performance_id=booking_data.performance_id,
        booking_reference=booking_reference,
        total_amount=total_amount,
        booking_status="Pending"
    )
    db.add(db_booking)
    db.flush()
    return db_booking


def create_booking_details(db: Session, booking_id: int, seat_details: List[dict]):
    """Create booking details for selected seats"""
    for detail in seat_details:
        db_detail = models.BookingDetail(
            booking_id=booking_id,
            seat_id=detail["seat_id"],
            seat_price=detail["price"],
            row_number=detail["row"],
            seat_number=detail["number"],
            seat_category=detail["category"]
        )
        db.add(db_detail)


def get_booking_by_id(db: Session, booking_id: int):
    """Get booking by ID"""
    return db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()


def get_user_bookings(db: Session, user_id: int):
    """Get all bookings for a user"""
    return db.query(models.Booking).filter(
        models.Booking.user_id == user_id
    ).order_by(models.Booking.booking_date.desc()).all()


def cancel_booking(db: Session, booking_id: int):
    """Cancel a booking"""
    booking = get_booking_by_id(db, booking_id)
    if booking:
        booking.booking_status = "Cancelled"
        # Restore available seats
        performance = booking.performance
        seat_count = db.query(models.BookingDetail).filter(
            models.BookingDetail.booking_id == booking_id
        ).count()
        performance.available_seats += seat_count
        db.commit()
    return booking


# ============================================
# PAYMENT OPERATIONS
# ============================================

def create_payment(db: Session, payment_data: schemas.PaymentCreate, transaction_id: str):
    """Create a new payment record"""
    db_payment = models.Payment(
        booking_id=payment_data.booking_id,
        amount=payment_data.amount,
        payment_method=payment_data.payment_method,
        transaction_id=transaction_id,
        payment_status="Completed",
        payment_date=datetime.now()
    )
    db.add(db_payment)
    
    # Update booking status
    booking = get_booking_by_id(db, payment_data.booking_id)
    if booking:
        booking.booking_status = "Confirmed"
    
    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payment_by_booking(db: Session, booking_id: int):
    """Get payment for a booking"""
    return db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id
    ).first()
