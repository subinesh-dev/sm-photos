
from datetime import datetime, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import GuestAccess
from app.core.security import decode_access_token


guest_bearer = HTTPBearer(auto_error=False)


def get_current_guest(
    credentials: HTTPAuthorizationCredentials = Depends(guest_bearer),
    db: Session = Depends(get_db)
):

    credentials_error = HTTPException(
        status_code=401,
        detail="Invalid or expired guest session.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise credentials_error

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        if payload.get("type") != "guest":
            raise credentials_error

        if payload.get("sub") != "guest":
            raise credentials_error

        access_id = int(payload["guest_access_id"])
        event_id = int(payload["event_id"])

    except (JWTError, ValueError, TypeError, KeyError):
        raise credentials_error

    access = (
        db.query(GuestAccess)
        .filter(
            GuestAccess.id == access_id,
            GuestAccess.event_id == event_id,
            GuestAccess.is_active.is_(True)
        )
        .first()
    )

    if access is None:
        raise credentials_error

    if access.expires_at is not None:

        expiry = access.expires_at

        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)

        if expiry <= datetime.now(timezone.utc):
            raise credentials_error

    return access
