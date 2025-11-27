from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import secrets
from app import models, schemas, database, auth

router = APIRouter(prefix="/api/users", tags=["Users"])

# In-memory storage for password reset tokens (in production, use database or Redis)
password_reset_tokens = {}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user"""
    # Check if email exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = auth.get_password_hash(user.password)
    
    # Create user
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone=user.phone,
        password_hash=hashed_password,
        city=user.city,
        country=user.country,
        registration_date=date.today()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.user_id}


@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """User login and JWT token generation"""
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    
    if not user or not auth.verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = auth.create_access_token(data={
        "sub": user.email, 
        "user_id": user.user_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin if hasattr(user, 'is_admin') else False
    })
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin if hasattr(user, 'is_admin') else False
    }


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user(token: str, db: Session = Depends(database.get_db)):
    """Get current user information"""
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/forgot-password")
def forgot_password(email_data: dict, db: Session = Depends(database.get_db)):
    """Request password reset - sends reset link to email (Business requirement 2.1)"""
    email = email_data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # Always return success to prevent email enumeration attacks
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        password_reset_tokens[reset_token] = {
            "user_id": user.user_id,
            "email": email,
            "expires": datetime.now() + timedelta(hours=1)
        }
        
        # In production, send email with reset link
        # For demo, we'll just return success
        print(f"Password reset token for {email}: {reset_token}")
    
    return {
        "message": "If the email exists in our system, a password reset link has been sent.",
        "status": "success"
    }


@router.post("/reset-password")
def reset_password(reset_data: dict, db: Session = Depends(database.get_db)):
    """Reset password using token (Business requirement 2.1)"""
    token = reset_data.get("token")
    new_password = reset_data.get("new_password")
    
    if not token or not new_password:
        raise HTTPException(status_code=400, detail="Token and new password are required")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Validate token
    token_data = password_reset_tokens.get(token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    if datetime.now() > token_data["expires"]:
        del password_reset_tokens[token]
        raise HTTPException(status_code=400, detail="Reset token has expired")
    
    # Update password
    user = db.query(models.User).filter(models.User.user_id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password_hash = auth.get_password_hash(new_password)
    db.commit()
    
    # Remove used token
    del password_reset_tokens[token]
    
    return {
        "message": "Password has been reset successfully",
        "status": "success"
    }
