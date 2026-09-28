from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
    UserSignupRequest,
)
from app.services.auth_service import authenticate_user, create_user_token, signup_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    signup_data: UserSignupRequest,
    db: Session = Depends(get_db),
):
    user = signup_user(db, signup_data)
    token = create_user_token(user)
    return AuthResponse(
        user=UserResponse.model_validate(user),
        token=token,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            login_data = UserLoginRequest(**body)
            email = str(login_data.email)
            password = login_data.password
        except (ValidationError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid login data",
            )
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")
        if not email or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email and password required",
            )

    user = authenticate_user(db, str(email), str(password))
    return create_user_token(user)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
