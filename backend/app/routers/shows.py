from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app import models, schemas, database

router = APIRouter(prefix="/api/shows", tags=["Shows"])


@router.get("/")
def get_shows(
    genre: Optional[str] = None,
    status: str = "Active",
    db: Session = Depends(database.get_db)
):
    """Retrieve all shows, optionally filter by genre"""
    query = db.query(models.Show).options(joinedload(models.Show.genre)).filter(models.Show.show_status == status)
    
    if genre:
        query = query.join(models.Genre).filter(models.Genre.genre_name == genre)
    
    shows = query.all()
    
    # Add genre_name to each show
    shows_data = []
    for show in shows:
        show_dict = {
            "show_id": show.show_id,
            "title": show.title,
            "description": show.description,
            "genre_id": show.genre_id,
            "genre_name": show.genre.genre_name if show.genre else None,
            "duration_minutes": show.duration_minutes,
            "language": show.language,
            "age_rating": show.age_rating,
            "poster_url": show.poster_url,
            "producer": show.producer,
            "director": show.director,
            "show_status": show.show_status,
            "created_at": show.created_at,
            "updated_at": show.updated_at
        }
        shows_data.append(show_dict)
    
    return {"shows": shows_data, "count": len(shows_data)}


@router.get("/{show_id}")
def get_show_detail(show_id: int, db: Session = Depends(database.get_db)):
    """Get detailed information about a specific show"""
    show = db.query(models.Show).options(joinedload(models.Show.genre)).filter(models.Show.show_id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    
    show_dict = {
        "show_id": show.show_id,
        "title": show.title,
        "description": show.description,
        "genre_id": show.genre_id,
        "genre_name": show.genre.genre_name if show.genre else None,
        "duration_minutes": show.duration_minutes,
        "language": show.language,
        "age_rating": show.age_rating,
        "poster_url": show.poster_url,
        "producer": show.producer,
        "director": show.director,
        "show_status": show.show_status,
        "created_at": show.created_at,
        "updated_at": show.updated_at
    }
    return show_dict


@router.get("/genres/")
def get_genres(db: Session = Depends(database.get_db)):
    """Get all available genres"""
    genres = db.query(models.Genre).all()
    return {"genres": genres, "count": len(genres)}


@router.get("/venues/")
def get_venues(db: Session = Depends(database.get_db)):
    """Get all available venues for filtering"""
    venues = db.query(models.Venue).all()
    venues_data = []
    for venue in venues:
        venues_data.append({
            "venue_id": venue.venue_id,
            "venue_name": venue.venue_name,
            "city": venue.city,
            "capacity": venue.total_capacity
        })
    return {"venues": venues_data, "count": len(venues_data)}
