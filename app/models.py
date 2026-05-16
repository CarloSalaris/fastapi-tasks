from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel

""" TASKS """


class TaskBase(SQLModel):
    title: str
    description: str | None = None
    completed: bool = False


class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
    user_id: int = Field(foreign_key="user.id")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskPublic(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime | None


""" USERS """


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.user)


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserUpdate(SQLModel):
    email: str | None = None
    username: str | None = None
    role: UserRole | None = None


class UserPublic(UserBase):
    id: int
    role: UserRole
