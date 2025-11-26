from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app import models, schemas, database, utils

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: schemas.BookingCreate,
    db: Session = Depends(database.get_db)
):
    """Create a new booking with selected seats"""
    # Validate performance exists
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == booking_data.performance_id
    ).first()
    
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    # Check seat availability
    for seat_id in booking_data.seat_ids:
        existing_booking = db.query(models.BookingDetail).join(
            models.Booking
        ).filter(
            models.BookingDetail.seat_id == seat_id,
            models.Booking.performance_id == booking_data.performance_id,
            models.Booking.booking_status.in_(["Pending", "Confirmed"])
        ).first()
        
        if existing_booking:
            raise HTTPException(status_code=400, detail=f"Seat {seat_id} already booked")
    
    # Calculate total amount
    total = Decimal('0.00')
    seat_details = []
    
    for seat_id in booking_data.seat_ids:
        seat = db.query(models.Seat).filter(models.Seat.seat_id == seat_id).first()
        if not seat:
            raise HTTPException(status_code=404, detail=f"Seat {seat_id} not found")
        
        price_obj = db.query(models.PerformancePricing).filter(
            models.PerformancePricing.performance_id == booking_data.performance_id,
            models.PerformancePricing.seat_category == seat.seat_category
        ).first()
        
        if not price_obj:
            raise HTTPException(status_code=404, detail=f"Pricing not found for {seat.seat_category}")
        
        total += price_obj.price
        seat_details.append({
            "seat_id": seat_id,
            "price": price_obj.price,
            "row": seat.row_number,
            "number": seat.seat_number,
            "category": seat.seat_category
        })
    
    # Create booking
    new_booking = models.Booking(
        user_id=booking_data.user_id,
        performance_id=booking_data.performance_id,
        booking_reference=utils.generate_booking_reference(),
        total_amount=total,
        booking_status="Pending"
    )
    db.add(new_booking)
    db.flush()
    
    # Create booking details
    for detail in seat_details:
        booking_detail = models.BookingDetail(
            booking_id=new_booking.booking_id,
            seat_id=detail["seat_id"],
            seat_price=detail["price"],
            row_number=detail["row"],
            seat_number=detail["number"],
            seat_category=detail["category"]
        )
        db.add(booking_detail)
    
    # Update available seats
    performance.available_seats -= len(booking_data.seat_ids)
    
    db.commit()
    db.refresh(new_booking)
    
    # Get full booking details for confirmation
    booking_details = []
    for detail in db.query(models.BookingDetail).filter(
        models.BookingDetail.booking_id == new_booking.booking_id
    ).all():
        booking_details.append({
            "seat_id": detail.seat_id,
            "row": detail.row_number,
            "seat_number": detail.seat_number,
            "category": detail.seat_category,
            "price": float(detail.seat_price)
        })
    
    # Get show and performance info
    show = db.query(models.Show).filter(models.Show.show_id == performance.show_id).first()
    venue = db.query(models.Venue).filter(models.Venue.venue_id == performance.venue_id).first()
    
    return {
        "booking_id": new_booking.booking_id,
        "booking_reference": new_booking.booking_reference,
        "total_amount": float(new_booking.total_amount),
        "booking_date": str(new_booking.booking_date),
        "booking_status": new_booking.booking_status,
        "show_title": show.title if show else None,
        "performance_date": str(performance.performance_date),
        "performance_time": str(performance.start_time),
        "venue_name": venue.venue_name if venue else None,
        "venue_address": venue.address_line1 if venue else None,
        "seats": booking_details
    }


@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking_detail(booking_id: int, db: Session = Depends(database.get_db)):
    """Get booking details"""
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return booking


@router.get("/reference/{reference}")
def get_booking_by_reference(reference: str, db: Session = Depends(database.get_db)):
    """Get booking details by booking reference"""
    booking = db.query(models.Booking).filter(
        models.Booking.booking_reference == reference
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Get performance and show details
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == booking.performance_id
    ).first()
    
    show = db.query(models.Show).filter(
        models.Show.show_id == performance.show_id
    ).first() if performance else None
    
    venue = db.query(models.Venue).filter(
        models.Venue.venue_id == performance.venue_id
    ).first() if performance else None
    
    # Get booking details (seats)
    seats = []
    for detail in booking.booking_details:
        seats.append({
            "row": detail.row_number,
            "seat_number": detail.seat_number,
            "category": detail.seat_category,
            "price": float(detail.seat_price)
        })
    
    return {
        "booking_id": booking.booking_id,
        "booking_reference": booking.booking_reference,
        "booking_status": booking.booking_status,
        "booking_date": str(booking.booking_date),
        "total_amount": float(booking.total_amount),
        "show_title": show.title if show else None,
        "performance_date": str(performance.performance_date) if performance else None,
        "performance_time": str(performance.start_time) if performance else None,
        "venue_name": venue.venue_name if venue else None,
        "venue_address": f"{venue.address_line1}, {venue.city}" if venue else None,
        "seats": seats
    }


@router.get("/user/{user_id}", response_model=List[schemas.BookingResponse])
def get_user_bookings(user_id: int, db: Session = Depends(database.get_db)):
    """Get all bookings for a specific user"""
    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == user_id
    ).order_by(models.Booking.booking_date.desc()).all()
    
    return bookings


@router.delete("/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(database.get_db)):
    """Cancel a booking"""
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    # Update booking status
    booking.booking_status = "Cancelled"
    
    # Update available seats
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == booking.performance_id
    ).first()
    
    seat_count = db.query(models.BookingDetail).filter(
        models.BookingDetail.booking_id == booking_id
    ).count()
    
    performance.available_seats += seat_count
    
    db.commit()
    
    return {"message": "Booking cancelled successfully"}
