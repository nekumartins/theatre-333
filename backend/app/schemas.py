from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal


# Genre Schemas
class GenreBase(BaseModel):
    genre_name: str
    description: Optional[str] = None

class GenreResponse(GenreBase):
    genre_id: int
    
    class Config:
        from_attributes = True


# User Schemas
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    city: Optional[str]
    account_status: str
    
    class Config:
        from_attributes = True


# Show Schemas
class ShowBase(BaseModel):
    title: str
    description: Optional[str] = None
    genre_id: int
    duration_minutes: int
    language: Optional[str] = None
    age_rating: Optional[str] = None
    poster_url: Optional[str] = None
    producer: Optional[str] = None
    director: Optional[str] = None

class ShowResponse(ShowBase):
    show_id: int
    show_status: str
    genre: Optional[GenreResponse] = None
    
    class Config:
        from_attributes = True


# Venue Schemas
class VenueResponse(BaseModel):
    venue_id: int
    venue_name: str
    city: str
    country: str
    total_capacity: int
    
    class Config:
        from_attributes = True


# Performance Schemas
class PerformanceResponse(BaseModel):
    performance_id: int
    show_id: int
    venue_id: int
    performance_date: date
    start_time: time
    total_seats: int
    available_seats: int
    performance_status: str
    show: Optional[ShowResponse] = None
    venue: Optional[VenueResponse] = None
    
    class Config:
        from_attributes = True


# Seat Schemas
class SeatResponse(BaseModel):
    seat_id: int
    row_number: str
    seat_number: str
    section: Optional[str]
    seat_category: str
    is_accessible: bool
    
    class Config:
        from_attributes = True


# Booking Schemas
class BookingCreate(BaseModel):
    user_id: int
    performance_id: int
    seat_ids: List[int]

class BookingDetailResponse(BaseModel):
    booking_detail_id: int
    seat_id: int
    seat_price: Decimal
    row_number: str
    seat_number: str
    seat_category: str
    
    class Config:
        from_attributes = True

class BookingResponse(BaseModel):
    booking_id: int
    booking_reference: str
    booking_date: datetime
    total_amount: Decimal
    booking_status: str
    performance: Optional[PerformanceResponse] = None
    booking_details: Optional[List[BookingDetailResponse]] = []
    
    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    booking_id: int
    payment_amount: Decimal
    payment_method: str
    card_last_four: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    payment_amount: Decimal
    payment_method: str
    payment_status: str
    payment_date: datetime
    transaction_id: Optional[str]
    
    class Config:
        from_attributes = True


# Token Schema
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
