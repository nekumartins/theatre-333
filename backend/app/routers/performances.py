from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict
from app import models, schemas, database

router = APIRouter(prefix="/api/performances", tags=["Performances"])


@router.get("/")
def get_all_performances(db: Session = Depends(database.get_db)):
    """Get all upcoming performances"""
    performances = db.query(models.Performance).filter(
        models.Performance.performance_date >= date.today(),
        models.Performance.performance_status == "Scheduled"
    ).all()
    
    performances_data = []
    for p in performances:
        performances_data.append({
            "performance_id": p.performance_id,
            "show_id": p.show_id,
            "venue_id": p.venue_id,
            "performance_date": p.performance_date.isoformat() if p.performance_date else None,
            "start_time": str(p.start_time) if p.start_time else None,
            "performance_status": p.performance_status
        })
    
    return {"performances": performances_data, "count": len(performances_data)}


@router.get("/show/{show_id}", response_model=List[schemas.PerformanceResponse])
def get_performances_for_show(show_id: int, db: Session = Depends(database.get_db)):
    """Get all upcoming performances for a specific show"""
    performances = db.query(models.Performance).filter(
        models.Performance.show_id == show_id,
        models.Performance.performance_date >= date.today(),
        models.Performance.performance_status == "Scheduled"
    ).all()
    
    return performances


@router.get("/{performance_id}", response_model=schemas.PerformanceResponse)
def get_performance_detail(performance_id: int, db: Session = Depends(database.get_db)):
    """Get specific performance details"""
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == performance_id
    ).first()
    
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    return performance


@router.get("/{performance_id}/seats")
def get_available_seats(performance_id: int, db: Session = Depends(database.get_db)):
    """Get seat availability for a specific performance"""
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == performance_id
    ).first()
    
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    # Get all seats for the venue
    all_seats = db.query(models.Seat).filter(
        models.Seat.venue_id == performance.venue_id,
        models.Seat.is_active == True
    ).all()
    
    # Get already booked seats
    booked_seats = db.query(models.BookingDetail.seat_id).join(
        models.Booking
    ).filter(
        models.Booking.performance_id == performance_id,
        models.Booking.booking_status.in_(["Pending", "Confirmed"])
    ).all()
    
    booked_seat_ids = [seat[0] for seat in booked_seats]
    
    # Get pricing for this performance
    pricing = db.query(models.PerformancePricing).filter(
        models.PerformancePricing.performance_id == performance_id
    ).all()
    
    pricing_dict = {p.seat_category: float(p.price) for p in pricing}
    
    # Mark seats as available or booked
    seat_map = []
    for seat in all_seats:
        seat_map.append({
            "seat_id": seat.seat_id,
            "row": seat.row_number,
            "number": seat.seat_number,
            "category": seat.seat_category,
            "section": seat.section,
            "is_accessible": seat.is_accessible,
            "is_booked": seat.seat_id in booked_seat_ids,
            "price": pricing_dict.get(seat.seat_category, 0.0)
        })
    
    return {
        "performance_id": performance_id,
        "performance_date": str(performance.performance_date),
        "start_time": str(performance.start_time),
        "available_seats": performance.available_seats,
        "seats": seat_map
    }
