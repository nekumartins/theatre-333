from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from app import models, schemas, database, auth

router = APIRouter(prefix="/api/users", tags=["Users"])


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
        "last_name": user.last_name
    })
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "first_name": user.first_name,
        "last_name": user.last_name
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
