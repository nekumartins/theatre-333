from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
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
    pending_bookings = db.query(models.Booking).filter(models.Booking.booking_status == "Pending").count()
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.account_status == "Active").count()
    
    # Revenue calculation
    from sqlalchemy import func
    total_revenue = db.query(func.sum(models.Payment.payment_amount)).filter(
        models.Payment.payment_status == "Completed"
    ).scalar() or 0
    
    return {
        "shows": {"total": total_shows, "active": active_shows},
        "venues": {"total": total_venues},
        "performances": {"total": total_performances, "upcoming": upcoming_performances},
        "bookings": {"total": total_bookings, "confirmed": confirmed_bookings, "pending": pending_bookings},
        "users": {"total": total_users, "active": active_users},
        "revenue": {"total": float(total_revenue)}
    }


# =============================================
# RBAC - ROLE MANAGEMENT
# =============================================

class RoleCreate(BaseModel):
    role_name: str
    description: str | None = None
    can_manage_shows: bool = False
    can_manage_venues: bool = False
    can_manage_performances: bool = False
    can_manage_bookings: bool = False
    can_view_analytics: bool = False
    can_manage_users: bool = False
    can_manage_pricing: bool = False
    can_issue_refunds: bool = False


class RoleResponse(BaseModel):
    role_id: int
    role_name: str
    description: str | None
    can_manage_shows: bool
    can_manage_venues: bool
    can_manage_performances: bool
    can_manage_bookings: bool
    can_view_analytics: bool
    can_manage_users: bool
    can_manage_pricing: bool
    can_issue_refunds: bool

    class Config:
        from_attributes = True


