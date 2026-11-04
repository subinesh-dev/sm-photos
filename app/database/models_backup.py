from sqlalchemy import (
    Column, Integer, String, DateTime,
    ForeignKey, Float
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.db import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    photos = relationship("Photo", back_populates="event")


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)

    event_id = Column(Integer, ForeignKey("events.id"))

    event = relationship("Event", back_populates="photos")
    faces = relationship("Face", back_populates="photo")


class Face(Base):
    __tablename__ = "faces"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"))

    confidence = Column(Float)
    embedding_path = Column(String)

    photo = relationship("Photo", back_populates="faces")