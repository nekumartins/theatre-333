import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, database

router = APIRouter(prefix="/api/verification", tags=["Email Verification"])

# Store verification tokens (in production, use Redis or database)
verification_tokens = {}


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


from pydantic import BaseModel

class EmailRequest(BaseModel):
    email: str

@router.post("/send-verification")
def send_verification_email(request: EmailRequest, db: Session = Depends(database.get_db)):
    """Send verification email to user"""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate token
    token = generate_verification_token()
    verification_tokens[token] = {
        "email": request.email,
        "expires": datetime.now() + timedelta(hours=24)
    }
    
    # In production, send actual email with link: f"{BASE_URL}/verify?token={token}"
    # For now, return token for testing
    verification_link = f"http://localhost:8000/verify?token={token}"
    
    return {
        "message": "Verification email sent successfully",
        "verification_link": verification_link,  # Remove in production
        "token": token  # Remove in production
    }


@router.post("/verify/{token}")
def verify_email(token: str, db: Session = Depends(database.get_db)):
    """Verify user email with token"""
    if token not in verification_tokens:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    token_data = verification_tokens[token]
    
    # Check if token expired
    if datetime.now() > token_data["expires"]:
        del verification_tokens[token]
        raise HTTPException(status_code=400, detail="Verification token has expired")
    
    # Get user
    user = db.query(models.User).filter(models.User.email == token_data["email"]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update user
    user.email_verified = True
    if user.account_status == "Active":
        user.account_status = "Active"  # Could have special "Verified" status
    
    db.commit()
    
    # Remove token
    del verification_tokens[token]
    
    return {
        "message": "Email verified successfully",
        "email": user.email,
        "email_verified": True
    }


@router.get("/status/{email}")
def get_verification_status(email: str, db: Session = Depends(database.get_db)):
    """Check if user's email is verified"""
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "email": user.email,
        "email_verified": user.email_verified,
        "account_status": user.account_status
    }


@router.post("/resend")
def resend_verification(request: EmailRequest, db: Session = Depends(database.get_db)):
    """Resend verification email"""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.email_verified:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Remove old token if exists
    tokens_to_remove = [t for t, data in verification_tokens.items() if data["email"] == request.email]
    for t in tokens_to_remove:
        del verification_tokens[t]
    
    # Generate new token
    token = generate_verification_token()
    verification_tokens[token] = {
        "email": request.email,
        "expires": datetime.now() + timedelta(hours=24)
    }
    
    verification_link = f"http://localhost:8000/verify?token={token}"
    
    return {
        "message": "Verification email resent successfully",
        "verification_link": verification_link,
        "token": token
    }
