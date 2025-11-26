from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, time
from app import models, database, auth
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# Pydantic schemas for admin operations
class ShowCreate(BaseModel):
    title: str
    description: str | None = None
    genre_id: int
    duration_minutes: int
    language: str | None = None
    age_rating: str | None = None
    poster_url: str | None = None
    producer: str | None = None
    director: str | None = None
    show_status: str = "Active"


class ShowUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    genre_id: int | None = None
    duration_minutes: int | None = None
    language: str | None = None
    age_rating: str | None = None
    poster_url: str | None = None
    producer: str | None = None
    director: str | None = None
    show_status: str | None = None


class VenueCreate(BaseModel):
    venue_name: str
    address_line1: str
    address_line2: str | None = None
    city: str
    postal_code: str | None = None
    country: str
    total_capacity: int
    phone: str | None = None
    facilities: str | None = None


class VenueUpdate(BaseModel):
    venue_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    total_capacity: int | None = None
    phone: str | None = None
    facilities: str | None = None


class PerformanceCreate(BaseModel):
    show_id: int
    venue_id: int
    performance_date: date
    start_time: time
    end_time: time | None = None
    total_seats: int
    available_seats: int
    performance_status: str = "Scheduled"
    special_notes: str | None = None


class PerformanceUpdate(BaseModel):
    show_id: int | None = None
    venue_id: int | None = None
    performance_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    total_seats: int | None = None
    available_seats: int | None = None
    performance_status: str | None = None
    special_notes: str | None = None


class PerformancePricingCreate(BaseModel):
    performance_id: int
    seat_category: str
    price: float


class PerformancePricingUpdate(BaseModel):
    price: float


class GenreCreate(BaseModel):
    genre_name: str
    description: str | None = None


# ===== GENRE MANAGEMENT =====

