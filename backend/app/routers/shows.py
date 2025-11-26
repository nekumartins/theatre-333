from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from backend.app import models, schemas, database

router = APIRouter(prefix="/api/shows", tags=["Shows"])


@router.get("/")
def get_shows(
    genre: Optional[str] = None,
    status: str = "Active",
    db: Session = Depends(database.get_db)
):
    """Retrieve all shows, optionally filter by genre"""
    query = db.query(models.Show).filter(models.Show.show_status == status)
    
    if genre:
        query = query.join(models.Genre).filter(models.Genre.genre_name == genre)
    
    shows = query.all()
    return {"shows": shows, "count": len(shows)}


@router.get("/{show_id}")
def get_show_detail(show_id: int, db: Session = Depends(database.get_db)):
    """Get detailed information about a specific show"""
    show = db.query(models.Show).filter(models.Show.show_id == show_id).first()
    if not show:
        raise HTTPException(status_code=404, detail="Show not found")
    return show


@router.get("/genres/")
def get_genres(db: Session = Depends(database.get_db)):
    """Get all available genres"""
    genres = db.query(models.Genre).all()
    return {"genres": genres, "count": len(genres)}
