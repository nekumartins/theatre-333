from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, datetime, timedelta
from typing import List
from app import models, database, auth

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_analytics(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get comprehensive dashboard analytics (Admin only)"""
    
    # Revenue analytics
    total_revenue = db.query(func.sum(models.Payment.payment_amount)).filter(
        models.Payment.payment_status == "Completed"
    ).scalar() or 0
    
    # Booking statistics
    total_bookings = db.query(models.Booking).count()
    confirmed_bookings = db.query(models.Booking).filter(
        models.Booking.booking_status == "Confirmed"
    ).count()
    pending_bookings = db.query(models.Booking).filter(
        models.Booking.booking_status == "Pending"
    ).count()
    cancelled_bookings = db.query(models.Booking).filter(
        models.Booking.booking_status == "Cancelled"
    ).count()
    
    # Payment statistics
    total_payments = db.query(models.Payment).count()
    successful_payments = db.query(models.Payment).filter(
        models.Payment.payment_status == "Completed"
    ).count()
    failed_payments = db.query(models.Payment).filter(
        models.Payment.payment_status == "Failed"
    ).count()
    
    payment_success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
    
    # User statistics
    total_users = db.query(models.User).count()
    verified_users = db.query(models.User).filter(models.User.email_verified == True).count()
    
    # Show statistics
    total_shows = db.query(models.Show).count()
    active_shows = db.query(models.Show).filter(models.Show.show_status == "Active").count()
    
    # Performance statistics
    total_performances = db.query(models.Performance).count()
    upcoming_performances = db.query(models.Performance).filter(
        models.Performance.performance_date >= date.today(),
        models.Performance.performance_status == "Scheduled"
    ).count()
    
    return {
        "revenue": {
            "total": float(total_revenue),
            "currency": "USD"
        },
        "bookings": {
            "total": total_bookings,
            "confirmed": confirmed_bookings,
            "pending": pending_bookings,
            "cancelled": cancelled_bookings,
            "confirmation_rate": (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
        },
        "payments": {
            "total_attempts": total_payments,
            "successful": successful_payments,
            "failed": failed_payments,
            "success_rate": round(payment_success_rate, 2)
        },
        "users": {
            "total": total_users,
            "verified": verified_users,
            "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
        },
        "shows": {
            "total": total_shows,
            "active": active_shows
        },
        "performances": {
            "total": total_performances,
            "upcoming": upcoming_performances
        }
    }


@router.get("/popular-shows")
def get_popular_shows(
    limit: int = 10,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get most popular shows by booking count (Admin only)"""
    
    popular_shows = db.query(
        models.Show.show_id,
        models.Show.title,
        func.count(models.Booking.booking_id).label('booking_count'),
        func.sum(models.Booking.total_amount).label('total_revenue')
    ).join(
        models.Performance, models.Show.show_id == models.Performance.show_id
    ).join(
        models.Booking, models.Performance.performance_id == models.Booking.performance_id
    ).filter(
        models.Booking.booking_status.in_(["Confirmed", "Pending"])
    ).group_by(
        models.Show.show_id, models.Show.title
    ).order_by(
        desc('booking_count')
    ).limit(limit).all()
    
    return [
        {
            "show_id": show.show_id,
            "title": show.title,
            "booking_count": show.booking_count,
            "total_revenue": float(show.total_revenue or 0)
        }
        for show in popular_shows
    ]


@router.get("/revenue-by-performance")
def get_revenue_by_performance(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get revenue breakdown by performance (Admin only)"""
    
    performance_revenue = db.query(
        models.Performance.performance_id,
        models.Show.title,
        models.Performance.performance_date,
        models.Performance.start_time,
        models.Venue.venue_name,
        func.count(models.Booking.booking_id).label('booking_count'),
        func.sum(models.Booking.total_amount).label('revenue')
    ).join(
        models.Show, models.Performance.show_id == models.Show.show_id
    ).join(
        models.Venue, models.Performance.venue_id == models.Venue.venue_id
    ).outerjoin(
        models.Booking, models.Performance.performance_id == models.Booking.performance_id
    ).filter(
        models.Booking.booking_status == "Confirmed"
    ).group_by(
        models.Performance.performance_id,
        models.Show.title,
        models.Performance.performance_date,
        models.Performance.start_time,
        models.Venue.venue_name
    ).order_by(
        desc('revenue')
    ).limit(20).all()
    
    return [
        {
            "performance_id": perf.performance_id,
            "show_title": perf.title,
            "performance_date": str(perf.performance_date),
            "start_time": str(perf.start_time),
            "venue_name": perf.venue_name,
            "booking_count": perf.booking_count or 0,
            "revenue": float(perf.revenue or 0)
        }
        for perf in performance_revenue
    ]


@router.get("/venue-utilization")
def get_venue_utilization(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get venue utilization statistics (Admin only)"""
    
    venue_stats = db.query(
        models.Venue.venue_id,
        models.Venue.venue_name,
        models.Venue.total_capacity,
        func.count(models.Performance.performance_id).label('performance_count'),
        func.sum(models.Performance.total_seats - models.Performance.available_seats).label('seats_sold')
    ).outerjoin(
        models.Performance, models.Venue.venue_id == models.Performance.venue_id
    ).group_by(
        models.Venue.venue_id,
        models.Venue.venue_name,
        models.Venue.total_capacity
    ).all()
    
    return [
        {
            "venue_id": venue.venue_id,
            "venue_name": venue.venue_name,
            "total_capacity": venue.total_capacity,
            "performance_count": venue.performance_count or 0,
            "seats_sold": venue.seats_sold or 0,
            "utilization_rate": round((venue.seats_sold or 0) / (venue.total_capacity * (venue.performance_count or 1)) * 100, 2) if venue.performance_count else 0
        }
        for venue in venue_stats
    ]


@router.get("/booking-trends")
def get_booking_trends(
    days: int = 30,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get booking trends over time (Admin only)"""
    
    start_date = datetime.now() - timedelta(days=days)
    
    daily_bookings = db.query(
        func.date(models.Booking.booking_date).label('date'),
        func.count(models.Booking.booking_id).label('booking_count'),
        func.sum(models.Booking.total_amount).label('revenue')
    ).filter(
        models.Booking.booking_date >= start_date
    ).group_by(
        func.date(models.Booking.booking_date)
    ).order_by(
        'date'
    ).all()
    
    return [
        {
            "date": str(booking.date),
            "booking_count": booking.booking_count,
            "revenue": float(booking.revenue or 0)
        }
        for booking in daily_bookings
    ]


@router.get("/payment-methods")
def get_payment_method_stats(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get payment method distribution (Admin only)"""
    
    payment_methods = db.query(
        models.Payment.payment_method,
        func.count(models.Payment.payment_id).label('count'),
        func.sum(models.Payment.payment_amount).label('total_amount')
    ).filter(
        models.Payment.payment_status == "Completed"
    ).group_by(
        models.Payment.payment_method
    ).all()
    
    return [
        {
            "payment_method": method.payment_method,
            "transaction_count": method.count,
            "total_amount": float(method.total_amount or 0)
        }
        for method in payment_methods
    ]


@router.get("/genre-performance")
def get_genre_performance(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get performance metrics by genre (Admin only)"""
    
    genre_stats = db.query(
        models.Genre.genre_name,
        func.count(models.Show.show_id).label('show_count'),
        func.count(models.Booking.booking_id).label('booking_count'),
        func.sum(models.Booking.total_amount).label('revenue')
    ).join(
        models.Show, models.Genre.genre_id == models.Show.genre_id
    ).outerjoin(
        models.Performance, models.Show.show_id == models.Performance.show_id
    ).outerjoin(
        models.Booking, models.Performance.performance_id == models.Booking.performance_id
    ).filter(
        models.Booking.booking_status == "Confirmed"
    ).group_by(
        models.Genre.genre_name
    ).all()
    
    return [
        {
            "genre": genre.genre_name,
            "show_count": genre.show_count,
            "booking_count": genre.booking_count or 0,
            "revenue": float(genre.revenue or 0)
        }
        for genre in genre_stats
    ]
