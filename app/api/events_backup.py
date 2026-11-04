from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.db import SessionLocal
from app.database.models import Event, Photo, Face


router = APIRouter(
    prefix="/api/events",
    tags=["Event Management"]
)


# --------------------------------------------------
# 1. CREATE EVENT
# --------------------------------------------------

@router.post("/")
def create_event(event_name: str):

    event_name = event_name.strip()

    if not event_name:
        raise HTTPException(
            status_code=400,
            detail="Event name cannot be empty."
        )

    if len(event_name) > 150:
        raise HTTPException(
            status_code=400,
            detail="Event name cannot exceed 150 characters."
        )

    db: Session = SessionLocal()

    try:

        existing_event = (
            db.query(Event)
            .filter(Event.event_name == event_name)
            .first()
        )

        if existing_event:
            raise HTTPException(
                status_code=409,
                detail="An event with this name already exists."
            )

        event = Event(
            event_name=event_name
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return {
            "status": "success",
            "message": "Event created successfully.",
            "event": {
                "id": event.id,
                "event_name": event.event_name,
                "created_at": str(event.created_at)
            }
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# --------------------------------------------------
# 2. GET ALL EVENTS
# --------------------------------------------------

@router.get("/")
def get_all_events():

    db: Session = SessionLocal()

    try:

        events = (
            db.query(Event)
            .order_by(Event.id.desc())
            .all()
        )

        results = []

        for event in events:

            photo_count = (
                db.query(func.count(Photo.id))
                .filter(Photo.event_id == event.id)
                .scalar()
            )

            face_count = (
                db.query(func.count(Face.id))
                .join(Photo, Face.photo_id == Photo.id)
                .filter(Photo.event_id == event.id)
                .scalar()
            )

            results.append({
                "id": event.id,
                "event_name": event.event_name,
                "created_at": str(event.created_at),
                "total_photos": photo_count,
                "total_faces": face_count
            })

        return {
            "total_events": len(results),
            "events": results
        }

    finally:
        db.close()


# --------------------------------------------------
# 3. GET EVENT DETAILS
# --------------------------------------------------

@router.get("/{event_id}")
def get_event(event_id: int):

    db: Session = SessionLocal()

    try:

        event = (
            db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Event not found."
            )

        photo_count = (
            db.query(func.count(Photo.id))
            .filter(Photo.event_id == event_id)
            .scalar()
        )

        face_count = (
            db.query(func.count(Face.id))
            .join(Photo, Face.photo_id == Photo.id)
            .filter(Photo.event_id == event_id)
            .scalar()
        )

        return {
            "id": event.id,
            "event_name": event.event_name,
            "created_at": str(event.created_at),
            "total_photos": photo_count,
            "total_faces": face_count
        }

    finally:
        db.close()