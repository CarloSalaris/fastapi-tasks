from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.models import User, UserCreate, UserPublic, UserRole

router = APIRouter(prefix="/auth", tags=["auth"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.post("/register", response_model=UserPublic, status_code=201)
def register(payload: UserCreate, session: SessionDep):
    existing = session.exec(
        select(User).where(
            (User.email == payload.email) | (User.username == payload.username)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="Email or username already registered"
        )

    # First user becomes admin
    is_first_user = session.exec(select(User)).first() is None

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=UserRole.admin if is_first_user else UserRole.user,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}
