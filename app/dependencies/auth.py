
from jose import JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")

        if not subject:
            raise credentials_error

        user_id = int(subject)

    except (JWTError, ValueError, TypeError):
        raise credentials_error

    admin = (
        db.query(User)
        .filter(
            User.id == user_id,
            User.is_active.is_(True)
        )
        .first()
    )

    if admin is None:
        raise credentials_error

    return admin
