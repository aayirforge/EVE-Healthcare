from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserSignupRequest


def signup_user(db: Session, signup_data: UserSignupRequest) -> User:
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        logger.warning(f"Signup failed: email {signup_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(signup_data.password)
    user = User(
        email=signup_data.email,
        hashed_password=hashed_password,
        full_name=signup_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"User signed up: id={user.id}, email={user.email}")
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_user_token(user: User) -> TokenResponse:
    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token, token_type="bearer")
