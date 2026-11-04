
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    events = relationship("Event", back_populates="owner")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String, nullable=False)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    owner = relationship("User", back_populates="events")
    photos = relationship("Photo", back_populates="event")
    guest_accesses = relationship(
        "GuestAccess",
        back_populates="event",
        cascade="all, delete-orphan"
    )


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


class GuestAccess(Base):
    __tablename__ = "guest_access"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(
        Integer,
        ForeignKey("events.id"),
        nullable=False,
        index=True
    )

    token_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=True
    )

    event = relationship(
        "Event",
        back_populates="guest_accesses"
    )
