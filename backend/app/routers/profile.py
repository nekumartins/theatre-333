from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from backend.app import models, schemas, database, auth

router = APIRouter(prefix="/api/profile", tags=["Profile"])


@router.get("/me")
def get_profile(current_user: dict = Depends(auth.get_current_user_from_token), db: Session = Depends(database.get_db)):
    """Get current user's profile"""
    user = db.query(models.User).filter(models.User.email == current_user.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "date_of_birth": user.date_of_birth,
        "address_line1": user.address_line1,
        "address_line2": user.address_line2,
        "city": user.city,
        "postal_code": user.postal_code,
        "country": user.country,
        "registration_date": user.registration_date,
        "email_verified": user.email_verified,
        "account_status": user.account_status
    }


@router.put("/update")
def update_profile(profile_data: dict, current_user: dict = Depends(auth.get_current_user_from_token), db: Session = Depends(database.get_db)):
    """Update user profile"""
    user = db.query(models.User).filter(models.User.email == current_user.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update allowed fields
    allowed_fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 
                     'address_line1', 'address_line2', 'city', 'postal_code', 'country']
    
    for field in allowed_fields:
        if field in profile_data:
            setattr(user, field, profile_data[field])
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Profile updated successfully", "user_id": user.user_id}