@router.post("/genres", status_code=status.HTTP_201_CREATED)
def create_genre(
    genre: GenreCreate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create a new genre (Admin only)"""
    # Check if genre already exists
    existing = db.query(models.Genre).filter(models.Genre.genre_name == genre.genre_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Genre already exists")
    
    new_genre = models.Genre(
        genre_name=genre.genre_name,
        description=genre.description
    )
    
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    
    return {"genre_id": new_genre.genre_id, "message": "Genre created successfully"}


@router.get("/genres")
def list_genres(db: Session = Depends(database.get_db)):
    """List all genres"""
    genres = db.query(models.Genre).all()
    return {"genres": [{"genre_id": g.genre_id, "genre_name": g.genre_name, "description": g.description} for g in genres]}


# ===== SHOW MANAGEMENT =====

@router.post("/shows", status_code=status.HTTP_201_CREATED)
def create_show(
    show: ShowCreate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create a new show (Admin only)"""
    # Verify genre exists
    genre = db.query(models.Genre).filter(models.Genre.genre_id == show.genre_id).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    new_show = models.Show(**show.dict())
    db.add(new_show)
    db.commit()
    db.refresh(new_show)
    
    return {"message": "Show created successfully", "show_id": new_show.show_id}


@router.put("/shows/{show_id}")
def update_show(
    show_id: int,
    show: ShowUpdate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update show details (Admin only)"""
    db_show = db.query(models.Show).filter(models.Show.show_id == show_id).first()
    if not db_show:
        raise HTTPException(status_code=404, detail="Show not found")
    
    # Update only provided fields
    update_data = show.dict(exclude_unset=True)
    
    # Verify genre if provided
    if "genre_id" in update_data:
        genre = db.query(models.Genre).filter(models.Genre.genre_id == update_data["genre_id"]).first()
        if not genre:
            raise HTTPException(status_code=404, detail="Genre not found")
    
    for field, value in update_data.items():
        setattr(db_show, field, value)
    
    db.commit()
    db.refresh(db_show)
    
    return {"message": "Show updated successfully"}


@router.delete("/shows/{show_id}")
def delete_show(
    show_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Delete a show (Admin only)"""
    db_show = db.query(models.Show).filter(models.Show.show_id == show_id).first()
    if not db_show:
        raise HTTPException(status_code=404, detail="Show not found")
    
    # Check for associated performances
    performances = db.query(models.Performance).filter(models.Performance.show_id == show_id).first()
    if performances:
        raise HTTPException(status_code=400, detail="Cannot delete show with existing performances. Set status to 'Inactive' instead.")
    
    db.delete(db_show)
    db.commit()
    
    return {"message": "Show deleted successfully"}


# ===== VENUE MANAGEMENT =====

@router.post("/venues", status_code=status.HTTP_201_CREATED)
def create_venue(
    venue: VenueCreate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create a new venue (Admin only)"""
    new_venue = models.Venue(**venue.dict())
    db.add(new_venue)
    db.commit()
    db.refresh(new_venue)
    
    return {"message": "Venue created successfully", "venue_id": new_venue.venue_id}


@router.put("/venues/{venue_id}")
def update_venue(
    venue_id: int,
    venue: VenueUpdate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update venue details (Admin only)"""
    db_venue = db.query(models.Venue).filter(models.Venue.venue_id == venue_id).first()
    if not db_venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    update_data = venue.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_venue, field, value)
    
    db.commit()
    db.refresh(db_venue)
    
    return {"message": "Venue updated successfully"}


@router.delete("/venues/{venue_id}")
def delete_venue(
    venue_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Delete a venue (Admin only)"""
    db_venue = db.query(models.Venue).filter(models.Venue.venue_id == venue_id).first()
    if not db_venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Check for associated performances
    performances = db.query(models.Performance).filter(models.Performance.venue_id == venue_id).first()
    if performances:
        raise HTTPException(status_code=400, detail="Cannot delete venue with existing performances")
    
    db.delete(db_venue)
    db.commit()
    
    return {"message": "Venue deleted successfully"}


# ===== PERFORMANCE MANAGEMENT =====

@router.post("/performances", status_code=status.HTTP_201_CREATED)
def create_performance(
    performance: PerformanceCreate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create a new performance (Admin only)"""
    # Verify show exists
    show = db.query(models.Show).filter(models.Show.show_id == performance.show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    
    # Verify venue exists
    venue = db.query(models.Venue).filter(models.Venue.venue_id == performance.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    new_performance = models.Performance(**performance.dict())
    db.add(new_performance)
    db.commit()
    db.refresh(new_performance)
    
    return {"message": "Performance created successfully", "performance_id": new_performance.performance_id}


@router.put("/performances/{performance_id}")
def update_performance(
    performance_id: int,
    performance: PerformanceUpdate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update performance details (Admin only)"""
    db_performance = db.query(models.Performance).filter(models.Performance.performance_id == performance_id).first()
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    update_data = performance.dict(exclude_unset=True)
    
    # Verify show if provided
    if "show_id" in update_data:
        show = db.query(models.Show).filter(models.Show.show_id == update_data["show_id"]).first()
        if not show:
            raise HTTPException(status_code=404, detail="Show not found")
    
    # Verify venue if provided
    if "venue_id" in update_data:
        venue = db.query(models.Venue).filter(models.Venue.venue_id == update_data["venue_id"]).first()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
    
    for field, value in update_data.items():
        setattr(db_performance, field, value)
    
    db.commit()
    db.refresh(db_performance)
    
    return {"message": "Performance updated successfully"}


@router.delete("/performances/{performance_id}")
def delete_performance(
    performance_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Delete a performance (Admin only)"""
    db_performance = db.query(models.Performance).filter(models.Performance.performance_id == performance_id).first()
    if not db_performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    # Check for associated bookings
    bookings = db.query(models.Booking).filter(models.Booking.performance_id == performance_id).first()
    if bookings:
        raise HTTPException(status_code=400, detail="Cannot delete performance with existing bookings. Set status to 'Cancelled' instead.")
    
    db.delete(db_performance)
    db.commit()
    
    return {"message": "Performance deleted successfully"}


# ===== PERFORMANCE PRICING MANAGEMENT =====

@router.post("/pricing", status_code=status.HTTP_201_CREATED)
def create_performance_pricing(
    pricing: PerformancePricingCreate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create pricing for a performance seat category (Admin only)"""
    # Verify performance exists
    performance = db.query(models.Performance).filter(
        models.Performance.performance_id == pricing.performance_id
    ).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")
    
    # Check if pricing already exists for this category
    existing = db.query(models.PerformancePricing).filter(
        models.PerformancePricing.performance_id == pricing.performance_id,
        models.PerformancePricing.seat_category == pricing.seat_category
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Pricing for this category already exists. Use update endpoint.")
    
    new_pricing = models.PerformancePricing(**pricing.dict())
    db.add(new_pricing)
    db.commit()
    db.refresh(new_pricing)
    
    return {"message": "Performance pricing created successfully", "pricing_id": new_pricing.pricing_id}


@router.put("/pricing/{pricing_id}")
def update_performance_pricing(
    pricing_id: int,
    pricing: PerformancePricingUpdate,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update performance pricing (Admin only)"""
    db_pricing = db.query(models.PerformancePricing).filter(
        models.PerformancePricing.pricing_id == pricing_id
    ).first()
    
    if not db_pricing:
        raise HTTPException(status_code=404, detail="Pricing not found")
    
    db_pricing.price = pricing.price
    db.commit()
    
    return {"message": "Pricing updated successfully"}


@router.delete("/pricing/{pricing_id}")
def delete_performance_pricing(
    pricing_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Delete performance pricing (Admin only)"""
    db_pricing = db.query(models.PerformancePricing).filter(
        models.PerformancePricing.pricing_id == pricing_id
    ).first()
    
    if not db_pricing:
        raise HTTPException(status_code=404, detail="Pricing not found")
    
    db.delete(db_pricing)
    db.commit()
    
    return {"message": "Pricing deleted successfully"}


@router.get("/performances/{performance_id}/pricing")
def get_performance_pricing(
    performance_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get all pricing for a performance (Admin only)"""
    pricing = db.query(models.PerformancePricing).filter(
        models.PerformancePricing.performance_id == performance_id
    ).all()
    
    return [
        {
            "pricing_id": p.pricing_id,
            "seat_category": p.seat_category,
            "price": float(p.price)
        }
        for p in pricing
    ]


# ===== STATS & OVERVIEW =====

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get admin dashboard statistics"""
    total_shows = db.query(models.Show).count()
    active_shows = db.query(models.Show).filter(models.Show.show_status == "Active").count()
    total_venues = db.query(models.Venue).count()
    total_performances = db.query(models.Performance).count()
    upcoming_performances = db.query(models.Performance).filter(
        models.Performance.performance_date >= date.today(),
        models.Performance.performance_status == "Scheduled"
    ).count()
    total_bookings = db.query(models.Booking).count()
    confirmed_bookings = db.query(models.Booking).filter(models.Booking.booking_status == "Confirmed").count()
    total_users = db.query(models.User).count()
    
    return {
        "shows": {"total": total_shows, "active": active_shows},
        "venues": {"total": total_venues},
        "performances": {"total": total_performances, "upcoming": upcoming_performances},
        "bookings": {"total": total_bookings, "confirmed": confirmed_bookings},
        "users": {"total": total_users}
    }
