from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.routers import users, shows, performances, bookings, payments, profile, admin
from app.database import get_db, engine
from app import models

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

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="../frontend/templates")

# Include routers
app.include_router(users.router)
app.include_router(shows.router)
app.include_router(performances.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(profile.router)
app.include_router(admin.router)


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
    """Seat selection page"""
    return templates.TemplateResponse("seat_selection.html", {"request": request, "performance_id": performance_id})


@app.get("/booking/{booking_id}/payment", response_class=HTMLResponse)
async def payment_page(request: Request, booking_id: int):
    """Payment page"""
    return templates.TemplateResponse("payment.html", {"request": request, "booking_id": booking_id})


@app.get("/my-bookings", response_class=HTMLResponse)
async def my_bookings_page(request: Request):
    """User bookings page"""
    return templates.TemplateResponse("my_bookings.html", {"request": request})


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
    """User profile page"""
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """Admin panel page"""
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Theatre Booking System API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
