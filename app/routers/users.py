from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.auth import get_admin_user, hash_password
from app.database import get_session
from app.models import User, UserCreate, UserPublic, UserRole, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

SessionDep = Annotated[Session, Depends(get_session)]
AdminUser = Annotated[User, Depends(get_admin_user)]


@router.get("/", response_model=list[UserPublic])
def list_users(
    session: SessionDep,
    admin: AdminUser,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
):
    return session.exec(select(User).offset(skip).limit(limit)).all()


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int, session: SessionDep, admin: AdminUser):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserPublic, status_code=201)
def create_user(
    payload: UserCreate, role: UserRole, session: SessionDep, admin: AdminUser
):
    existing = session.exec(
        select(User).where(
            (User.email == payload.email) | (User.username == payload.username)
        )
    ).first()
    if existing:
        raise HTTPException(
            status_code=409, detail="Email or username already registered"
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int, payload: UserUpdate, session: SessionDep, admin: AdminUser
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = payload.model_dump(exclude_unset=True)
    user.sqlmodel_update(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: SessionDep, admin: AdminUser):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
