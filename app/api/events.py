
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.db import get_db
from app.database.models import Event, Photo, Face, User
from app.dependencies.auth import get_current_admin


router = APIRouter(
    prefix="/api/events",
    tags=["Event Management"]
)


def get_owned_event(
    db: Session,
    event_id: int,
    admin_id: int
):
    event = (
        db.query(Event)
        .filter(
            Event.id == event_id,
            Event.owner_id == admin_id
        )
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Event not found."
        )

    return event


def event_summary(db: Session, event: Event):

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

    return {
        "id": event.id,
        "event_name": event.event_name,
        "created_at": str(event.created_at),
        "total_photos": photo_count,
        "total_faces": face_count
    }


# --------------------------------------------------
# CREATE EVENT - ADMIN ONLY
# --------------------------------------------------

@router.post("/")
def create_event(
    event_name: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

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

    existing_event = (
        db.query(Event)
        .filter(
            Event.event_name == event_name,
            Event.owner_id == current_admin.id
        )
        .first()
    )

    if existing_event:
        raise HTTPException(
            status_code=409,
            detail="You already have an event with this name."
        )

    event = Event(
        event_name=event_name,
        owner_id=current_admin.id
    )

    try:
        db.add(event)
        db.commit()
        db.refresh(event)

        return {
            "status": "success",
            "message": "Event created successfully.",
            "event": event_summary(db, event)
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create event."
        )


# --------------------------------------------------
# LIST CURRENT ADMIN'S EVENTS
# --------------------------------------------------

@router.get("/")
def get_all_events(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    events = (
        db.query(Event)
        .filter(Event.owner_id == current_admin.id)
        .order_by(Event.id.desc())
        .all()
    )

    return {
        "total_events": len(events),
        "events": [
            event_summary(db, event)
            for event in events
        ]
    }


# --------------------------------------------------
# GET OWNED EVENT DETAILS
# --------------------------------------------------

@router.get("/{event_id}")
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):

    event = get_owned_event(
        db,
        event_id,
        current_admin.id
    )

    return event_summary(db, event)