@router.get("/roles")
def list_roles(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """List all roles (Admin only)"""
    roles = db.query(models.Role).all()
    return [
        {
            "role_id": r.role_id,
            "role_name": r.role_name,
            "description": r.description,
            "can_manage_shows": r.can_manage_shows,
            "can_manage_venues": r.can_manage_venues,
            "can_manage_performances": r.can_manage_performances,
            "can_manage_bookings": r.can_manage_bookings,
            "can_view_analytics": r.can_view_analytics,
            "can_manage_users": r.can_manage_users,
            "can_manage_pricing": r.can_manage_pricing,
            "can_issue_refunds": r.can_issue_refunds,
            "user_count": db.query(models.User).filter(models.User.role_id == r.role_id).count()
        }
        for r in roles
    ]


@router.post("/roles", status_code=status.HTTP_201_CREATED)
def create_role(
    role: RoleCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Create a new role (Admin only)"""
    existing = db.query(models.Role).filter(models.Role.role_name == role.role_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    new_role = models.Role(**role.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="CREATE_ROLE",
        entity_type="Role",
        entity_id=new_role.role_id,
        new_values=role.model_dump(),
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Role created successfully", "role_id": new_role.role_id}


@router.put("/roles/{role_id}")
def update_role(
    role_id: int,
    role: RoleCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update a role (Admin only)"""
    db_role = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    old_values = {"role_name": db_role.role_name}
    
    for key, value in role.model_dump().items():
        setattr(db_role, key, value)
    
    db.commit()
    db.refresh(db_role)
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="UPDATE_ROLE",
        entity_type="Role",
        entity_id=role_id,
        old_values=old_values,
        new_values=role.model_dump(),
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Role updated successfully"}


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Delete a role (Admin only) - only if no users assigned"""
    db_role = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    users_with_role = db.query(models.User).filter(models.User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete role - {users_with_role} users are assigned to this role"
        )
    
    role_name = db_role.role_name
    db.delete(db_role)
    db.commit()
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="DELETE_ROLE",
        entity_type="Role",
        entity_id=role_id,
        old_values={"role_name": role_name},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Role deleted successfully"}


# =============================================
# RBAC - USER MANAGEMENT
# =============================================

class UserUpdateAdmin(BaseModel):
    account_status: str | None = None
    is_admin: bool | None = None
    role_id: int | None = None


@router.get("/users")
def list_users(
    search: str | None = None,
    account_status: str | None = None,
    role_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """List all users with filtering options (Admin only)"""
    query = db.query(models.User)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.User.email.ilike(search_term),
                models.User.first_name.ilike(search_term),
                models.User.last_name.ilike(search_term)
            )
        )
    
    if account_status:
        query = query.filter(models.User.account_status == account_status)
    
    if role_id:
        query = query.filter(models.User.role_id == role_id)
    
    total = query.count()
    users = query.order_by(desc(models.User.created_at)).offset(offset).limit(limit).all()
    
    result = []
    for user in users:
        booking_count = db.query(models.Booking).filter(models.Booking.user_id == user.user_id).count()
        result.append({
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone,
            "account_status": user.account_status,
            "is_admin": user.is_admin,
            "role_id": user.role_id,
            "role_name": user.role.role_name if user.role else None,
            "registration_date": str(user.registration_date) if user.registration_date else None,
            "email_verified": user.email_verified,
            "booking_count": booking_count
        })
    
    return {"users": result, "total": total}


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get a specific user's details (Admin only)"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    booking_count = db.query(models.Booking).filter(models.Booking.user_id == user.user_id).count()
    
    # Get user's bookings
    bookings = db.query(models.Booking).filter(
        models.Booking.user_id == user_id
    ).order_by(desc(models.Booking.booking_date)).limit(10).all()
    
    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
        "address_line1": user.address_line1,
        "city": user.city,
        "country": user.country,
        "account_status": user.account_status,
        "is_admin": user.is_admin,
        "role_id": user.role_id,
        "role_name": user.role.role_name if user.role else None,
        "registration_date": str(user.registration_date) if user.registration_date else None,
        "email_verified": user.email_verified,
        "booking_count": booking_count,
        "recent_bookings": [
            {
                "booking_id": b.booking_id,
                "booking_reference": b.booking_reference,
                "booking_status": b.booking_status,
                "total_amount": float(b.total_amount),
                "booking_date": str(b.booking_date)
            }
            for b in bookings
        ]
    }


@router.put("/users/{user_id}")
def update_user_admin(
    user_id: int,
    update: UserUpdateAdmin,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Update a user's admin status, role, or account status (Admin only)"""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-demotion
    if user_id == admin.get("user_id") and update.is_admin == False:
        raise HTTPException(status_code=400, detail="Cannot remove your own admin status")
    
    old_values = {
        "account_status": user.account_status,
        "is_admin": user.is_admin,
        "role_id": user.role_id
    }
    
    if update.account_status is not None:
        if update.account_status not in ["Active", "Suspended", "Deactivated"]:
            raise HTTPException(status_code=400, detail="Invalid account status")
        user.account_status = update.account_status
    
    if update.is_admin is not None:
        user.is_admin = update.is_admin
    
    if update.role_id is not None:
        role = db.query(models.Role).filter(models.Role.role_id == update.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
        user.role_id = update.role_id
    
    db.commit()
    db.refresh(user)
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="UPDATE_USER",
        entity_type="User",
        entity_id=user_id,
        old_values=old_values,
        new_values=update.model_dump(exclude_none=True),
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "User updated successfully"}


# =============================================
# RBAC - BOOKING MANAGEMENT
# =============================================

@router.get("/bookings")
def list_all_bookings(
    search: str | None = None,
    booking_status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """List all bookings with filtering (Admin only)"""
    query = db.query(models.Booking).join(models.User).join(models.Performance).join(models.Show)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Booking.booking_reference.ilike(search_term),
                models.User.email.ilike(search_term),
                models.User.first_name.ilike(search_term),
                models.Show.title.ilike(search_term)
            )
        )
    
    if booking_status:
        query = query.filter(models.Booking.booking_status == booking_status)
    
    total = query.count()
    bookings = query.order_by(desc(models.Booking.booking_date)).offset(offset).limit(limit).all()
    
    result = []
    for booking in bookings:
        seat_count = db.query(models.BookingDetail).filter(
            models.BookingDetail.booking_id == booking.booking_id
        ).count()
        
        result.append({
            "booking_id": booking.booking_id,
            "booking_reference": booking.booking_reference,
            "user_id": booking.user_id,
            "user_name": f"{booking.user.first_name} {booking.user.last_name}",
            "user_email": booking.user.email,
            "performance_id": booking.performance_id,
            "show_title": booking.performance.show.title,
            "performance_date": str(booking.performance.performance_date),
            "total_amount": float(booking.total_amount),
            "booking_status": booking.booking_status,
            "booking_date": str(booking.booking_date),
            "seat_count": seat_count
        })
    
    return {"bookings": result, "total": total}


class AdminCancelRequest(BaseModel):
    reason: str


@router.post("/bookings/{booking_id}/cancel")
def admin_cancel_booking(
    booking_id: int,
    cancel: AdminCancelRequest,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Cancel a booking (Admin only)"""
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status == "Cancelled":
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    
    old_status = booking.booking_status
    booking.booking_status = "Cancelled"
    booking.cancellation_date = datetime.now()
    
    # Release seats
    seat_count = db.query(models.BookingDetail).filter(
        models.BookingDetail.booking_id == booking_id
    ).count()
    
    performance = booking.performance
    performance.available_seats += seat_count
    
    db.commit()
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="ADMIN_CANCEL_BOOKING",
        entity_type="Booking",
        entity_id=booking_id,
        old_values={"booking_status": old_status},
        new_values={"booking_status": "Cancelled", "reason": cancel.reason},
        ip_address=request.client.host if request.client else None
    )
    
    return {"message": "Booking cancelled successfully", "booking_reference": booking.booking_reference}


class RefundRequest(BaseModel):
    reason: str
    refund_amount: float | None = None


@router.post("/bookings/{booking_id}/refund")
def admin_issue_refund(
    booking_id: int,
    refund: RefundRequest,
    request: Request,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Issue a refund for a booking (Admin only)"""
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.booking_status not in ["Confirmed", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Can only refund confirmed or cancelled bookings")
    
    # Get original payment
    payment = db.query(models.Payment).filter(
        models.Payment.booking_id == booking_id,
        models.Payment.payment_status == "Completed"
    ).first()
    
    if not payment:
        raise HTTPException(status_code=400, detail="No completed payment found for this booking")
    
    refund_amount = refund.refund_amount if refund.refund_amount else float(booking.total_amount)
    
    if refund_amount > float(booking.total_amount):
        raise HTTPException(status_code=400, detail="Refund amount cannot exceed booking total")
    
    old_status = booking.booking_status
    booking.refund_amount = refund_amount
    booking.booking_status = "Refunded"
    
    payment.payment_status = "Refunded"
    payment.refund_date = datetime.now()
    payment.refund_transaction_id = f"REF-{booking.booking_reference}"
    
    db.commit()
    
    # Audit log
    log_audit_action(
        db=db,
        user_id=admin.get("user_id"),
        action="ISSUE_REFUND",
        entity_type="Booking",
        entity_id=booking_id,
        old_values={"booking_status": old_status},
        new_values={"booking_status": "Refunded", "refund_amount": refund_amount, "reason": refund.reason},
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "message": "Refund issued successfully",
        "booking_reference": booking.booking_reference,
        "refund_amount": refund_amount
    }


# =============================================
# AUDIT LOGS
# =============================================

def log_audit_action(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None
):
    """Create an audit log entry"""
    try:
        audit = models.AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit)
        db.commit()
        return audit
    except Exception as e:
        # Don't fail the main operation if audit logging fails
        print(f"Audit log error: {e}")
        return None


@router.get("/audit-logs")
def list_audit_logs(
    user_id: int | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """List audit logs with filtering (Admin only)"""
    query = db.query(models.AuditLog).join(models.User)
    
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    
    if action:
        query = query.filter(models.AuditLog.action == action)
    
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    
    total = query.count()
    logs = query.order_by(desc(models.AuditLog.timestamp)).offset(offset).limit(limit).all()
    
    result = []
    for log in logs:
        result.append({
            "log_id": log.log_id,
            "user_id": log.user_id,
            "user_name": f"{log.user.first_name} {log.user.last_name}",
            "user_email": log.user.email,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "timestamp": str(log.timestamp)
        })
    
    return {"logs": result, "total": total}


@router.get("/audit-logs/actions")
def list_audit_actions(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get list of unique audit actions for filtering"""
    actions = db.query(models.AuditLog.action).distinct().all()
    return [a[0] for a in actions]


@router.get("/audit-logs/entity-types")
def list_entity_types(
    db: Session = Depends(database.get_db),
    admin: dict = Depends(auth.verify_admin)
):
    """Get list of unique entity types for filtering"""
    types = db.query(models.AuditLog.entity_type).distinct().all()
    return [t[0] for t in types]
