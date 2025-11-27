from fastapi import FastAPI, Request, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pathlib import Path
from typing import Optional
from app.routers import users, shows, performances, bookings, payments, profile, admin, verification, analytics
from app.database import get_db, engine
from app import models, auth

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Theatre Booking System",
    description="Online theatre booking platform API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(users.router)
app.include_router(shows.router)
app.include_router(performances.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(profile.router)
app.include_router(admin.router)
app.include_router(verification.router)
app.include_router(analytics.router)


# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/shows", response_class=HTMLResponse)
async def shows_page(request: Request):
    """Shows listing page"""
    return templates.TemplateResponse("shows.html", {"request": request})


@app.get("/shows/{show_id}", response_class=HTMLResponse)
async def show_detail_page(request: Request, show_id: int):
    """Show detail page"""
    return templates.TemplateResponse("show_detail.html", {"request": request, "show_id": show_id})


@app.get("/performance/{performance_id}/seats", response_class=HTMLResponse)
async def seat_selection_page(request: Request, performance_id: int):
    """Seat selection page (requires login)"""
    # Check if user is logged in via localStorage (JavaScript handles this)
    # API endpoints are protected, this is just the page
    return templates.TemplateResponse("seat_selection.html", {"request": request, "performance_id": performance_id})


@app.get("/booking/{booking_id}/payment", response_class=HTMLResponse)
async def payment_page(request: Request, booking_id: int):
    """Payment page (requires login)"""
    # Check if user is logged in via localStorage (JavaScript handles this)
    # API endpoints are protected, this is just the page
    return templates.TemplateResponse("payment_new.html", {"request": request, "booking_id": booking_id})


@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings_page(request: Request):
    """User bookings page (requires login)"""
    # Check if user is logged in via localStorage (JavaScript handles this)
    # API endpoints are protected, this is just the page
    return templates.TemplateResponse("my_bookings_enhanced.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page (requires login)"""
    # Check if user is logged in via localStorage (JavaScript handles this)
    # API endpoints are protected, this is just the page
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin panel page (requires admin login)"""
    # Check if user is logged in and is admin via localStorage (JavaScript handles this)
    # API endpoints are protected, this is just the page
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/booking/confirmation", response_class=HTMLResponse)
async def booking_confirmation_page(request: Request):
    """Booking confirmation page"""
    return templates.TemplateResponse("booking_confirmation.html", {"request": request})


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    """Forgot password page"""
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    """Reset password page"""
    return templates.TemplateResponse("reset_password.html", {"request": request})


@app.get("/booking/{booking_id}/ticket", response_class=HTMLResponse)
async def ticket_page(request: Request, booking_id: int):
    """E-Ticket page (requires login and confirmed booking)"""
    return templates.TemplateResponse("ticket.html", {"request": request, "booking_id": booking_id})


@app.get("/show/{show_id}", response_class=HTMLResponse)
async def show_detail_alt_page(request: Request, show_id: int):
    """Show detail page (alternate URL)"""
    return templates.TemplateResponse("show_detail.html", {"request": request, "show_id": show_id})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Theatre Booking System API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
