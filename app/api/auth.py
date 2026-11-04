
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User, Event
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.dependencies.auth import get_current_admin


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    password: str = Field(min_length=12, max_length=128)


@router.post("/register")
def register_first_admin(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    if (
        "@" not in email
        or email.startswith("@")
        or email.endswith("@")
        or "." not in email.split("@")[-1]
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address."
        )

    # Only the first admin can register publicly.
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=403,
            detail=(
                "Admin registration is closed. "
                "An administrator account already exists."
            )
        )

    existing = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Email address is already registered."
        )

    admin = User(
        email=email,
        password_hash=hash_password(data.password),
        is_active=True
    )

    try:
        db.add(admin)
        db.flush()

        # Claim only currently unassigned legacy events.
        db.query(Event).filter(
            Event.owner_id.is_(None)
        ).update(
            {Event.owner_id: admin.id},
            synchronize_session=False
        )

        db.commit()
        db.refresh(admin)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create administrator account."
        )

    token = create_access_token(admin.id)

    return {
        "status": "success",
        "message": "First administrator created successfully.",
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "email": admin.email
        }
    }


@router.post("/login")
def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.strip().lower()

    admin = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    # Use the same response for unknown email and wrong password.
    if (
        admin is None
        or not admin.is_active
        or not verify_password(
            form_data.password,
            admin.password_hash
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(admin.id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "email": admin.email
        }
    }


@router.get("/me")
def get_admin_profile(
    current_admin: User = Depends(get_current_admin)
):
    return {
        "id": current_admin.id,
        "email": current_admin.email,
        "is_active": current_admin.is_active,
        "created_at": str(current_admin.created_at)
    }
