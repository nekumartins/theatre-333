from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app import models, schemas, database, utils, ticket_utils

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
        booking_reference=ticket_utils.generate_booking_reference(),
        total_amount=total,
        booking_status="Pending",
        payment_deadline=ticket_utils.calculate_payment_deadline()  # 15-minute deadline
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


@router.get("/{booking_id}/ticket")
def get_ticket(booking_id: int, db: Session = Depends(database.get_db)):
    """
    Get booking ticket with QR code
    Business requirement: Generate ticket with QR code for venue validation
    """
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status != "Confirmed":
        raise HTTPException(status_code=400, detail="Booking must be confirmed and paid to generate ticket")
    
    # Get performance, show, venue details
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == booking.performance_id
    ).first()
    
    show = db.query(models.Show).filter(
        models.Show.show_id == performance.show_id
    ).first()
    
    venue = db.query(models.Venue).filter(
        models.Venue.venue_id == performance.venue_id
    ).first()
    
    user = db.query(models.User).filter(
        models.User.user_id == booking.user_id
    ).first()
    
    # Get seats
    booking_details = db.query(models.BookingDetail).filter(
        models.BookingDetail.booking_id == booking_id
    ).all()
    
    seat_info = ", ".join([f"Row {bd.row_number} Seat {bd.seat_number}" for bd in booking_details])
    
    # Generate QR code
    qr_code = ticket_utils.generate_qr_code(booking.booking_reference, booking_id)
    
    # Prepare booking data for email/ticket
    booking_data = {
        "booking_reference": booking.booking_reference,
        "show_title": show.title,
        "performance_date": performance.performance_date.strftime("%B %d, %Y"),
        "start_time": performance.start_time.strftime("%I:%M %p"),
        "venue_name": venue.venue_name,
        "venue_address": f"{venue.address_line1}, {venue.city}",
        "seat_info": seat_info,
        "total_amount": str(booking.total_amount),
        "payment_status": "Confirmed",
        "booking_date": booking.booking_date.strftime("%B %d, %Y %I:%M %p")
    }
    
    return {
        "booking_id": booking_id,
        "booking_reference": booking.booking_reference,
        "qr_code": qr_code,
        "booking_data": booking_data,
        "message": "Ticket generated successfully"
    }


@router.post("/{booking_id}/send-confirmation")
def send_confirmation_email(booking_id: int, db: Session = Depends(database.get_db)):
    """
    Send booking confirmation email with ticket and QR code
    Business requirement: Email confirmation with booking details
    """
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status != "Confirmed":
        raise HTTPException(status_code=400, detail="Can only send confirmation for confirmed bookings")
    
    # Get user
    user = db.query(models.User).filter(
        models.User.user_id == booking.user_id
    ).first()
    
    # Get ticket data
    ticket_response = get_ticket(booking_id, db)
    
    # Send email
    email_result = ticket_utils.send_booking_confirmation(
        user.email,
        ticket_response["booking_data"],
        ticket_response["qr_code"]
    )
    
    return {
        "message": "Confirmation email sent successfully",
        "email_status": email_result["status"],
        "recipient": email_result["recipient"]
    }


@router.post("/{booking_id}/refund")
def request_refund(
    booking_id: int,
    refund_data: dict,
    db: Session = Depends(database.get_db)
):
    """
    Request a refund for a confirmed booking
    Business requirement: Cancellations allowed up to 24 hours before performance
    """
    from datetime import datetime, timedelta
    
    booking = db.query(models.Booking).filter(
        models.Booking.booking_id == booking_id
    ).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status != "Confirmed":
        raise HTTPException(status_code=400, detail="Can only refund confirmed bookings")
    
    # Get performance to check date
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == booking.performance_id
    ).first()
    
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    # Check if within cancellation window (24 hours before performance)
    perf_datetime = datetime.combine(performance.performance_date, performance.start_time)
    hours_until_show = (perf_datetime - datetime.now()).total_seconds() / 3600
    
    if hours_until_show < 0:
        raise HTTPException(status_code=400, detail="Cannot refund after performance has started")
    
    # Calculate refund amount based on policy
    # Full refund if > 24 hours, 50% if < 24 hours
    refund_amount = float(booking.total_amount)
    refund_percentage = 100
    
    if hours_until_show < 24:
        refund_amount = refund_amount * 0.5
        refund_percentage = 50
    
    # Update booking status to Cancelled
    booking.booking_status = "Cancelled"
    
    # Release the seats by updating available_seats count
    booking_details = db.query(models.BookingDetail).filter(
        models.BookingDetail.booking_id == booking_id
    ).all()
    
    performance.available_seats += len(booking_details)
    
    # Update payment status to Refunded if exists
    payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id,
        models.Payment.payment_status == "Completed"
    ).first()
    
    if payment:
        payment.payment_status = "Refunded"
    
    db.commit()
    
    # Get user for email notification
    user = db.query(models.User).filter(
        models.User.user_id == booking.user_id
    ).first()
    
    return {
        "message": "Refund request processed successfully",
        "booking_id": booking_id,
        "booking_reference": booking.booking_reference,
        "original_amount": float(booking.total_amount),
        "refund_amount": refund_amount,
        "refund_percentage": refund_percentage,
        "reason": refund_data.get("reason", "Customer requested"),
        "status": "Refunded",
        "email_sent_to": user.email if user else None
    }
